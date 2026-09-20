"""The learning checkpoint counted everything, so it meant nothing.

The banner read "28,179 unprocessed signals" and could not go down. Three
independent defects stacked:

  1. The marker file it compared timestamps against, ~/.claude/rules/playbook.md,
     has never existed. A missing file gave mtime 0, so every signal ever
     written was "newer than the last playbook update" -- forever.
  2. It counted every row in the log, including the ~15k written by the
     PostToolUse outcome tracker (build_pass, retry_pattern, edit_churn).
     A build that passed is not something the user corrected.
  3. The correction patterns fired on ordinary speech ("I don't need this")
     and on injected prompts the user never typed (live-meeting coaching),
     producing 11,307 high-severity "corrections".

These tests pin each defect shut.
"""
from __future__ import annotations

import importlib.util
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

HOOK_PATH = Path(__file__).resolve().parents[1] / "hooks" / "learning-signal-hook.py"


def _load_hook():
    """The filename is hyphenated, so it cannot be imported by name."""
    spec = importlib.util.spec_from_file_location("learning_signal_hook", HOOK_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules["learning_signal_hook"] = module
    spec.loader.exec_module(module)
    return module


hook = _load_hook()


def _iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat()


MARKER_AGE_HOURS = 24


@pytest.fixture
def log(tmp_path, monkeypatch):
    """A signal log and a playbook marker, both isolated to the test.

    The marker is backdated so a row "since the playbook update" is an ordinary
    past timestamp rather than one in the future.
    """
    signal_file = tmp_path / "signals.jsonl"
    playbook = tmp_path / "playbook-full.md"
    playbook.write_text("# playbook\n", encoding="utf-8")
    marker = (datetime.now(timezone.utc) - timedelta(hours=MARKER_AGE_HOURS)).timestamp()
    os.utime(playbook, (marker, marker))

    monkeypatch.setattr(hook, "SIGNAL_FILE", signal_file)
    monkeypatch.setattr(hook, "PLAYBOOK_FILES", (playbook,))
    monkeypatch.setattr(hook, "ACK_FILE", tmp_path / "never-acked")

    def write(rows):
        signal_file.write_text(
            "".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8"
        )

    write.playbook = playbook
    write.signal_file = signal_file
    return write


def _row(*, source="user_language", type="correction", age_hours=1.0):
    """age_hours = how long ago the row was written. Under MARKER_AGE_HOURS it
    lands after the playbook update and counts; over it, it does not."""
    return {
        "type": type,
        "severity": "high",
        "source": source,
        "message_preview": "x",
        "timestamp": _iso(datetime.now(timezone.utc) - timedelta(hours=age_hours)),
    }


# --- 1. the marker must resolve to a file that exists --------------------

def test_missing_marker_file_does_not_make_every_signal_pending(tmp_path, monkeypatch):
    """The original bug: a marker path that does not exist read as mtime 0,
    so the whole history counted as unprocessed on every single prompt."""
    present = tmp_path / "playbook-full.md"
    present.write_text("# playbook\n", encoding="utf-8")
    monkeypatch.setattr(
        hook, "PLAYBOOK_FILES", (tmp_path / "does-not-exist.md", present)
    )
    monkeypatch.setattr(hook, "ACK_FILE", tmp_path / "never-acked")

    assert hook.last_processed_at() == pytest.approx(present.stat().st_mtime)
    assert hook.last_processed_at() > 0


def test_signals_older_than_the_playbook_are_not_counted(log):
    log([_row(age_hours=96), _row(age_hours=72), _row(age_hours=25)])
    assert hook.count_pending_signals() == 0


def test_an_ack_file_clears_the_count_without_touching_a_playbook(log, tmp_path):
    log([_row(age_hours=1)])
    assert hook.count_pending_signals() == 1
    ack = tmp_path / "acked"
    ack.write_text("", encoding="utf-8")
    hook.ACK_FILE = ack
    assert hook.count_pending_signals() == 0


# --- 2. only genuine user corrections count ------------------------------

def test_outcome_tracker_rows_are_not_counted(log):
    """~15k of the 28k rows came from PostToolUse telemetry, not the user."""
    log([
        _row(source="outcome", type="retry_pattern", age_hours=1),
        _row(source="outcome", type="success", age_hours=1),
        _row(source="outcome", type="edit_churn", age_hours=1),
        _row(source="factory_bridge", type="correction", age_hours=1),
    ])
    assert hook.count_pending_signals() == 0


def test_positive_signals_are_not_counted(log):
    log([_row(type="positive", age_hours=1), _row(type="correction", age_hours=1)])
    assert hook.count_pending_signals() == 1


def test_corrections_and_frustration_since_the_marker_do_count(log):
    log([
        _row(type="correction", age_hours=1),
        _row(type="frustration", age_hours=2),
        _row(type="correction", age_hours=48),      # before the marker
        _row(source="outcome", type="correction", age_hours=1),
    ])
    assert hook.count_pending_signals() == 2


def test_count_stops_at_the_ceiling(log, monkeypatch):
    monkeypatch.setattr(hook, "COUNT_CEILING", 5)
    log([_row(age_hours=1) for _ in range(50)])
    assert hook.count_pending_signals() == 5


def test_malformed_lines_do_not_break_the_count(log):
    path = log.signal_file
    log([_row(age_hours=1)])
    with path.open("a", encoding="utf-8") as handle:
        handle.write("not json at all\n")
        handle.write(json.dumps({"type": "correction", "source": "user_language"}) + "\n")
    assert hook.count_pending_signals() == 1


# --- 3. detection must not fire on ordinary speech -----------------------

@pytest.mark.parametrize("message", [
    "I don't need this file, it can go later",
    "we don't have a staging environment yet",
    "check if you don't already have that dependency",
    "what's wrong with the build right now?",
    "figure out what is wrong here",
    "the number is actually fine as it stands",
    "that is actually the behaviour I expected",
])
def test_ordinary_speech_is_not_a_correction(message):
    signal = hook.detect_signal(message)
    assert signal is None or signal["type"] != "correction", message


@pytest.mark.parametrize("message", [
    "no, don't do that",
    "Don't use the cache here",
    "that's wrong, revert it",
    "you picked the wrong file",
    "Actually, use the other approach",
    "I already told you to skip the migration",
    "why did you commit to main",
])
def test_real_corrections_still_fire(message):
    signal = hook.detect_signal(message)
    assert signal is not None, message
    assert signal["type"] in {"correction", "frustration"}, message


# --- 4. injected prompts are not the user talking ------------------------

def test_live_meeting_coaching_injection_is_not_a_correction():
    injected = (
        "You are coaching Bryan during a LIVE meeting. A META_MODEL trigger "
        "just fired (intent: quantify_vague_amount). Apply the model and don't "
        "stop until the vague amount is quantified."
    )
    assert hook.is_injected(injected) is True
    assert hook.detect_signal(injected) is None


def test_a_pasted_wall_of_text_is_not_a_correction():
    assert hook.detect_signal("no, don't do that. " + "x" * 3000) is None


def test_the_hooks_own_banner_is_not_fed_back_as_a_signal():
    assert hook.detect_signal("[Learning checkpoint: 28179 unprocessed corrections]") is None


# --- 5. the read stays bounded -------------------------------------------

def test_tail_read_is_bounded_and_drops_the_partial_line(tmp_path):
    path = tmp_path / "big.jsonl"
    path.write_text("".join(f"line{i:06d}\n" for i in range(20000)), encoding="utf-8")
    lines = hook.tail_lines(path, 1024)

    assert 0 < len(lines) < 200
    assert lines[-1] == "line019999"
    assert all(line.startswith("line") for line in lines), "partial line leaked in"


def test_tail_read_of_a_missing_file_is_empty(tmp_path):
    assert hook.tail_lines(tmp_path / "nope.jsonl", 1024) == []


# --- 6. a work order is not a correction ---------------------------------
#
# The banner came back: 53 "unprocessed corrections" of which 45 were the
# user's own scoped briefs. A brief is full of the words a correction uses --
# "Do not deploy", "Do not modify code", "No more reviews" -- but it assigns
# work rather than telling the assistant it got something wrong. These pin the
# three shapes that produced the noise.

BRIEF = (
    "Identity\n"
    "You are the release gatekeeper for PR #203.\n\n"
    "Task\n"
    "Wait for the Codex review of the exact current head: cf2cad5f.\n\n"
    "Constraints\n"
    "- Do not modify code, push, or re-run the reviewer.\n"
    "- Do not merge until the verdict is in.\n\n"
    "Output Format\n"
    "Return only the verdict and the head it was taken against.\n"
)

CROSS_SESSION = (
    '<cross-session-message from="uds:\\.\pipe\LOCAL\cc-msg-e0fb" from-name="agile-38" '
    'from-mode="executor">Do not touch the migration. I own it.</cross-session-message>'
)

WORK_ORDER = (
    "Close PR #45 now. No more reviews, fixes, CI redesign, or security-checker work.\n\n"
    "First, read the actual GitHub state for the PR and report the head.\n"
)


@pytest.mark.parametrize("message,label", [
    (BRIEF, "a structured brief with a constraints list"),
    (CROSS_SESSION, "an agent-to-agent relay"),
    (WORK_ORDER, "a work order that opens with 'No more'"),
    ("We hit a deployment preflight blocker. Do not deploy, restart or stop any service.",
     "a constraint sentence naming services"),
    ("Owner confirmation - record this as a decision, not Q-47:\n\n"
     "- Sector is public issuer metadata.\n- Do not reopen it.", "an owner decision"),
    ("You are the sole owner of PR #44.\n\nOwner ruling:\n- Finish and push PR #44.\n"
     "- Exclude the field for now.", "an ownership ruling"),
    ("Delete only the confirmed merged remote branches. Do not delete anything else.",
     "a scoped deletion order"),
    ("Continue with Option 1. Use the owner database URL only; keep its value redacted.",
     "a continuation order"),
])
def test_an_instruction_is_not_a_correction(message, label):
    assert hook.detect_signal(message) is None, label


@pytest.mark.parametrize("message,label", [
    ("no, dont do that - use the other approach", "the plainest correction there is"),
    ("No, don't do it that way.", "a negation with an anaphor"),
    ("that's the wrong file", "naming the work wrong"),
    ("stop doing that", "an explicit stop"),
    ("I already told you to use the other approach", "a repeat"),
    ("why did you change the schema?", "questioning an action taken"),
    ("actually, use the other one", "a reversal"),
    ("Correction to the PR #47 fix: do not commit or push yet. The two-revision "
     "scenario must be exercised first.", "a brief that announces itself as a correction"),
])
def test_a_real_correction_still_counts(message, label):
    signal = hook.detect_signal(message)

    assert signal is not None, label
    assert signal["type"] in {"correction", "frustration"}, label


def test_windows_line_endings_do_not_hide_a_brief():
    assert hook.detect_signal(BRIEF.replace("\n", "\r\n")) is None


def test_a_brief_is_recognised_by_its_sections_not_its_length():
    short_brief = "Identity\nYou own PR #9.\n\nTask\nDo not merge it yet.\n"

    assert len(short_brief) < hook.MAX_HUMAN_PROMPT_CHARS
    assert hook.detect_signal(short_brief) is None
