# claude-learn

> **The self-improving plugin for Claude Code.** Claude gets measurably better every session — automatically.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Claude Code Plugin](https://img.shields.io/badge/Claude_Code-Plugin-blueviolet)]()
[![Version](https://img.shields.io/badge/version-2.0.0-green)]()

## The Problem

Claude Code starts every session with zero memory of what worked last time. You correct the same mistakes. It retries the same dead ends. Good approaches aren't captured. Bad habits aren't eliminated. Every session resets.

**Memory plugins** (claude-mem, episodic-memory) solve recall — they remember *what happened*. But knowing what happened doesn't change *what you do next*. That's the gap.

## The Solution

**claude-learn** captures behavioral rules from real outcomes, scores them based on evidence, and loads them every session. Rules that keep proving value persist. One-off flukes decay. Accumulated wisdom auto-generates new skills.

```
Observe → Capture → Score → Apply → Validate → Decay or Confirm → Prune or Graduate
                                        ↑                                    |
                                        └────────────────────────────────────┘
```

This is a **closed feedback loop**. No other Claude Code plugin has one.

## Why This Is Better Than Every Alternative

### vs. Homunculus (311 stars)
Homunculus captures "instincts" as YAML rules but **never validates them**. Instincts accumulate forever with no scoring, no decay, no way to know which ones actually help. claude-learn scores every rule, confirms across multiple sessions, decays stale ones, and prunes automatically.

### vs. codesurf-insights
Retrospective only — analyzes conversation logs after the session. No real-time capture, no scoring, no structure. Just text appended to CLAUDE.md.

### vs. claude-self-improve
Improves the **code**, not Claude's **behavior**. Proposes PRs for code quality. Different goal entirely.

### vs. claude-mem / episodic-memory
Complementary, not competitive. Memory plugins are the **diary** ("what happened"). claude-learn is the **training program** ("what to do differently"). Use both.

## Feature Comparison

| Capability | claude-learn | Homunculus | codesurf-insights | claude-mem |
|-----------|-------------|-----------|-------------------|-----------|
| Real-time learning capture | **3 layers** | 1 layer | Post-session | N/A (memory, not learning) |
| Scored rules with evidence tracking | **Yes** | No | No | No |
| Outcome-based learning (tool results) | **Yes** | No | No | No |
| Graduated trust (multi-session validation) | **Yes** | No | No | No |
| Closed feedback loop | **Yes** | No | No | No |
| Context-aware decay | **Yes** | No | No | No |
| Auto-skill generation from patterns | **Yes** | Partial | No | No |
| Retry/churn detection | **Yes** | No | No | No |
| Success capture (not just failures) | **Yes** | No | No | No |
| Token-budgeted with auto-pruning | **Yes** | No | No | No |
| Rule self-verification | **Yes** | No | No | No |
| Structured A/B experiments | **Yes** | No | No | No |
| Boundary exploration protocol | **Yes** | No | No | No |
| Meta-learning (learns about learning) | **Yes** | No | No | No |
| Memory system integration | **Yes** | No | No | N/A |
| Generalization protocol | **Yes** | No | No | No |

## How It Works

### Three Detection Layers

Learning capture is near-bulletproof because it doesn't rely on a single mechanism:

**Layer 1: Behavioral Protocol** (primary — always active)
The playbook auto-loads as a rules file every session. It contains detailed instructions for Claude to capture learnings the instant they occur: corrections, failures, discoveries, success patterns, speed wins, user preferences.

**Layer 2: Language Detection Hook** (safety net — UserPromptSubmit)
A Python hook mechanically scans every user message for:
- **Corrections**: "no", "wrong", "don't", "I said", "actually"
- **Frustration**: "again?", "how many times", "you keep"
- **Positive reinforcement**: "perfect", "exactly", "nailed it"

Outputs `[Learning signal]` reminders that Claude cannot ignore. Even if Claude is deep in a complex task and "forgets" to capture, the hook catches it.

**Layer 3: Outcome Tracking Hook** (ground truth — PostToolUse)
A second hook tracks what actually happened with tools:
- **Tests**: pass/fail with counts
- **Builds**: success/failure with error context
- **Deploys**: success/failure
- **Retry patterns**: same operation attempted 3+ times = wrong approach
- **Edit churn**: same file edited 5+ times = unclear thinking
- **Install failures**, **lint results**, and more

This captures **success**, not just failure. When tests pass on the first try, that's a learnable pattern.

### Scoring System

Every rule earns and loses points based on real-world evidence:

| Event | Points |
|-------|--------|
| User correction (highest signal) | +2.0 |
| Boundary experiment succeeded | +2.0 |
| Failure→recovery pattern captured | +1.5 |
| Capability discovery | +1.5 |
| Rule confirmed (applied, prevented mistake) | +1.0 |
| Success outcome captured | +1.0 |
| Rule violation (had rule, didn't follow it) | +1.0 to existing rule |
| Session loaded, rule not triggered | -0.1 (-0.05 if proven) |
| Score drops below 1.0 | Archived |
| Score drops below 0 | Deleted |

### Graduated Trust
A rule needs confirmation in **3+ distinct sessions** to be "proven." Proven rules decay at half speed. This prevents a single lucky session from creating permanent behavior.

### Context-Aware Decay
Rules tagged with `ctx: react` only decay during React sessions. A Remotion video rule won't lose points while you're debugging Python. The SessionStart hook detects project context from your working directory automatically.

### Generalization Protocol
Every learning is generalized before capture. Claude is instructed to ask: *"If I saw a DIFFERENT task with the SAME shape, would this rule apply?"*

- **Bad**: "In user's Remotion project, measure pb-01-intro.mp3 before writing PottioBoxDemo"
- **Good**: "For any video composition with audio sync: ALWAYS measure audio durations before writing timing code"

### Rule Self-Verification
After completing a task or recovering from an error, Claude scans the playbook for rules that *should* have applied. If a rule existed but wasn't followed, that's a rule violation — the rule's score increases and the trigger context is refined.

### Structured A/B Experiments
The Capability Frontier tracks hypotheses to test. When experiments run, they use structured comparison:
```
EXPERIMENT: [hypothesis]
APPROACH A (default): [normal approach]
APPROACH B (experiment): [new approach]
METRIC: [tool calls | retries | corrections]
WINNER: [A or B] because [measured reason]
```

### Auto-Skill Generation
When 5+ rules in a single category all reach score 3.0+, Claude suggests generating a dedicated skill from them. The playbook is the nursery; graduated skills are the product.

### Memory System Integration
If claude-mem or other memory tools are available, Claude cross-references recent observations for patterns that should become playbook rules. Memory is "what happened" — the playbook is "what to do about it."

### Meta-Learning
The system tracks its own effectiveness: learning velocity per session, category strengths, blindspot detection, rule lifecycle analysis. If a category has zero rules after many sessions, frontier experiments target it.

## Installation

### From GitHub

```bash
# Add marketplace
claude plugin marketplace add OutcomeFocusAi/claude-learn

# Install plugin
claude plugin install claude-learn@outcomefocusai
```

### What happens on install

1. Plugin registers 3 hooks (UserPromptSubmit, PostToolUse, SessionStart)
2. First session: SessionStart hook creates `~/.claude/rules/playbook.md`
3. Playbook auto-loads every subsequent session
4. Learning begins immediately — zero configuration

## Usage

**You don't need to do anything.** Claude learns automatically and silently. The system is invisible by default.

### `/learn` — Manual Dashboard

```
/learn           — Full review: stats, signals, session scan, auto-skill check
/learn status    — Quick stats only
/learn add "X"   — Manually add a learning (score 2.0)
/learn frontier  — View/manage capability frontier
/learn prune     — Force pruning pass (merge similar, archive weak)
/learn meta      — Meta-learning analysis (velocity, blindspots, categories)
/learn export    — Shareable format (all files, scores reset to 1.0)
/learn signals   — View raw hook signals
/learn reset     — Archive everything, start fresh
```

## Files Created

| File | Purpose | Auto-loaded? |
|------|---------|-------------|
| `~/.claude/rules/playbook.md` | Scored behavioral rules + protocol | **Yes** (every session) |
| `~/.claude/playbook-archive.jsonl` | Decayed/pruned rules | No |
| `~/.claude/.learning-signals.jsonl` | Pending signals from hooks | No |
| `~/.claude/.learning-retries.json` | Retry/churn tracker | No (reset each session) |

## Token Budget

The playbook stays under **5,000 tokens** (~40-60 rules). When it exceeds budget, lowest-scored rules are automatically archived. Context-aware decay ensures rules only lose points when they're relevant. Proven rules decay at half speed.

## FAQ

**Will this slow down my sessions?**
No. Hooks complete in <200ms. Learning captures cost ~300 tokens each. Even a heavy session with 10 learnings adds 3k tokens total.

**What if I close the tab?**
Learnings are written to the playbook file immediately (no batching). Anything captured survives. The hook signal file also persists — next session picks up unprocessed signals.

**Does it work across projects?**
Yes. The playbook is global. Context tags let rules specify when they apply. Context-aware decay means irrelevant rules don't lose points during unrelated work.

**How is this different from a CLAUDE.md file?**
CLAUDE.md is static instructions you write manually. The playbook is dynamic rules that Claude writes, scores, validates, and prunes automatically based on real outcomes. They're complementary.

**Can I share my learnings?**
`/learn export` outputs the complete plugin with your learned rules as seed content (scores reset to 1.0). Others install it and start with your wisdom as a baseline.

## Keywords

Claude Code plugin, self-improving AI, adaptive AI assistant, machine learning feedback loop, AI self-improvement, scored behavioral rules, Claude Code skills, continuous learning, AI optimization, Claude Code hooks, automated learning capture, AI boundary exploration, self-improving LLM, Claude Code automation, AI workflow optimization

## License

MIT — [OutcomeFocus AI](https://github.com/OutcomeFocusAi)
