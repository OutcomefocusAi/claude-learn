#!/usr/bin/env python3
"""UserPromptSubmit hook: Detect learning signals in user messages.

Mechanically detects corrections, positive reinforcement, and frustration.
Writes signals to ~/.claude/.learning-signals.jsonl.
Outputs reminder if signals accumulate without playbook updates.

Must complete in <100ms. Must always exit 0.
"""

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

SIGNAL_FILE = Path.home() / ".claude" / ".learning-signals.jsonl"
PLAYBOOK_FILE = Path.home() / ".claude" / "rules" / "playbook.md"

# ── Detection patterns ─────────────────────────────────────────────────────

CORRECTION_PATTERNS = [
    r"\bno[,.\s!]",
    r"\bnot that\b",
    r"\bwrong\b",
    r"\bdon'?t\b(?!.*\byou\b.*\bthink\b)",
    r"\bstop\s+(doing|that|it)\b",
    r"\bi said\b",
    r"\bi told you\b",
    r"\bi already\b",
    r"\bthat'?s not\b",
    r"\binstead of\b",
    r"\byou should have\b",
    r"\bwhy did you\b",
    r"\bnot what i\b",
    r"\bthat was wrong\b",
    r"\bthe other\b",
    r"\bactually[,\s]\b",
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


def detect_signal(message: str) -> dict | None:
    """Detect learning signals in user message."""
    msg_lower = message.lower().strip()

    if len(msg_lower) < 5 or msg_lower.startswith("/"):
        return None

    for pattern in FRUSTRATION_PATTERNS:
        if re.search(pattern, msg_lower):
            return {"type": "frustration", "severity": "high", "message_preview": message[:120]}

    for pattern in CORRECTION_PATTERNS:
        if re.search(pattern, msg_lower):
            return {"type": "correction", "severity": "high", "message_preview": message[:120]}

    for pattern in POSITIVE_PATTERNS:
        if re.search(pattern, msg_lower):
            return {"type": "positive", "severity": "normal", "message_preview": message[:120]}

    return None


def count_pending_signals() -> int:
    """Count signals since last playbook update."""
    if not SIGNAL_FILE.exists():
        return 0

    pb_mtime = PLAYBOOK_FILE.stat().st_mtime if PLAYBOOK_FILE.exists() else 0

    count = 0
    try:
        for line in SIGNAL_FILE.read_text(encoding="utf-8").strip().split("\n"):
            if not line.strip():
                continue
            try:
                entry = json.loads(line)
                ts = datetime.fromisoformat(entry.get("timestamp", "")).timestamp()
                if ts > pb_mtime:
                    count += 1
            except (json.JSONDecodeError, ValueError):
                continue
    except Exception:
        pass
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
                print(f"[Learning checkpoint: {pending} unprocessed signals — update playbook before continuing]")
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
            print(f"[Learning checkpoint: {pending} unprocessed signals — update playbook NOW]")

    except Exception:
        pass

    sys.exit(0)


if __name__ == "__main__":
    main()
