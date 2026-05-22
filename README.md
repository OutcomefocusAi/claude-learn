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

### Which path is right for you?

| You use... | Use this path |
|------------|---------------|
| Claude Code CLI (terminal / VS Code / JetBrains extension) | [Option A](#option-a-claude-code-cli) |
| Claude Desktop (the downloadable desktop app) | [Option B](#option-b-claude-desktop) |
| Claude Web (claude.ai in a browser) | [Option C](#option-c-claude-web) |

Mixed teams (some on CLI, some on Desktop) work fine — both paths read and write the same playbook file and push to the same team repo.

---

### Option A: Claude Code CLI

**Prerequisites:** Claude Code CLI installed and working. That's it — no Python, no Git configuration, no extra steps.

> Download Claude Code: https://claude.ai/code

```bash
# Step 1: Register the plugin source
claude plugin marketplace add OutcomeFocusAi/claude-learn

# Step 2: Install
claude plugin install claude-learn@outcomefocusai
```

Your first session automatically creates `~/.claude/rules/playbook.md` and `~/.claude/rules/playbook-community.md`. Learning begins immediately and runs silently in the background.

**To enable team sync**, see [Team Repo Setup](#team-repo-setup) below, then add one line:
```bash
# Windows (PowerShell)
'{"team_repo": "https://github.com/YOUR_ORG/YOUR_REPO.git"}' | Out-File -Encoding utf8 "$env:USERPROFILE\.claude\.claude-learn-config.json"

# Mac / Linux
echo '{"team_repo": "https://github.com/YOUR_ORG/YOUR_REPO.git"}' > ~/.claude/.claude-learn-config.json
```

---

### Option B: Claude Desktop

> **There is no server URL or address to configure.** The MCP server is a local Python process that runs on each user's machine. Claude Desktop starts and manages it automatically. You never type a URL, open a port, or configure a remote server. Each team member installs their own copy.

#### Prerequisites

Run each check before proceeding:

```bash
# Python 3.10 or later — required
python3 --version    # Mac / Linux
py --version         # Windows
# Must show 3.10.x or higher
# Not installed? Download from https://python.org/downloads
# Windows tip: check "Add Python to PATH" during install

# Git — required only if using team sync, skip if solo
git --version
# Not installed? Download from https://git-scm.com/downloads

# Claude Desktop — must be installed and up to date
# Download from https://claude.ai/download
```

#### Step 1 — Get the server file

**Option 1: Clone the full repo (recommended — includes templates)**
```bash
git clone https://github.com/OutcomeFocusAi/claude-learn.git
```

**Option 2: Download only what you need**
```bash
# Mac / Linux
mkdir -p claude-learn/mcp-server claude-learn/templates
curl -L -o claude-learn/mcp-server/server.py \
  https://raw.githubusercontent.com/OutcomeFocusAi/claude-learn/master/mcp-server/server.py
curl -L -o claude-learn/templates/playbook.md \
  https://raw.githubusercontent.com/OutcomeFocusAi/claude-learn/master/templates/playbook.md
curl -L -o claude-learn/templates/project-system-prompt.md \
  https://raw.githubusercontent.com/OutcomeFocusAi/claude-learn/master/templates/project-system-prompt.md
```

Note the **full absolute path** to `server.py` — you will need it in Step 3:
```bash
# Mac / Linux
realpath claude-learn/mcp-server/server.py
# example output: /Users/jsmith/claude-learn/mcp-server/server.py

# Windows (PowerShell)
(Get-Item "claude-learn\mcp-server\server.py").FullName
# example output: C:\Users\jsmith\claude-learn\mcp-server\server.py
```

#### Step 2 — Install the Python dependency

```bash
# Mac / Linux
pip3 install "fastmcp>=3.0.0"

# Windows
py -m pip install "fastmcp>=3.0.0"
```

Verify it installed correctly:
```bash
python3 -c "import fastmcp; print('fastmcp', fastmcp.__version__, '— OK')"  # Mac / Linux
py -c "import fastmcp; print('fastmcp', fastmcp.__version__, '— OK')"       # Windows
# Should print: fastmcp 3.x.x — OK
```

If you see `ModuleNotFoundError`, Python found a different interpreter than pip installed into. Try:
```bash
python3 -m pip install "fastmcp>=3.0.0"   # Mac / Linux
py -m pip install "fastmcp>=3.0.0"        # Windows
```

#### Step 3 — Configure Claude Desktop

Find the Claude Desktop config file for your OS:

| OS | Full path |
|----|-----------|
| **Windows** | `C:\Users\YOUR_USERNAME\AppData\Roaming\Claude\claude_desktop_config.json` |
| **Mac** | `/Users/YOUR_USERNAME/Library/Application Support/Claude/claude_desktop_config.json` |
| **Linux** | `/home/YOUR_USERNAME/.config/Claude/claude_desktop_config.json` |

The file may not exist yet — create it if needed. Open it in any text editor and add:

**Windows** — use `py` as the command and double-backslashes in the path:
```json
{
  "mcpServers": {
    "claude-learn": {
      "command": "py",
      "args": ["C:\\Users\\YOUR_USERNAME\\claude-learn\\mcp-server\\server.py"]
    }
  }
}
```

**Mac / Linux** — use `python3` as the command:
```json
{
  "mcpServers": {
    "claude-learn": {
      "command": "python3",
      "args": ["/Users/YOUR_USERNAME/claude-learn/mcp-server/server.py"]
    }
  }
}
```

> **Use the exact absolute path from Step 1.** Do not use `~`, relative paths, or environment variables — Claude Desktop does not expand them.
>
> If Claude Desktop already has other MCP servers, add `"claude-learn": { ... }` inside the existing `"mcpServers"` block alongside them — do not replace the whole file.

#### Step 4 — Create a Project in Claude Desktop

1. Open Claude Desktop
2. Click **Projects** in the left sidebar → **New Project**
3. Open [`templates/project-system-prompt.md`](templates/project-system-prompt.md) from this repo
4. Copy the full contents and paste into the project's **Custom Instructions** field
5. In the project context panel (right side), click **Add context** → select the **`playbook://current`** resource listed under `claude-learn`
6. Save the project

Every conversation you start inside this project will automatically load your playbook and follow the learning protocol.

#### Step 5 — Verify it works

1. **Quit Claude Desktop completely** and reopen it (required for config changes to take effect)
2. Open a conversation in the project you just created
3. Type: `call get_playbook and show me the first 10 lines`
4. Claude should respond with the playbook content

**If Claude says the tool isn't available:**
- Confirm the path in the config file matches exactly what `realpath` / `Get-Item` returned in Step 1
- Confirm `fastmcp` is installed for the same Python that `py` or `python3` points to
- Fully quit and reopen Claude Desktop (not just close the window)
- Check `~/.claude/.claude-learn-team.log` for error messages from the server

**To enable team sync**, see [Team Repo Setup](#team-repo-setup) below.

---

### Option C: Claude Web

**Current limitation:** The MCP server in this repo uses stdio transport — it runs as a local process started by Claude Desktop. The browser-based claude.ai interface requires MCP servers to be hosted at a publicly accessible HTTPS URL. The local server does not work directly with the web interface.

**Your options for Web users:**

**1. Switch to Claude Desktop (recommended)** — full automation, no hosting required, same team repo works for everyone.

**2. Host the MCP server** (advanced — requires a server/VM your team can reach):
```python
# Change the last line of mcp-server/server.py from:
mcp.run()
# to:
mcp.run(transport="sse", host="0.0.0.0", port=8000)
```
Your MCP server address would then be `https://your-server.com/sse`. Add authentication before exposing this — the server has access to your git credentials and playbook.

**3. Manual playbook for Web-only teams** — no automation, but you get the protocol:
- Create a Project at claude.ai
- Paste the contents of [`templates/project-system-prompt.md`](templates/project-system-prompt.md) as Custom Instructions
- Paste the contents of [`templates/playbook.md`](templates/playbook.md) after the system prompt
- Update the playbook content manually when rules accumulate

---

## Team Repo Setup

This section applies to all installation options. Configure once per team; each member then points to the same repo.

### What the repo needs

A git repository with exactly one file: **`playbook.md`**. This is the shared team playbook. All team members read and write this single file automatically — there is nothing else to manage.

**The repo must be reachable by `git clone` from each team member's machine.** Test this before configuring (see [Git Authentication](#git-authentication) below).

### Create the team repo

**Step 1:** Create a new empty repository on GitHub, GitLab, Bitbucket, or your internal git server. Name it anything (e.g. `team-playbook`). Private is fine and recommended.

**Step 2:** Seed it with the starter playbook:
```bash
git clone https://github.com/YOUR_ORG/YOUR_REPO.git
cd YOUR_REPO

# Copy the starter template from this repo
cp /path/to/claude-learn/templates/playbook.md ./playbook.md
# (or download it directly from GitHub)

git add playbook.md
git commit -m "init: team playbook"
git push
```

**Step 3:** Share the repo URL with your team. Each member adds it to their config:

```bash
# Windows (PowerShell) — creates the config file
$config = '{"team_repo": "https://github.com/YOUR_ORG/YOUR_REPO.git"}'
$config | Out-File -Encoding utf8 "$env:USERPROFILE\.claude\.claude-learn-config.json"

# Mac / Linux
echo '{"team_repo": "https://github.com/YOUR_ORG/YOUR_REPO.git"}' \
  > ~/.claude/.claude-learn-config.json
```

On first session, the client clones the repo automatically. Every session after: pulls on start, pushes on end. Rules scored higher on one machine win over lower-scored versions on others — no human arbitration needed.

### Git authentication

The server and CLI hooks call `git clone` / `git push` using your machine's existing git credentials. **Test this first** — if your terminal can push to the repo, the plugin can too:

```bash
git clone YOUR_TEAM_REPO_URL /tmp/test-clone && echo "auth OK" && rm -rf /tmp/test-clone
```

**If this fails, fix credentials before configuring the plugin:**

| Repo type | Fix |
|-----------|-----|
| **GitHub HTTPS** | Create a Personal Access Token at github.com/settings/tokens (needs `repo` scope). Use `https://TOKEN@github.com/ORG/REPO.git` as the `team_repo` URL, or run `git config --global credential.helper store` and clone once to cache |
| **GitHub SSH** | Generate an SSH key, add public key to GitHub → Settings → SSH Keys, use `git@github.com:ORG/REPO.git` as the URL. Verify with `ssh -T git@github.com` |
| **GitLab / Bitbucket** | Same pattern — HTTPS token or SSH key for your platform |
| **Self-hosted git** | Ensure the host is reachable from each machine. Use SSH or an internal HTTPS token |

> **Enterprise / VPN note:** If the team repo is behind a VPN or firewall, `git push` will fail silently when the user is off-network. The local playbook still works — rules are preserved locally and will sync the next time the user has access. No data is lost.

---

## Usage

### Claude Code CLI

**Invisible by default.** Claude learns silently in the background. Use `/learn` when you want to inspect or control what's happening.

```
/learn              Full review + interactive menu
/learn status       Quick stats: rule count, pending signals, archived
/learn add "X"      Manually add a rule at score 2.0
/learn contribute   Share proven rules with the community playbook
/learn community    View community playbook
/learn frontier     Capability experiments log
/learn workflows    Linked rule chains
/learn regress      Regression alerts (rules that stopped being confirmed)
/learn meta         Learning velocity + category analysis
/learn export       Shareable format for rules
```

### Claude Desktop (MCP tools)

Claude calls tools automatically as part of the learning protocol. You can also trigger them directly:

| Say to Claude | What happens |
|---------------|--------------|
| "What rules are you following?" | Calls `get_playbook()`, shows current rules |
| "Add a rule: always X before Y" | Calls `add_rule()` |
| "Update the score on rule X" | Calls `update_rule()` |
| "Sync your learnings to the team" | Calls `sync_now()`, pushes immediately |

---

## Files

| File | Purpose | CLI | Desktop |
|------|---------|-----|---------|
| `~/.claude/rules/playbook.md` | Team playbook — rules + protocol (shared by both transports) | Auto-loaded as rules file | Served via `playbook://current` resource |
| `~/.claude/rules/playbook-community.md` | Community seed rules | Auto-loaded | — |
| `~/.claude/.claude-learn-config.json` | Team repo URL | Read by hooks | Read by MCP server |
| `~/.claude/.claude-learn-team/` | Local git clone of team repo | CLI hooks | MCP server |
| `~/.claude/.claude-learn-team.log` | Team sync log (check here if sync fails) | Both | Both |
| `~/.claude/playbook-archive.jsonl` | Rules archived by decay | No | No |
| `~/.claude/.learning-signals.jsonl` | Raw hook signal log | No | — |
| `~/.claude/.playbook-regression.json` | Regression tracker | No | — |
| `mcp-server/server.py` | MCP server entry point for Desktop | — | Local process |
| `templates/playbook.md` | Starter playbook (auto-used on first run) | CLI + Desktop | Desktop |
| `templates/project-system-prompt.md` | Paste into Claude Desktop Project instructions | — | Required |
| `templates/playbook-community.md` | Community rules template | CLI | — |

**File paths by OS:**

| Path shown | Windows | Mac / Linux |
|------------|---------|-------------|
| `~/.claude/` | `C:\Users\USERNAME\.claude\` | `~/.claude/` |
| Claude Desktop config | `C:\Users\USERNAME\AppData\Roaming\Claude\claude_desktop_config.json` | `~/Library/Application Support/Claude/claude_desktop_config.json` |

---

## Troubleshooting

**"Tool not available" or MCP tools don't appear in Claude Desktop**
- Fully quit and reopen Claude Desktop after editing `claude_desktop_config.json`
- Confirm the path to `server.py` is absolute (no `~`, no relative paths)
- Run the path directly to check for errors: `py "C:\...\server.py"` or `python3 "/Users/.../server.py"` — it should start and wait for input
- Confirm `fastmcp` is installed: `py -c "import fastmcp"` should not error

**"No playbook found" from `get_playbook()`**
- The server auto-creates the playbook from the bundled template on first startup
- If you used Option 2 (download only), confirm `templates/playbook.md` exists at the same level as `mcp-server/`
- Check that `~/.claude/rules/` directory exists and is writable

**Git push / pull fails silently**
- Check `~/.claude/.claude-learn-team.log` for the error message
- Test git auth manually: `git clone YOUR_REPO_URL /tmp/test` — fix whatever blocks this
- On VPN-required repos: connect to VPN first, then start Claude Desktop

**Playbook at 38k cap warning**
- `add_rule()` returns a cap warning when the playbook would exceed 38,000 characters
- Ask Claude to prune low-scoring rules (score < 2.0) or archive ones not relevant to current work
- CLI users: `/learn` → review and archive low-value rules

**Team members getting different rules**
- This is expected early on — each machine's rules diverge until they sync
- Score-wins merge means the highest-scored version of each rule propagates to everyone over time
- Rules only exist on one machine don't appear for others until the next push/pull cycle

---

## FAQ

**Do I need to configure a server address or URL?**
For Claude Desktop: no. The MCP server is a local process on each user's machine — there is no network address, no port to open, no firewall rule needed. For Claude Web: yes, you would need a hosted URL (see [Option C](#option-c-claude-web)).

**Will this slow me down?**
No. CLI hooks run in under 200ms. The MCP server adds ~1s on Claude Desktop startup for the git pull, then stays resident and adds no latency to conversations.

**What if I close the tab or quit Claude Desktop?**
Learnings write to disk immediately — no batching, nothing is lost. The MCP server also pushes to the team repo on disconnect as a final flush.

**Can CLI and Desktop users share the same team repo?**
Yes. Both transports read/write `~/.claude/rules/playbook.md` and sync to the same git repo. A rule learned in a CLI session is available to a Desktop user on their next connect, and vice versa.

**Does it work without a team repo?**
Yes. Solo users (no `team_repo` in config) get the full local experience — the playbook loads, tools work, rules persist. Git sync is simply skipped. You can add the team repo config later without reinstalling anything.

**vs CLAUDE.md?**
CLAUDE.md is static instructions you write once. The playbook is dynamic — Claude writes and scores rules based on evidence, and prunes ones that stop being useful. Use both: CLAUDE.md for project-specific context, the playbook for universal behavioral patterns.

**How do I contribute rules to the community?**
CLI: run `/learn contribute`. Desktop: ask Claude "draft a contribution of my proven rules" — it formats your highest-scored rules as a GitHub issue against this repo.

**What's the 38k character limit?**
The playbook is loaded into context on every session. At ~40k characters users reported hook timeout errors. The 38k cap leaves a buffer. If you hit it, prune rules with scores below 2.0 — they haven't proven their value yet.

---

## Pair With Session Coherence

Claude Learn teaches your AI **how to work better**. [Session Coherence](https://github.com/OutcomeFocusAi/session-coherence) gives your AI **cross-tool session memory** — one chronicle shared by 9 tools (Claude Code, Cursor, Codex, Gemini, Aider, and more). Together, they give every session memory AND learning. Zero infrastructure for both.

## Keywords

Claude Code plugin, self-improving AI, adaptive AI agent, collective intelligence, community learning, scored behavioral rules, machine learning feedback loop, Claude Code skills, continuous learning, AI self-improvement, meta-learning, regression detection, causal learning, workflow generation, anticipatory execution, Claude Code hooks, AI optimization, self-improving LLM, Claude Code automation

## License

MIT — [OutcomeFocus AI](https://github.com/OutcomeFocusAi)
