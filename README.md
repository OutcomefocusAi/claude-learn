# claude-learn

> **The self-improving plugin for Claude.** Claude gets measurably better every session — automatically. Works across Claude Code CLI, Claude Desktop, and Claude Web. Your proven learnings help every user. Every user's learnings help you.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Claude Code Plugin](https://img.shields.io/badge/Claude_Code-Plugin-blueviolet)]()
[![Claude Desktop](https://img.shields.io/badge/Claude_Desktop-MCP-orange)]()
[![Version](https://img.shields.io/badge/version-3.2.0-green)]()

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

### How It Works — The Full Loop

```
You use Claude normally
    ↓
Rules accumulate in your personal playbook (scored, validated)
    ↓
Rules reach "proven" status (score 3.0+, confirmed across 3+ sessions)
    ↓
Run /learn contribute
    ↓
Claude does TWO things:
    ├── 1. Proposes your new proven rules for community
    └── 2. Reports your validation scores on EXISTING community rules
            ("read-before-edit is score 4.2 on my system, confirmed 6x")
    ↓
Submitted as GitHub issue (or PR if you have write access)
    ↓
Maintainer reviews:
    ├── Merges new quality rules at score 1.0
    └── Bumps existing rules when 3+ users independently validate them
    ↓
Plugin update delivers changes to ALL users
    ↓
Community rule scores reflect real validation:
    1 contributor  → score 1.0 (unproven, must earn trust on your system)
    3+ validators  → score 2.0 (independently confirmed by multiple users)
    5+ validators  → score 3.0 (widely proven — high confidence)
```

**The key insight:** Every time someone runs `/learn contribute`, they're not just proposing new rules — they're **validating existing ones.** This is what makes community scores go UP. More users validating = higher scores = more trust for new installs.

### How to Contribute

```bash
# In Claude Code, run:
/learn contribute

# Claude will:
# 1. Show your proven rules (score 3.0+, 3+ sessions) → proposes new ones
# 2. Check your scores on existing community rules → reports validations
# 3. Strip personal details, generalize wording
# 4. Create a GitHub issue with new rules + validation report

# For repo contributors with write access:
# Edit templates/playbook-community.md directly and submit a PR
```

**You cannot modify the core plugin code.** Only the maintainer can merge changes. Contributors can only submit issues/PRs which require approval. Your contributions add value — they never risk breaking anything.

### Two Playbooks, One System

| Playbook | File | Source | Priority |
|----------|------|--------|----------|
| **Personal** | `~/.claude/rules/playbook.md` | Your sessions | **Highest** — always wins conflicts |
| **Community** | `~/.claude/rules/playbook-community.md` | All contributors | Starting point — must prove itself to YOU |

Both auto-load every session. Personal rules always take priority. Community rules start at their community-validated score (1.0 to 3.0 based on how many users confirmed them), but can still decay on YOUR system if they don't fit your workflow.

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

### Three Detection Layers (Claude Code CLI)

**Layer 1: Behavioral Protocol** — The playbook auto-loads as a rules file. Contains 19 protocol sections that instruct Claude how to capture, score, generalize, verify, and evolve learnings.

**Layer 2: Language Detection Hook** (UserPromptSubmit) — Scans every user message for corrections, frustration, and positive reinforcement. Injects `[Learning signal]` reminders.

**Layer 3: Outcome Tracking Hook** (PostToolUse) — Detects test/build/deploy results, retry patterns (3x+), edit churn (5x+), install failures, lint results.

### MCP Server (Claude Desktop / Web)

For non-CLI interfaces, the MCP server replicates the same sync loop via protocol primitives:

**Startup pull** — `git pull` runs when Claude Desktop connects to the MCP server (server starts with the app).

**Resource injection** — The playbook is exposed as `playbook://current`, pinnable to a Claude Desktop Project so rules load into every conversation automatically.

**Tool-driven capture** — Claude calls `update_rule()` and `add_rule()` directly when the behavioral protocol triggers, replacing the hook-injected reminders.

**Shutdown push + debounced push** — Any write schedules a 60s push; the server also pushes on disconnect. Equivalent to the `Stop` hook.

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

### Claude Code CLI

```bash
# Add marketplace
claude plugin marketplace add OutcomeFocusAi/claude-learn

# Install
claude plugin install claude-learn@outcomefocusai
```

First session creates both playbooks automatically. Learning begins immediately.

### Claude Desktop / Enterprise (MCP)

**1. Install the MCP server**

```bash
# Clone the repo (or just copy mcp-server/)
git clone https://github.com/OutcomeFocusAi/claude-learn.git
cd claude-learn/mcp-server
pip install -r requirements.txt
```

**2. Add to Claude Desktop config**

Edit `%APPDATA%\Claude\claude_desktop_config.json` (Windows) or `~/Library/Application Support/Claude/claude_desktop_config.json` (Mac):

```json
{
  "mcpServers": {
    "claude-learn": {
      "command": "python",
      "args": ["/absolute/path/to/claude-learn/mcp-server/server.py"]
    }
  }
}
```

Use `py` instead of `python` on Windows.

**3. Create a Project in Claude Desktop**

- Open Claude Desktop → New Project
- Paste the contents of [`templates/project-system-prompt.md`](templates/project-system-prompt.md) as the project instructions
- In the project context panel, add the `playbook://current` resource

**4. Configure team sync (optional but recommended)**

```bash
# Create config file
echo '{"team_repo": "https://github.com/YOUR_ORG/team-playbook.git"}' \
  > ~/.claude/.claude-learn-config.json
```

The team repo should contain a `playbook.md` file. On first connect the server clones it; every session thereafter pulls on start and pushes on end.

**Solo users:** skip step 4. The MCP server still serves the local playbook and all tools work — git sync is simply skipped.

---

## Usage

### Claude Code CLI

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

### Claude Desktop / Web (MCP tools)

Claude calls these tools directly as part of its behavioral protocol. You can also invoke them by asking:

| Ask Claude | What happens |
|------------|-------------|
| "What rules are you following?" | Calls `get_playbook()` |
| "Add a rule about X" | Calls `add_rule()` |
| "Sync your learnings" | Calls `sync_now()` |

## Files

| File | Purpose | CLI | Desktop |
|------|---------|-----|---------|
| `~/.claude/rules/playbook.md` | Scored rules (shared by both transports) | Auto-loaded | Via `get_playbook()` |
| `~/.claude/rules/playbook-community.md` | Community rules | Auto-loaded | — |
| `~/.claude/.claude-learn-config.json` | Team repo config | Read by hooks | Read by MCP server |
| `~/.claude/.claude-learn-team/` | Local clone of team repo | CLI hooks | MCP server |
| `~/.claude/.claude-learn-team.log` | Team sync log | Both | Both |
| `~/.claude/playbook-archive.jsonl` | Decayed rules | No | No |
| `~/.claude/.learning-signals.jsonl` | Hook signals | No | — |
| `~/.claude/.playbook-regression.json` | Regression tracker | No | — |
| `mcp-server/server.py` | MCP server for Desktop/Web | — | Entry point |
| `templates/project-system-prompt.md` | Project instructions template | — | Paste into Project |

## FAQ

**Will this slow me down?** No. CLI hooks < 200ms. MCP server adds ~1s on startup for git pull, then stays resident.

**What if I close the tab?** Learnings write immediately to disk. No batching. The MCP server also pushes on disconnect.

**Cross-project?** Yes. Context tags filter relevance. Context-aware decay handles the rest.

**vs CLAUDE.md?** CLAUDE.md is static instructions you write. The playbook is dynamic rules Claude writes, scores, and prunes based on evidence. Use both.

**How do I contribute rules?** CLI: run `/learn contribute`. Desktop: ask Claude "contribute my proven rules" — it will draft a GitHub issue using the community format.

**CLI and Desktop on the same team?** Yes. Both read/write `~/.claude/rules/playbook.md` and push to the same team git repo. A rule learned in a CLI session is available to a Desktop user on their next connect, and vice versa.

**Does the MCP server work without a team repo?** Yes. Solo users get the full playbook experience — rules load, tools work, everything syncs locally. Just skip the `team_repo` config.

---

## Pair With Session Coherence

Claude Learn teaches your AI **how to work better**. [Session Coherence](https://github.com/OutcomeFocusAi/session-coherence) gives your AI **cross-tool session memory** — one chronicle shared by 9 tools (Claude Code, Cursor, Codex, Gemini, Aider, and more). Together, they give every session memory AND learning. Zero infrastructure for both.

## Keywords

Claude Code plugin, self-improving AI, adaptive AI agent, collective intelligence, community learning, scored behavioral rules, machine learning feedback loop, Claude Code skills, continuous learning, AI self-improvement, meta-learning, regression detection, causal learning, workflow generation, anticipatory execution, Claude Code hooks, AI optimization, self-improving LLM, Claude Code automation

## License

MIT — [OutcomeFocus AI](https://github.com/OutcomeFocusAi)
