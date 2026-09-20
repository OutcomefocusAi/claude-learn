#!/usr/bin/env python3
"""UserPromptSubmit hook: Detect learning signals in user messages.

Mechanically detects corrections, positive reinforcement, and frustration.
Writes signals to ~/.claude/.learning-signals.jsonl.
Outputs reminder if signals accumulate without playbook updates.

The checkpoint counts ONLY genuine corrections the user typed. Everything
else still gets logged -- outcome-tracker rows, positives, injected prompts --
because the log is the corpus. But a build that passed is not a correction,
and nagging about 28,000 of them trains the reader to ignore the banner.

Must complete in <100ms. Must always exit 0.
"""

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

SIGNAL_FILE = Path.home() / ".claude" / ".learning-signals.jsonl"

# Whichever of these is newest marks "the playbook was last updated". The
# original named a single file, ~/.claude/rules/playbook.md, that has never
# existed on this machine -- so its mtime read as 0, every signal ever written
# counted as pending, and the banner could not go down no matter what was
# processed. Resolve against the files that are actually there, plus an ack
# file so a processing pass can clear the count without touching a playbook.
PLAYBOOK_FILES = (
    Path.home() / ".claude" / "playbook" / "playbook-full.md",
    Path.home() / ".claude" / "rules" / "playbook-distilled.md",
    Path.home() / ".claude" / "rules" / "playbook.md",
)
ACK_FILE = Path.home() / ".claude" / ".learning-signals-acked"

# Only these count toward the checkpoint. "outcome"-sourced rows are written by
# the PostToolUse tracker (retry_pattern, build_pass, edit_churn); they are
# telemetry about tool use, not something the user corrected.
COUNTED_SOURCES = frozenset({"user_language"})
COUNTED_TYPES = frozenset({"correction", "frustration"})

# The banner is a nag, not a metric -- stop counting once it is already loud.
COUNT_CEILING = 200
# Bound the read: the signal log is append-only and already megabytes. Only the
# tail can contain anything newer than the marker.
TAIL_BYTES = 512 * 1024

# Prompts the user did not type. Live-meeting coaching injections and replayed
# system text arrive through UserPromptSubmit like anything else, and they are
# full of the words the correction patterns look for.
INJECTED_MARKERS = (
    "you are coaching",
    "meta_model",
    "<system-reminder",
    "<task-notification",
    "# identity\n",
    "clean_language",
    "[learning signal:",
    "[learning checkpoint:",
    "session-start hook",
    "<cross-session-message",
)
MAX_HUMAN_PROMPT_CHARS = 2000

# ── Detection patterns ─────────────────────────────────────────────────────

CORRECTION_PATTERNS = [
    # "No," or "No!" reverses something. Bare "No more reviews, fixes" and
    # "no." opened work orders, which assign work rather than correct it.
    r"(?:^|[.!?]\s+)no[,!]",
    r"\bnot that\b",
    # Asserting the work is wrong, not asking what is wrong with something.
    # Bare \bwrong\b matched "what's wrong with the build?", which is a question.
    r"\b(?:that'?s|thats|this is|it'?s|its|you'?re|youre)\s+(?:the\s+)?wrong\b",
    r"\bwrong\s+(?:one|way|file|approach|thing|place|answer|order|direction)\b",
    # Imperative "don't" pointing AT SOMETHING ALREADY HAPPENING: "don't do
    # that", "do not do it that way". A constraint naming its object instead --
    # "Do not deploy", "Do not modify code", "Do not delete anything else" --
    # is a scope limit inside a brief, which is an instruction, not a
    # correction. Forty-five of fifty-three signals in one batch were those.
    r"(?:^|[.!?]\s+)(?:don'?t|do not)\s+(?:do\s+)?(?:that|this|it|again)\b",
    r"\bstop\s+(doing|that|it)\b",
    r"\bi said\b",
    r"\bi told you\b",
    r"\bi already (?:said|told|asked|mentioned)\b",  # "I already told" not "I already have"
    r"\bthat'?s not\b",
    r"\binstead of (?:doing|using|that)\b",  # Directed correction, not general "instead of X try Y"
    r"\byou should have\b",
    r"\bwhy did you\b",
    r"\bnot what i\b",
    r"\bthat was wrong\b",
    r"\bthe other (?:one|way|approach|thing)\b",  # Specific correction, not "the other package"
    # Sentence-opening "Actually, ..." reverses a direction. Mid-sentence
    # "it's actually fine" does not.
    r"(?:^|[.!?]\s+)actually[,\s]",
    # "Correction to the PR #47 fix: ..." is a correction wearing a brief's
    # clothes, and it is the one shape that must survive the work-order
    # exclusion below.
    r"^correction\b|^\W{0,3}correction to\b",
]

POSITIVE_PATTERNS = [
    r"\bperfect\b",
    r"\bexactly\b",
    r"\bnailed it\b",
    r"\bthat'?s it\b",
    r"\bgreat\b(?!.*\bbut\b)",
    r"\bnice\b(?!.*\bbut\b)",
    r"\blove it\b",
    r"\byes!",
    r"\bawesome\b",
    r"\bbeautiful\b",
    r"\bbrilliant\b",
]

FRUSTRATION_PATTERNS = [
    r"\bagain\?",
    r"\bhow many times\b",
    r"\bi already told\b",
    r"\bwhy do you keep\b",
    r"\bstop doing\b",
    r"\bwasting\b",
    r"\byou keep\b",
    r"\bsame mistake\b",
    r"\bi just said\b",
]


#: Section headings in the scoped briefs this user writes. Two or more of them
#: at the start of a line means the message assigns work.
BRIEF_SECTIONS = (
    "identity", "task", "context", "constraints", "verification",
    "output format", "required discovery", "scope", "deliverable",
    "context boundary check", "required design", "required tests",
)


#: A negation that opens a short message is feedback on the work in hand.
#: Beyond this, it is a constraint inside something longer that assigns work.
SHORT_ENOUGH_TO_BE_FEEDBACK = 200


def leading_imperative_negation(message: str) -> bool:
    """True for "Don't use the cache here" and false for a brief's constraints.

    The discriminator is where the negation sits, not what it forbids. Feedback
    leads with it and then stops; a work order describes a situation or assigns
    a task first and constrains it afterwards.
    """
    if len(message.strip()) > SHORT_ENOUGH_TO_BE_FEEDBACK:
        return False
    # The negation has to OPEN the message, after at most a short lead-in.
    # "I don't need this file" and "we don't have a staging environment" are
    # statements about the world; "Don't use the cache here" is an order about
    # the work in hand, and only the second one is feedback.
    opener = r"^[\W]*(?:ok|okay|no|please|hey|and|but)?[,\s]*(?:don'?t|do not)\s+\w+"
    return bool(re.match(opener, message.strip(), re.I))


def announces_a_correction(message: str) -> bool:
    """True when the message says outright that it is correcting something.

    A correction is allowed to be long and structured. This is the escape
    hatch that keeps `is_a_work_order` from swallowing one.
    """
    return bool(re.match(r"\s*\W{0,3}correction\b", message, re.I))


def is_a_work_order(message: str) -> bool:
    """True when the message assigns work rather than correcting work done.

    The user writes scoped briefs with headed sections and constraint lists,
    and those are full of the words a correction uses. An instruction is not
    feedback: counting it as one buried eight real corrections under
    forty-five work orders and trained the reader to ignore the banner.
    """
    lines = [line.strip().lower().lstrip("#*- ").rstrip(":*") for line in message.splitlines()]
    found = {line for line in lines if line in BRIEF_SECTIONS}
    return len(found) >= 2


def is_injected(message: str) -> bool:
    """True if this prompt was generated for the user rather than typed by them.

    Coaching injections and replayed system text reach UserPromptSubmit exactly
    like a typed message, and they contain the very words the correction
    patterns look for -- the newest row in the log when this was written was a
    live-meeting META_MODEL prompt filed as a high-severity correction.
    """
    lowered = message.lower()
    if any(marker in lowered for marker in INJECTED_MARKERS):
        return True
    return len(message) > MAX_HUMAN_PROMPT_CHARS


def detect_signal(message: str) -> dict | None:
    """Detect learning signals in user message."""
    message = message.replace("\r\n", "\n")
    msg_lower = message.lower().strip()

    if len(msg_lower) < 5 or msg_lower.startswith("/"):
        return None
    if is_injected(message):
        return None
    if is_a_work_order(message) and not announces_a_correction(message):
        return None

    for pattern in FRUSTRATION_PATTERNS:
        if re.search(pattern, msg_lower):
            return {"type": "frustration", "severity": "high", "message_preview": message[:120]}

    for pattern in CORRECTION_PATTERNS:
        if re.search(pattern, msg_lower):
            return {"type": "correction", "severity": "high", "message_preview": message[:120]}

    if leading_imperative_negation(message):
        return {"type": "correction", "severity": "high", "message_preview": message[:120]}

    for pattern in POSITIVE_PATTERNS:
        if re.search(pattern, msg_lower):
            return {"type": "positive", "severity": "normal", "message_preview": message[:120]}

    return None


def last_processed_at() -> float:
    """Epoch seconds of the most recent playbook update or explicit ack."""
    newest = 0.0
    for path in (*PLAYBOOK_FILES, ACK_FILE):
        try:
            newest = max(newest, path.stat().st_mtime)
        except OSError:
            continue
    return newest


def tail_lines(path: Path, max_bytes: int) -> list[str]:
    """Last whole lines of a file, reading at most max_bytes from the end.

    The signal log is append-only and already megabytes; reading all of it on
    every prompt is what pushed this hook past its 100ms budget. Anything
    newer than the marker is necessarily at the end.
    """
    try:
        size = path.stat().st_size
        with path.open("rb") as handle:
            if size > max_bytes:
                handle.seek(size - max_bytes)
                handle.readline()  # discard the partial line we landed in
            blob = handle.read()
    except OSError:
        return []
    return blob.decode("utf-8", errors="replace").splitlines()


def count_pending_signals() -> int:
    """Count genuine user corrections recorded since the playbook was updated."""
    if not SIGNAL_FILE.exists():
        return 0

    marker = last_processed_at()
    count = 0
    for line in tail_lines(SIGNAL_FILE, TAIL_BYTES):
        if not line.strip():
            continue
        try:
            entry = json.loads(line)
        except (json.JSONDecodeError, ValueError):
            continue
        if entry.get("source") not in COUNTED_SOURCES:
            continue
        if entry.get("type") not in COUNTED_TYPES:
            continue
        try:
            ts = datetime.fromisoformat(entry.get("timestamp", "")).timestamp()
        except (TypeError, ValueError):
            continue
        if ts <= marker:
            continue
        count += 1
        if count >= COUNT_CEILING:
            break
    return count


def main():
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            sys.exit(0)

        data = json.loads(raw)

        message = ""
        for field in ("prompt", "message", "content", "text", "user_message"):
            val = data.get(field, "")
            if val and isinstance(val, str):
                message = val
                break

        if not message:
            pending = count_pending_signals()
            if pending >= 3:
                print(f"[Learning checkpoint: {pending} unprocessed corrections — update playbook before continuing]")
            sys.exit(0)

        signal = detect_signal(message)

        if signal:
            signal["timestamp"] = datetime.now(timezone.utc).isoformat()
            signal["source"] = "user_language"
            SIGNAL_FILE.parent.mkdir(parents=True, exist_ok=True)

            with open(SIGNAL_FILE, "a", encoding="utf-8") as f:
                f.write(json.dumps(signal) + "\n")

            if signal["severity"] == "high":
                print(f"[Learning signal: {signal['type']} detected — capture this in playbook]")

        pending = count_pending_signals()
        if pending >= 3:
            print(f"[Learning checkpoint: {pending} unprocessed corrections — update playbook NOW]")

    except Exception:
        pass

    sys.exit(0)


if __name__ == "__main__":
    main()
