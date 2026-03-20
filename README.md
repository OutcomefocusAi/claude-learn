# claude-learn

> **The self-improving plugin for Claude Code.** Claude gets measurably better every session — automatically. Your proven learnings help every user. Every user's learnings help you.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Claude Code Plugin](https://img.shields.io/badge/Claude_Code-Plugin-blueviolet)]()
[![Version](https://img.shields.io/badge/version-3.0.0-green)]()

---

## What This Does

Claude Code starts every session from zero. You correct the same mistakes. It retries the same dead ends. Good approaches vanish. **claude-learn fixes this.**

It captures behavioral rules from real outcomes, scores them with evidence, validates across sessions, and loads them automatically. Rules that work persist. Flukes decay. Clusters of rules graduate into skills. And your proven rules feed a **community playbook** that makes everyone's Claude better.

```
Observe → Capture → Score → Validate → Decay or Confirm → Prune or Graduate
    ↑         ↑         ↑                                        |
    |     [3 layers]  [evidence]                                  |
    └─────────────────────────────────────────────────────────────┘

Your proven rules ──→ Community Playbook ──→ All users benefit
```

---

## Collective Intelligence

**This is the headline feature no other tool has.**

When your rules reach "proven" status (validated across 3+ sessions, score 3.0+), you can contribute them to the community playbook. Other users receive them on their next plugin update. Their Claude validates the rules independently — good rules survive, bad ones decay per-user.

**A rule validated by many independent users across different projects is essentially a universal law of AI coding assistance.**

### How It Works

```
You use Claude normally
    ↓
Rules accumulate in your personal playbook (scored, validated)
    ↓
Rules reach "proven" status (score 3.0+, sessions >= 3)
    ↓
Run /learn contribute → selects your best generalized rules
    ↓
Submitted as GitHub issue or PR to claude-learn repo
    ↓
Maintainer reviews, deduplicates, merges
    ↓
Plugin update delivers new community rules to ALL users
    ↓
Each user's Claude validates independently
    ↓
Rules that work for many people = universal truth
```

### How to Contribute

```bash
# In Claude Code, run:
/learn contribute

# Claude will:
# 1. Show your proven rules (score 3.0+, 3+ sessions)
# 2. Filter out anything too specific to your setup
# 3. Generalize the wording for universal use
# 4. Create a GitHub issue on this repo with formatted rules

# For repo contributors with write access:
# Edit templates/playbook-community.md directly and submit a PR
```

### Two Playbooks, One System

| Playbook | File | Source | Priority |
|----------|------|--------|----------|
| **Personal** | `~/.claude/rules/playbook.md` | Your sessions | **Highest** — always wins conflicts |
| **Community** | `~/.claude/rules/playbook-community.md` | All contributors | Baseline — must prove itself to you |

Both auto-load every session. Personal rules take priority. Community rules start at score 1.0 on your system and must earn their way up through your usage.

---

## Why This Is Better Than Every Alternative

| Capability | claude-learn | Homunculus | codesurf-insights | claude-mem |
|-----------|-------------|-----------|-------------------|-----------|
| Real-time learning (3 layers) | **Yes** | 1 layer | Post-session | N/A |
| Scored rules with evidence | **Yes** | No | No | No |
| Closed feedback loop | **Yes** | No | No | No |
| Collective intelligence | **Yes** | No | No | No |
| Second-order learning (meta-rules) | **Yes** | No | No | No |
| Causal chain capture | **Yes** | No | No | No |
| Context-aware decay | **Yes** | No | No | No |
| Regression detection | **Yes** | No | No | No |
| Anticipatory execution | **Yes** | No | No | No |
| Workflow generation from rule chains | **Yes** | No | No | No |
| Negative space / uncertainty tracking | **Yes** | No | No | No |
| Session quality correlation | **Yes** | No | No | No |
| Structured A/B experiments | **Yes** | No | No | No |
| Auto-skill generation | **Yes** | Partial | No | No |
| Graduated trust (multi-session) | **Yes** | No | No | No |
| Outcome-based learning | **Yes** | No | No | No |
| Token-budgeted auto-pruning | **Yes** | No | No | No |
| Memory system integration | **Yes** | No | No | N/A |

### In Plain English

- **Homunculus** captures observations but never validates them. You get a growing pile of unverified notes.
- **codesurf-insights** analyzes logs after the fact. No real-time learning.
- **claude-mem** remembers what happened. It doesn't change what Claude does next.
- **claude-learn** changes behavior based on evidence. And shares proven behavior with everyone.

---

## Architecture

### Three Detection Layers

**Layer 1: Behavioral Protocol** — The playbook auto-loads as a rules file. Contains 19 protocol sections that instruct Claude how to capture, score, generalize, verify, and evolve learnings.

**Layer 2: Language Detection Hook** (UserPromptSubmit) — Scans every user message for corrections, frustration, and positive reinforcement. Injects `[Learning signal]` reminders.

**Layer 3: Outcome Tracking Hook** (PostToolUse) — Detects test/build/deploy results, retry patterns (3x+), edit churn (5x+), install failures, lint results.

### Learning Levels

| Level | What | Example |
|-------|------|---------|
| **Rule** | Single behavioral instruction | "Run tests after every edit" |
| **Meta-Rule** | Abstraction across 3+ similar rules | "Before calling any external dependency, verify it's available" |
| **Workflow** | Linked chain of rules with order | "lint → test → coverage → commit" |
| **Causal Rule** | Upstream prevention instead of downstream handling | "Use CLI to add deps, not manual edits — prevents sync issues" |
| **Anticipatory Rule** | Proactive setup before the situation arises | "When entering video work, measure all audio durations upfront" |

### Scoring

| Event | Points |
|-------|--------|
| User correction | +2.0 |
| Boundary experiment succeeded | +2.0 |
| Failure→recovery | +1.5 |
| Discovery | +1.5 |
| Confirmed / success outcome | +1.0 |
| Not triggered (context-aware) | -0.1 (-0.05 if proven) |
| Below 1.0 → archived | Below 0 → deleted |

### Safety Mechanisms

- **Graduated trust**: Rules need 3+ session confirmations to be "proven"
- **Context-aware decay**: Remotion rules don't decay during Python work
- **Regression detection**: Flags proven rules that stopped being confirmed
- **Uncertainty tracking**: Explicit "I don't know" prevents confident mistakes
- **Session quality tracking**: Catches rules that are followed but counterproductive

---

## Installation

```bash
# Add marketplace
claude plugin marketplace add OutcomeFocusAi/claude-learn

# Install
claude plugin install claude-learn@outcomefocusai
```

First session creates both playbooks automatically. Learning begins immediately.

## Usage

**Invisible by default.** Claude learns silently. Use `/learn` when you want to see what's happening.

```
/learn              Full review + interactive menu
/learn status       Quick stats
/learn add "X"      Manual rule (score 2.0)
/learn contribute   Share proven rules with community
/learn community    View community playbook
/learn frontier     Capability experiments
/learn workflows    Linked rule chains
/learn regress      Regression alerts
/learn meta         Learning velocity + analysis
/learn export       Shareable format
```

## Files

| File | Purpose | Auto-loaded |
|------|---------|------------|
| `~/.claude/rules/playbook.md` | Personal scored rules | **Yes** |
| `~/.claude/rules/playbook-community.md` | Community rules | **Yes** |
| `~/.claude/playbook-archive.jsonl` | Decayed rules | No |
| `~/.claude/.learning-signals.jsonl` | Hook signals | No |
| `~/.claude/.playbook-regression.json` | Regression tracker | No |

## FAQ

**Will this slow me down?** No. Hooks < 200ms. Captures ~ 300 tokens each.

**What if I close the tab?** Learnings write immediately to disk. No batching.

**Cross-project?** Yes. Context tags filter relevance. Context-aware decay handles the rest.

**vs CLAUDE.md?** CLAUDE.md is static instructions you write. The playbook is dynamic rules Claude writes, scores, and prunes based on evidence. Use both.

**How do I contribute rules?** Run `/learn contribute`. It selects your proven rules, generalizes them, and creates a GitHub issue. Or submit a PR directly to `templates/playbook-community.md`.

---

## Keywords

Claude Code plugin, self-improving AI, adaptive AI agent, collective intelligence, community learning, scored behavioral rules, machine learning feedback loop, Claude Code skills, continuous learning, AI self-improvement, meta-learning, regression detection, causal learning, workflow generation, anticipatory execution, Claude Code hooks, AI optimization, self-improving LLM, Claude Code automation

## License

MIT — [OutcomeFocus AI](https://github.com/OutcomeFocusAi)
