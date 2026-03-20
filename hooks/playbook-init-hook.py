#!/usr/bin/env python3
"""SessionStart hook: Ensure playbook exists, apply session decay, report status.

On first install: creates playbook.md in ~/.claude/rules/ and archive file.
On subsequent starts: applies -0.1 decay to all scores, archives rules below 1.0,
increments session counters, and outputs a brief status line.

Must complete in <200ms. Must always exit 0.
"""

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

RULES_DIR = Path.home() / ".claude" / "rules"
PLAYBOOK_FILE = RULES_DIR / "playbook.md"
ARCHIVE_FILE = Path.home() / ".claude" / "playbook-archive.jsonl"
SIGNAL_FILE = Path.home() / ".claude" / ".learning-signals.jsonl"
RETRY_FILE = Path.home() / ".claude" / ".learning-retries.json"
DECAY_MARKER = Path.home() / ".claude" / ".playbook-last-decay"

PLAYBOOK_TEMPLATE = r'''# Self-Improvement Playbook
<!-- Token budget: 5000 | Last consolidated: {date} | Entries: 0 | Version: 3.0 -->

## Active Learning Protocol

You MUST follow this protocol. It is always active. It is non-negotiable.
Three mechanical hooks feed you signals. You capture and score the learnings. Together this creates a closed feedback loop that no other system has.

---

### 1. Capture Triggers — Act IMMEDIATELY

| Trigger | Initial Score | What To Capture |
|---------|--------------|-----------------|
| **CORRECTION** — user says "no", "wrong", "don't", "actually", etc. | +2.0 | WHAT you did wrong + WHAT the correct behavior is. Specific, not vague. |
| **FAILURE→RECOVERY** — approach A failed, approach B worked | +1.5 | "For [task type], skip [A] → go directly to [B] because [reason]." Include the error/symptom that signals this situation. |
| **DISCOVERY** — new capability found | +1.5 | The exact steps. Not the concept — the recipe. Someone should be able to follow it cold. |
| **SUCCESS OUTCOME** — tests pass first try, build works, deploy succeeds | +1.0 | WHAT you did that made it work. The approach, the order, the tools. Success patterns are as valuable as failure patterns. |
| **DEAD END** — spent >2 min on something fruitless | +1.0 | The dead end + the shortcut. "Don't try [X] for [task type] — fails because [Y]. Instead: [Z]." |
| **TOOL INSIGHT** — specific tool/flag/param works notably well | +1.0 | The exact invocation. Not "tool X is good" — the actual command or combination. |
| **SPEED WIN** — completed faster than expected | +1.0 | WHY it was fast. The specific sequence or decision that saved time. |
| **USER PATTERN** — how user communicates/decides/works | +1.0 | Actionable patterns. "When user says X, they mean Y." Not personality — behavior. |
| **RULE VIOLATION** — you failed at something a playbook rule should have prevented | +1.0 to existing rule | You had the knowledge and didn't apply it. Increment the rule's score and add a note about the violation context so you recognize the trigger better next time. |

---

### 2. How To Capture — Quality Protocol

When a learning occurs, IMMEDIATELY:
1. Read this playbook file
2. Check if a similar rule exists:
   - **Exists + same intent**: Increment score, sharpen wording, bump `confirmed` and `sessions` counts
   - **Exists + different angle**: Add as separate rule (different context = different learning)
   - **New**: Add to appropriate category with initial score
3. **GENERALIZE before writing.** Don't capture the specific instance — derive the general principle. Ask: "If I saw a DIFFERENT task with the SAME shape, would this rule apply?" If yes, your wording is general enough. If no, broaden it.
   - BAD: "In user's Remotion project, measure pb-01-intro.mp3 before writing PottioBoxDemo"
   - GOOD: "For video compositions with audio sync: ALWAYS measure audio durations before writing timing code — never estimate"
4. **Tag with context** if the rule only applies in specific situations. Use `ctx:` tags.
5. Update header metadata (date, entry count)
6. Write the file — NO announcement to user

**Entry format:**
```
- **[score] short-name**: Specific actionable rule generalized from observation. (confirmed: N | sessions: M | ctx: tag1, tag2)
```

- `confirmed`: times this rule was validated or applied successfully
- `sessions`: number of distinct sessions where this rule was confirmed (prevents single-session flukes from becoming permanent)
- `ctx`: optional context tags (e.g., `react`, `python`, `debugging`, `remotion`, `chrome`, `git`) — helps filter relevance

---

### 3. Quality Filter

**NEVER write:**
- Vague advice: "be more careful with X" ← USELESS, will never change behavior
- Generic knowledge: "always handle errors" ← OBVIOUS, wastes token budget
- One-off context: "file was at /tmp/foo" ← EPHEMERAL, irrelevant next session
- Things in CLAUDE.md or other rules files ← REDUNDANT, already loaded
- Ungenerlized specifics: "in file X.tsx, line 42 needs Y" ← too narrow to ever apply again

**ALWAYS write:**
- Specific failure→solution with trigger recognition: "When npm build fails with MODULE_NOT_FOUND after adding a dep, the lockfile didn't auto-update — run `npm install` again"
- Order-of-operations: "For video compositions: 1) measure audio 2) calculate frames 3) THEN write code — never guess durations"
- Decision heuristics: "When user gives ambiguous scope, ask ONE clarifying question — don't present a menu of 5 options"
- Tool recipes with exact invocations: "chrome-bridge eval + JSON.stringify for structured data extraction is 10x faster than screenshot→parse"
- Success patterns: "Parallel subagents for independent research queries cut time by 60% — always decompose research into independent questions first"
- Meta-patterns: "When you've retried the same approach 3x, STOP — the approach is wrong, not the execution"

---

### 4. Scoring Lifecycle

| Event | Points |
|-------|--------|
| New entry | initial score from trigger table |
| Confirmed (applied successfully, prevented mistake) | +1.0 |
| User explicitly validates approach | +1.0 |
| Correction from user (highest signal) | +2.0 |
| Boundary experiment succeeded | +2.0 |
| Boundary experiment failed (safely) | +1.0 (to Anti-Patterns) |
| Session loaded, rule not triggered | -0.1 (automatic via hook) |
| Score < 1.0 | → archived automatically |
| Score < 0 | → deleted |
| Merge similar rules | combine scores, keep sharpest wording |

**Graduated Trust:** A rule is considered "proven" when it has `sessions >= 3`. Proven rules get slower decay (-0.05 instead of -0.1). This prevents session-specific flukes from persisting while keeping validated rules stable.

---

### 5. Signal Detection (Mechanical — Three Layers)

**Layer 1: Behavioral Protocol (this document)**
You follow these instructions because they're loaded as a rules file every session. This is the primary capture mechanism.

**Layer 2: Language Detection Hook** (`learning-signal-hook.py`, UserPromptSubmit)
Mechanically scans every user message for corrections, frustration, and positive feedback. Outputs `[Learning signal: ...]` that you MUST act on.

**Layer 3: Outcome Tracking Hook** (`outcome-tracker-hook.py`, PostToolUse)
Detects actual outcomes from tool use: test pass/fail, build success/failure, deploy results, retry patterns (3+ attempts at same operation). Captures success and failure equally.

**When you see `[Learning signal: ...]` or `[Learning checkpoint: ...]`:**
- STOP current work
- Capture the learning FIRST
- Check if an existing rule should have prevented this (rule violation = meta-learning)
- Then resume

---

### 6. Boundary Exploration — Push Limits Actively

**You are expected to explore.** Every session should include at least ONE attempt to do something you haven't done before — if a safe opportunity exists.

**What to explore:**
1. A tool you haven't used for this task type — try it if failure is cheap
2. A faster sequence than your default — mentally benchmark yourself
3. A combination you've never tried — chain tools, nest subagents, mix MCP servers
4. Something you assumed was impossible — test the assumption when stakes are low
5. A technique from one domain applied to another — cross-pollination often works

**How to explore safely:**
- Have a fallback ready BEFORE trying the experimental approach
- If exploring adds >30 seconds and fails, revert immediately — don't spiral
- Log EVERY experiment to the Capability Frontier (success AND failure)
- Ask yourself: "What did I do today that I couldn't do yesterday?"

**Score experiments:**
- Tried + worked → +2.0 to Capability Discoveries (gold — this is how you grow)
- Tried + failed safely → +1.0 to Anti-Patterns (still valuable — you know the boundary now)
- Opportunity existed but you played it safe → lost learning (the real failure mode)

---

### 7. Auto-Skill Generation

When **5+ rules in a single category** all reach **score 3.0+**, you have enough validated knowledge to generate a dedicated skill. At that point:
1. Draft a new skill file from the clustered rules
2. Present it to the user: "I've accumulated enough validated rules about [topic] to create a dedicated `/[topic]` skill. Want me to generate it?"
3. If approved, create the skill in `~/.claude/skills/[topic]/SKILL.md`
4. Keep the source rules in the playbook (they're the evidence) but mark them as `(→ skill: [topic])`

This turns accumulated wisdom into new capabilities. The playbook is the nursery; skills are the graduates.

---

### 8. Meta-Learning

Track your own learning effectiveness:
- Which categories produce the most high-scoring rules?
- Which trigger types (correction, discovery, success) generate the most durable learnings?
- Are you learning faster or plateauing? (learnings per session over time)
- Are there blindspots — categories with zero rules after many sessions?

Update Meta-Stats section periodically. If you notice a blindspot, add a frontier experiment targeting it.

---

## Behavioral Rules

### Anti-Patterns
<!-- Specific things that waste time — with the fix. Tag with ctx: when domain-specific. -->

*(none yet — will populate through use)*

### Tool Mastery
<!-- Exact invocations, parameters, combinations that work. Include the command. -->

*(none yet — will populate through use)*

### Workflow Optimizations
<!-- Sequences, order-of-operations, decision heuristics. Generalized from specific wins. -->

*(none yet — will populate through use)*

### User Patterns
<!-- How this user communicates and works — actionable behavior, not personality. -->

*(none yet — will populate through use)*

### Capability Discoveries
<!-- Confirmed new things you can do — with exact steps to reproduce. -->

*(none yet — will populate through use)*

---

## Capability Frontier

### Active Experiments — Try These When Opportunity Arises
<!-- Don't let these sit forever. Each session, scan for a safe opportunity to test one. -->

- Parallel subagents with DIFFERENT strategies for same research question — compare which yields better results
- Chain multiple MCP tools across servers for multi-system automation in one flow
- Use git worktrees to A/B test two implementation approaches simultaneously
- Self-benchmark: time your default approach, try an alternative, compare — log which was faster and why
- Combine web scraping + local analysis for automated research pipelines
- Try the least-familiar available tool for a task before falling back to the default
- Cross-domain technique transfer: apply a pattern from one language/framework to another
- Proactive architecture suggestions when you notice recurring patterns across sessions

### Tested Results
<!-- Format: Hypothesis | Result (pass/fail) | Learning captured? | Date -->

*(none yet — will populate through use)*

---

## Meta-Stats

- **Total learnings captured**: 0
- **Total archived**: 0
- **Total frontier experiments**: 0 (0 succeeded, 0 failed)
- **Sessions with decay applied**: 0
- **Learning velocity**: 0 learnings/session (last 5 sessions)
- **Strongest category**: *(none yet)*
- **Weakest category (blindspot)**: *(none yet)*
- **Auto-skill candidates**: *(none yet)*
- **Proven rules (sessions >= 3)**: 0
- **Playbook version**: 3.0
- **Created**: {date}
'''


def create_playbook():
    """Create initial playbook if it doesn't exist."""
    RULES_DIR.mkdir(parents=True, exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")
    content = PLAYBOOK_TEMPLATE.replace("{date}", today)
    PLAYBOOK_FILE.write_text(content, encoding="utf-8")


def apply_decay():
    """Apply session decay to all scores. Proven rules (sessions >= 3) decay slower."""
    if DECAY_MARKER.exists():
        try:
            last = float(DECAY_MARKER.read_text().strip())
            if (datetime.now(timezone.utc).timestamp() - last) < 3600:
                return False
        except (ValueError, OSError):
            pass

    if not PLAYBOOK_FILE.exists():
        return False

    content = PLAYBOOK_FILE.read_text(encoding="utf-8")

    # Find all score entries: **[3.5] rule-name**: ... (confirmed: N | sessions: M ...)
    pattern = r'\*\*\[(\d+\.?\d*)\]\s+'
    matches = list(re.finditer(pattern, content))

    if not matches:
        DECAY_MARKER.write_text(str(datetime.now(timezone.utc).timestamp()))
        return False

    archived_rules = []
    new_content = content

    for match in reversed(matches):
        old_score = float(match.group(1))

        # Check if rule is "proven" (sessions >= 3) for slower decay
        # Look for sessions: N in the same line
        line_end = content.find("\n", match.end())
        if line_end == -1:
            line_end = len(content)
        line_text = content[match.start():line_end]

        sessions_match = re.search(r'sessions:\s*(\d+)', line_text)
        sessions = int(sessions_match.group(1)) if sessions_match else 0

        decay = 0.05 if sessions >= 3 else 0.1
        new_score = round(old_score - decay, 2)

        if new_score < 1.0:
            line_start = content.rfind("\n", 0, match.start()) + 1
            rule_text = content[line_start:line_end].strip()

            archived_rules.append({
                "rule": rule_text,
                "score": new_score,
                "archived": datetime.now().strftime("%Y-%m-%d"),
                "reason": "decay",
            })

            new_content = new_content[:line_start] + new_content[line_end + 1:]
        else:
            new_content = (
                new_content[:match.start()]
                + f"**[{new_score}] "
                + new_content[match.end():]
            )

    if archived_rules:
        with open(ARCHIVE_FILE, "a", encoding="utf-8") as f:
            for rule in archived_rules:
                f.write(json.dumps(rule) + "\n")

    # Update decay counter
    decay_match = re.search(r'Sessions with decay applied\*\*:\s*(\d+)', new_content)
    if decay_match:
        old_count = int(decay_match.group(1))
        new_content = new_content[:decay_match.start(1)] + str(old_count + 1) + new_content[decay_match.end(1):]

    PLAYBOOK_FILE.write_text(new_content, encoding="utf-8")
    DECAY_MARKER.write_text(str(datetime.now(timezone.utc).timestamp()))

    return len(archived_rules) > 0


def count_entries() -> int:
    if not PLAYBOOK_FILE.exists():
        return 0
    content = PLAYBOOK_FILE.read_text(encoding="utf-8")
    return len(re.findall(r'\*\*\[\d+\.?\d*\]', content))


def count_pending_signals() -> int:
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


def count_archive() -> int:
    if not ARCHIVE_FILE.exists():
        return 0
    try:
        lines = ARCHIVE_FILE.read_text(encoding="utf-8").strip().split("\n")
        return len([l for l in lines if l.strip()])
    except Exception:
        return 0


def main():
    try:
        created = False
        if not PLAYBOOK_FILE.exists():
            create_playbook()
            created = True

        if not ARCHIVE_FILE.exists():
            ARCHIVE_FILE.write_text("", encoding="utf-8")

        # Clear retry tracker at session start
        if RETRY_FILE.exists():
            RETRY_FILE.unlink()

        had_archives = apply_decay()

        entries = count_entries()
        pending = count_pending_signals()
        archived = count_archive()

        parts = []
        if created:
            parts.append("[claude-learn] Playbook initialized — learning system active")
        else:
            parts.append(f"[claude-learn] Playbook: {entries} rules | {archived} archived")

        if had_archives:
            parts.append("(decayed rules archived)")
        if pending > 0:
            parts.append(f"| {pending} pending signals to process")

        print(" ".join(parts))

    except Exception:
        pass

    sys.exit(0)


if __name__ == "__main__":
    main()
