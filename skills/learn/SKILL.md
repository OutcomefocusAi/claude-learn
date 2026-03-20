---
name: learn
description: >
  /learn — Review, manage, and interact with the self-improvement playbook.
  Shows what Claude has learned, scored rules, capability frontier, pending
  signals, regressions, community rules. Learning happens automatically
  via behavioral protocol and mechanical hooks — this skill is for
  visibility, control, and contributing to collective intelligence.
---

# /learn — Self-Improvement Dashboard

## Overview

Claude learns continuously via three layers:
1. **Behavioral protocol** in `~/.claude/rules/playbook.md` (auto-loaded)
2. **Language detection hook** (UserPromptSubmit) — corrections, frustration, praise
3. **Outcome tracking hook** (PostToolUse) — test/build/deploy results, retries, churn

Two playbooks auto-load:
- **Personal**: `~/.claude/rules/playbook.md` — your rules, your scores
- **Community**: `~/.claude/rules/playbook-community.md` — collective intelligence from all users

## When Invoked

### Step 1: Load Current State

Read both playbooks and signal files. Present:
```
=== Playbook Status ===
Personal:         N rules across N categories (N meta-rules, N workflows)
Community:        N universal rules
Token usage:      ~N / 5000
Proven rules:     N (sessions >= 3)
Top 3 by score:   [list]
Latest 3 added:   [list]
Regressions:      N rules declining (or "none")
Uncertainties:    N tracked items
Frontier:         N active experiments, N tested
Archive:          N decayed rules
Pending signals:  N unprocessed
Session context:  [detected ctx tags]
```

### Step 2: Process Pending Signals

Group by source, draft rules for each, apply generalization + causal chain analysis. Check for second-order patterns (3+ rules with same shape → meta-rule).

### Step 3: Session Scan

Check for uncaptured learnings, rule violations, regression patterns, workflow chain opportunities, and negative space items.

### Step 4: Interactive Menu

```
What would you like to do?
 1. Review all rules (by category, score, or context)
 2. Add a learning manually (score 2.0)
 3. Remove or adjust a rule
 4. Review capability frontier + add experiments
 5. View workflows (linked rule chains)
 6. View uncertainty tracker
 7. View community playbook
 8. Contribute proven rules to community
 9. View archived rules (restore one?)
10. Force pruning pass
11. Meta-learning analysis
12. Export playbook
13. Done
```

## Sub-Commands

- `/learn` — full review
- `/learn status` — quick stats
- `/learn add "<rule>"` — manually add (score 2.0)
- `/learn frontier` — capability frontier
- `/learn workflows` — view/manage linked rule chains
- `/learn uncertainties` — things you don't know
- `/learn community` — view community playbook + status
- `/learn contribute` — **contribute proven rules to collective intelligence** (see below)
- `/learn regress` — view regression alerts
- `/learn prune` — force pruning + merge similar
- `/learn meta` — meta-learning analysis (velocity, blindspots, second-order patterns)
- `/learn export` — shareable format
- `/learn signals` — raw hook signals
- `/learn reset` — archive everything, fresh start

## `/learn contribute` — Collective Intelligence

This is how the community playbook grows. When invoked:

### Step 1: Select Candidates
Scan your personal playbook for rules meeting contribution criteria:
- Score >= 3.0 (well-validated)
- Sessions >= 3 (proven across multiple sessions)
- Generalized wording (not user-specific or project-specific)
- Has a causal explanation (WHY, not just WHAT)

Present the candidates: "These N rules qualify for community contribution."

### Step 2: User Selects
The user picks which rules to contribute (or all).

### Step 3: Validate Existing Community Rules
Read `~/.claude/rules/playbook-community.md` and check each community rule against your personal playbook:
- If you have a similar personal rule at score 3.0+ → report as "validated"
- If the community rule decayed on your system → report as "not validated"
- If you haven't encountered it → report as "no data"

This validation report is how community scores increase. When 3+ users independently validate a rule, the maintainer bumps its template score from 1.0 to 2.0. At 5+ validators → 3.0.

### Step 4: Prepare Submission
For each new rule:
- Strip personal context (user names, project paths, personal tools)
- Ensure wording is universal ("When working on X" not "In Jeremy's X project")
- Set score to 1.0 (must be validated by community)
- Format for the community playbook

For validation reports on existing rules:
- Include rule name, your local score, confirmed count, session count
- This is the evidence that drives community score increases

### Step 5: Submit
Create a GitHub issue on the claude-learn repo:
```bash
gh issue create --repo OutcomeFocusAi/claude-learn \
  --title "Community contribution: [N] new rules + [M] validations" \
  --body "[formatted new rules + validation report on existing rules]"
```

The issue includes TWO sections:
1. **New rules** — proposed additions to the community playbook
2. **Validation report** — your scores on existing community rules

The maintainer reviews, deduplicates new rules, aggregates validation counts, bumps community scores where warranted, and merges. Next plugin update delivers changes to all users.

### Alternative: Direct PR
For users with repo write access:
```bash
# Edit templates/playbook-community.md directly
# Add rules to the "Universal Rules" section
# Submit PR
gh pr create --title "Add N community rules" --body "[rules + evidence]"
```

### How Community Rules Reach Users
1. Maintainer merges contribution into `templates/playbook-community.md`
2. New plugin version is released
3. User runs `claude plugin update claude-learn@outcomefocusai`
4. SessionStart hook syncs updated community playbook to `~/.claude/rules/`
5. Community rules auto-load next session
6. Each user's Claude validates them independently — good rules persist, bad ones decay per-user

## Pruning Pass

1. Archive scored below 1.0, delete below 0
2. Merge >70% semantic overlap (combine scores)
3. Check for second-order patterns → generate meta-rules
4. Check for sequential rules → generate workflows
5. Check for regression patterns
6. If over 5000 token budget, archive lowest-scored
7. Report all changes

## Meta-Learning Analysis (`/learn meta`)

1. **Category distribution** — which categories have most/fewest rules?
2. **Score distribution** — noisy capture (many low) or quality (few high)?
3. **Learning velocity** — rules/session over last 5 sessions
4. **Second-order patterns** — any 3+ rules sharing a shape?
5. **Causal depth** — how many rules have `cause:` explanations?
6. **Workflow coverage** — are related rules linked?
7. **Regression alerts** — proven rules no longer being confirmed?
8. **Uncertainty gaps** — tracked unknowns that need frontier experiments?
9. **Session quality trend** — positive/negative signal ratio over time
10. **Community alignment** — how many community rules are validated locally?

## Key Principles

1. **Learning is always on** — dashboard, not engine
2. **Three detection layers** — behavioral + language + outcome
3. **Second-order learning** — patterns of patterns, not just patterns
4. **Causal > correlational** — prevent problems, don't just handle them
5. **Collective intelligence** — your proven rules help everyone
6. **Quality > quantity** — meta-rules replace clusters of specific rules
7. **Track uncertainty** — knowing what you don't know prevents confident mistakes
8. **Regression awareness** — catch declining performance before the user does
9. **Anticipatory execution** — proactive, not reactive
10. **Measure experiments** — count tool calls, not vibes
