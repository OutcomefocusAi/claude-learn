---
name: learn
description: >
  /learn — Review, manage, and interact with the self-improvement playbook.
  Shows what Claude has learned, scored rules, capability frontier, pending
  signals from language and outcome hooks. The learning itself happens
  automatically via behavioral protocol and mechanical hooks — this skill
  is for visibility, control, and meta-analysis.
---

# /learn — Self-Improvement Dashboard

## Overview

Claude continuously captures learnings via three mechanisms:
1. **Behavioral protocol** in `~/.claude/rules/playbook.md` (auto-loaded, Claude follows capture instructions)
2. **Language detection hook** (UserPromptSubmit) — detects corrections, frustration, positive feedback
3. **Outcome tracking hook** (PostToolUse) — detects test/build/deploy outcomes, retry patterns, edit churn

Learning is always happening. This skill is the control panel.

## When Invoked

### Step 1: Load Current State

Read `~/.claude/rules/playbook.md` and `~/.claude/.learning-signals.jsonl` (if exists).
Count archive entries from `~/.claude/playbook-archive.jsonl`.

Present:
```
=== Playbook Status ===
Entries:          N rules across N categories
Token usage:      ~N / 5000
Proven rules:     N (sessions >= 3)
Top 3 by score:   [list with scores]
Latest 3 added:   [most recently added/updated]
Frontier:         N active experiments, N tested
Archive:          N decayed rules
Pending signals:  N unprocessed
  - N from user language (corrections/praise)
  - N from outcome tracking (test/build/retry/churn)
Learning velocity: N learnings/session (last 5 sessions)
```

### Step 2: Process Pending Signals

If there are unprocessed signals in `.learning-signals.jsonl`:
- Group by source (user_language vs outcome)
- For each signal type, draft a rule:
  - **Corrections/frustrations**: "This signal suggests: [draft rule]. Capture it?"
  - **Outcome successes**: "This succeeded — what approach made it work? [draft rule]"
  - **Outcome failures**: "This failed — what should you do differently? [draft rule]"
  - **Retry patterns**: "You retried this 3x+ — what's the better approach? [draft rule]"
  - **Edit churn**: "You edited this file 5x+ — what was the root cause of churn?"
  - **Positive feedback**: "User validated this approach — which rule does it confirm?"
- Apply generalization principle: derive the general rule, not the specific instance
- Process all, then clear processed entries

### Step 3: Session Scan

Analyze the current session for learnings the hooks might have missed:
- Approaches that were unusually fast or slow
- New tool combinations tried
- Boundary experiments (attempted or missed opportunities)
- Patterns in how you solved problems
- Rule violations (did you fail at something a playbook rule should have caught?)

Present candidates for approval.

### Step 4: Auto-Skill Check

Scan each category for 5+ rules with score 3.0+. If found:
- "You have N proven rules about [topic]. Want me to generate a dedicated `/[topic]` skill?"
- If approved, create skill, mark source rules with `(→ skill: [topic])`

### Step 5: Interactive Menu

```
What would you like to do?
1. Review all rules (by category, by score, or by context tag)
2. Add a learning manually (starts at score 2.0)
3. Remove or adjust a rule's score
4. Review capability frontier + add experiments
5. View archived rules (restore one?)
6. Force pruning pass (merge similar, archive weak)
7. Show meta-learning analysis
8. Export playbook (shareable format)
9. Done
```

## Sub-Commands

- `/learn` — full review (all steps)
- `/learn status` — step 1 only (quick glance)
- `/learn add "<rule>"` — manually add with score 2.0
- `/learn frontier` — show frontier, add experiments, review results
- `/learn prune` — force archive low-scored, merge similar rules
- `/learn meta` — meta-learning analysis: velocity, blindspots, category strength
- `/learn history` — full stats and timeline
- `/learn export` — clean shareable format (scores reset to 1.0)
- `/learn signals` — show raw pending signals from all hooks
- `/learn reset` — archive everything, fresh start (confirms first)

## Pruning Pass

1. Archive anything scored below 1.0
2. Delete anything scored below 0
3. Merge rules with >70% semantic overlap (combine scores, keep sharper wording)
4. If over 5000 token budget, archive lowest-scored until under budget
5. Check for auto-skill generation candidates
6. Update meta-stats
7. Report what was pruned/merged/promoted

Archive format:
```json
{"rule": "...", "category": "...", "score": 0.8, "archived": "2026-03-19", "reason": "decay|merged|budget", "confirmed": 2, "sessions": 1}
```

## Meta-Learning Analysis (`/learn meta`)

When invoked, analyze:
1. **Category distribution** — which categories have the most/fewest rules?
2. **Score distribution** — are most rules low-scored (noisy capture) or high-scored (quality)?
3. **Learning velocity** — rules captured per session over last 5 sessions. Increasing = growing. Flat = plateauing. Decreasing = either mastery or blind spots.
4. **Trigger analysis** — which trigger types (correction, discovery, success, failure) produce the most durable rules?
5. **Blindspot detection** — categories with 0 rules after 5+ sessions. Add frontier experiments targeting them.
6. **Rule lifecycle** — average time from creation to "proven" (sessions >= 3). How long until rules validate?
7. **Auto-skill candidates** — categories approaching the 5-rule/3.0-score threshold.

Present findings and suggest actions.

## Export Format

When `/learn export` is invoked:
- Output the complete plugin structure (all files) so anyone can install it
- Include learned rules with scores reset to 1.0 (fresh start with seed knowledge)
- Include all hook scripts unchanged
- Include setup instructions
- Exclude meta-stats (personal), archive (stale), and signal files (ephemeral)

## Key Principles

1. **Learning is always on** — this skill is the dashboard, not the engine
2. **Three detection layers** — behavioral + language hook + outcome hook = near-complete coverage
3. **Quality over quantity** — 10 sharp generalized rules beat 50 specific observations
4. **Graduated trust** — rules need multi-session confirmation to be "proven"
5. **Success = failure in value** — capture what WORKED, not just what broke
6. **Boundary exploration is mandatory** — at least one experiment per session when safe
7. **Generalize, don't template** — derive principles, not instance-specific instructions
8. **Auto-evolve** — accumulated rules graduate into dedicated skills
9. **Meta-learn** — learn about how you learn, find blindspots, track velocity
10. **Transparency** — show confidence levels, never hide uncertainty
