# claude-learn

**Self-improving Claude Code.** The only plugin that closes the feedback loop — observe, capture, score, validate, prune, evolve.

Claude silently learns what works, what fails, and what's possible. Rules are scored based on real outcomes. Validated rules persist. Flukes decay. Accumulated wisdom auto-generates new skills. Every session, Claude gets measurably better.

## Why This Exists

Every other "learning" or "memory" plugin for Claude Code has the same gap: they capture observations but **never validate them**. You end up with a growing pile of unverified notes that bloat context and may or may not help.

**claude-learn closes the loop:**

```
Observe → Capture → Score → Apply → Measure → Confirm or Decay → Prune
                                         ↑                          |
                                         └──────────────────────────┘
```

## How It's Different

| Feature | claude-learn | Homunculus | codesurf-insights | claude-self-improve |
|---------|-------------|-----------|-------------------|---------------------|
| Real-time capture | **3 layers** | 1 layer | Post-session | 1 layer |
| Outcome-based learning (tool results) | **Yes** | No | No | No |
| Scored rules with decay | **Yes** | No | No | No |
| Graduated trust (multi-session) | **Yes** | No | No | No |
| Feedback loop (measure→adjust) | **Yes** | No | No | No |
| Boundary exploration protocol | **Yes** | No | No | No |
| Auto-prune to token budget | **Yes** | No | No | No |
| Auto-generate skills from patterns | **Yes** | Partial | No | No |
| Retry/churn detection | **Yes** | No | No | No |
| Generalization protocol | **Yes** | No | No | No |
| Meta-learning (learn about learning) | **Yes** | No | No | No |
| Success capture (not just failures) | **Yes** | No | No | No |

## Architecture

### Three Detection Layers

**Layer 1: Behavioral Protocol** (primary)
The playbook auto-loads as a `~/.claude/rules/` file every session. It contains detailed instructions for Claude to capture learnings immediately when they occur — corrections, failures, discoveries, success patterns, speed wins. Claude follows these because they're loaded into context, not because a hook reminds it.

**Layer 2: Language Detection Hook** (safety net — UserPromptSubmit)
Mechanically scans every user message for:
- **Corrections**: "no", "wrong", "don't", "I said", "actually"
- **Frustration**: "again?", "how many times", "you keep"
- **Positive reinforcement**: "perfect", "exactly", "nailed it"

Injects `[Learning signal]` into context. Claude can't ignore it.

**Layer 3: Outcome Tracking Hook** (ground truth — PostToolUse)
Detects actual outcomes, not language:
- **Tests**: pass/fail with counts
- **Builds**: success/failure with error context
- **Deploys**: success/failure
- **Installs**: failure detection
- **Lint**: pass/fail
- **Retry patterns**: same operation 3x+ = wrong approach
- **Edit churn**: same file edited 5x+ = unclear thinking

### Scoring System

Rules earn and lose points based on **what actually happens**:

| Event | Points |
|-------|--------|
| User correction (highest signal) | +2.0 |
| Boundary experiment succeeded | +2.0 |
| Failure→recovery captured | +1.5 |
| Capability discovery | +1.5 |
| Rule confirmed (applied, prevented mistake) | +1.0 |
| Success outcome captured | +1.0 |
| Boundary experiment failed safely | +1.0 |
| Session loaded, rule not triggered | -0.1 (-0.05 if proven) |
| Score drops below 1.0 | → Archived |
| Score drops below 0 | → Deleted |

### Graduated Trust

A rule needs `sessions >= 3` (confirmed in 3+ distinct sessions) to be considered "proven." Proven rules:
- Decay at half speed (-0.05/session instead of -0.1)
- Are prioritized in the playbook
- Are candidates for auto-skill generation

This prevents single-session flukes from becoming permanent behavior.

### Generalization Protocol

Every learning is generalized before capture. The playbook instructs Claude to ask: "If I saw a DIFFERENT task with the SAME shape, would this rule apply?" This produces rules that transfer across projects and contexts.

Bad: "In user's Remotion project, measure pb-01-intro.mp3 before writing PottioBoxDemo"
Good: "For any video composition with audio sync: ALWAYS measure audio durations before writing timing code"

### Context Tags

Rules can be tagged with `ctx:` for relevance filtering:
```
- **[3.5] measure-before-code**: Always measure audio durations before writing video composition timing. (confirmed: 5 | sessions: 3 | ctx: remotion, video, audio)
```

### Auto-Skill Generation

When 5+ rules in a single category all reach score 3.0+, Claude suggests generating a dedicated skill from them. The playbook is the nursery; skills are the graduates. This is how the system evolves new capabilities.

### Boundary Exploration

The playbook maintains a **Capability Frontier** — hypotheses about what Claude could do but hasn't tried yet. Each session, Claude looks for safe opportunities to test a hypothesis. Both successes (+2.0) and failures (+1.0 to Anti-Patterns) are valuable. Playing it safe when an opportunity exists is the real failure mode.

### Meta-Learning

The system tracks its own effectiveness:
- **Learning velocity**: rules captured per session
- **Category strength**: which areas have the most proven rules
- **Blindspot detection**: categories with zero rules after many sessions
- **Trigger analysis**: which events produce the most durable learnings
- **Rule lifecycle**: average time from creation to "proven"

## Installation

### From GitHub (recommended)

```bash
# Add marketplace
claude plugin add-marketplace outcomefocusai --source github --repo OutcomeFocusAi/claude-learn

# Install plugin
claude plugin install learn@outcomefocusai
```

### From local path

```bash
claude plugin install --from /path/to/claude-learn
```

### What happens on install

1. Plugin registers hooks (UserPromptSubmit, PostToolUse, SessionStart)
2. First session: SessionStart hook creates `~/.claude/rules/playbook.md`
3. Playbook auto-loads every subsequent session
4. Learning begins immediately — no configuration needed

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
/learn history   — Full stats and timeline
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
| `~/.claude/.learning-retries.json` | Retry/churn tracker (reset each session) | No |
| `~/.claude/.playbook-last-decay` | Decay dedup marker | No |

## Token Budget

The playbook stays under **5000 tokens** (~40-60 rules). When it exceeds budget, lowest-scored rules are automatically archived. Session decay ensures stale rules eventually drop off. Proven rules decay at half speed.

## FAQ

**Will this slow down my sessions?**
No. Hooks complete in <200ms. Learning captures cost ~300 tokens each. Even a heavy session with 10 learnings costs 3k tokens — negligible.

**What if I close the tab?**
Learnings are written to the playbook file immediately when captured (no batching). Anything captured survives tab close. The only loss is potential learnings that Claude hadn't captured yet — the hooks' signal file survives too, so next session picks up unprocessed signals.

**Does it work across projects?**
Yes. The playbook is global (`~/.claude/rules/`). Context tags let rules specify when they apply. A rule tagged `ctx: react` won't interfere with Python work.

**Can I share my playbook with someone?**
`/learn export` outputs the complete plugin with your learned rules as seed content (scores reset to 1.0). Bryan can install it and start with your wisdom as a baseline, then develop his own learnings on top.

**How is this different from claude-mem?**
claude-mem captures session memory (what happened). claude-learn captures behavioral rules (what to do differently). They're complementary — claude-mem is the diary, claude-learn is the training program.

## License

MIT — OutcomeFocus AI
