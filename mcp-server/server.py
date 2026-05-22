#!/usr/bin/env python3
"""
claude-learn MCP server — Claude Desktop and Web support.

Provides the same team playbook sync as the CLI hooks, via MCP protocol:
  - Startup:  git pull from team repo, merge into local playbook
  - Resource: playbook://current — injectable in Claude Desktop Projects
  - Tools:    get_playbook, update_rule, add_rule, sync_now
  - Shutdown: git push local changes back to team repo
  - Writes:   debounced 60s push after any rule update

Works with Claude Desktop (stdio transport) and any MCP-compatible client.
Silent on all failures — never disrupts a session.

Config: ~/.claude/.claude-learn-config.json  →  {"team_repo": "https://..."}
Solo users (no team_repo): resource and tools still work, git sync is skipped.
"""

import json
import re
import socket
import subprocess
import threading
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path

from fastmcp import FastMCP

# ── Constants (identical to CLI hooks) ────────────────────────────────────────
PLAYBOOK_FILE = Path.home() / ".claude" / "rules" / "playbook.md"
CONFIG_FILE   = Path.home() / ".claude" / ".claude-learn-config.json"
TEAM_DIR      = Path.home() / ".claude" / ".claude-learn-team"
TEAM_LOG      = Path.home() / ".claude" / ".claude-learn-team.log"
SIZE_LIMIT    = 38_000


# ── Config & Logging ──────────────────────────────────────────────────────────

def load_config() -> dict:
    if not CONFIG_FILE.exists():
        return {}
    try:
        return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def log_team(msg: str) -> None:
    try:
        with open(TEAM_LOG, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [mcp] {msg}\n")
    except OSError:
        pass


# ── Playbook ops (mirrors CLI hooks — single source of behaviour) ─────────────

def extract_rules_as_dict(content: str) -> dict:
    """Return {name: (score, full_line)} for every scored rule in Behavioral Rules section."""
    result = {}
    start = content.find("## Behavioral Rules")
    if start == -1:
        return result
    pattern = r'\*\*\[(\d+\.?\d*)\]\s+([^*]+)\*\*:'
    for m in re.finditer(pattern, content[start:]):
        score      = float(m.group(1))
        name       = m.group(2).strip()
        abs_pos    = start + m.start()
        line_start = content.rfind('\n', 0, abs_pos) + 1
        line_end   = content.find('\n', abs_pos)
        if line_end == -1:
            line_end = len(content)
        result[name] = (score, content[line_start:line_end])
    return result


def merge_playbooks(local_content: str, remote_content: str) -> str:
    """Score-wins merge: higher score keeps; local-only rules appended before Workflows."""
    local_rules  = extract_rules_as_dict(local_content)
    remote_rules = extract_rules_as_dict(remote_content)
    result = remote_content

    for name, (local_score, local_line) in local_rules.items():
        if name in remote_rules:
            remote_score, remote_line = remote_rules[name]
            if local_score > remote_score:
                result = result.replace(remote_line, local_line, 1)

    new_lines = [line for name, (_, line) in local_rules.items()
                 if name not in remote_rules]
    if new_lines:
        markers = ["## Workflows", "## Uncertainty Tracker",
                   "## Capability Frontier", "## Meta-Stats"]
        insert_pos = len(result)
        for marker in markers:
            pos = result.find(f"\n{marker}")
            if pos != -1:
                insert_pos = pos
                break
        result = result[:insert_pos] + "\n" + "\n".join(new_lines) + result[insert_pos:]

    return result


# ── Git sync ──────────────────────────────────────────────────────────────────

def git_pull() -> None:
    """Pull (or clone) team repo and merge into local playbook. Silent on failure."""
    config   = load_config()
    repo_url = config.get("team_repo", "").strip()
    if not repo_url:
        return

    try:
        if not TEAM_DIR.exists():
            r = subprocess.run(
                ["git", "clone", "--depth=1", repo_url, str(TEAM_DIR)],
                capture_output=True, text=True, timeout=30,
            )
            if r.returncode != 0:
                log_team(f"clone failed: {r.stderr[:200]}")
                return
            log_team(f"cloned {repo_url}")
        else:
            r = subprocess.run(
                ["git", "-C", str(TEAM_DIR), "pull", "--rebase", "--quiet"],
                capture_output=True, text=True, timeout=10,
            )
            if r.returncode != 0:
                log_team(f"pull failed: {r.stderr[:200]}")

        team_playbook = TEAM_DIR / "playbook.md"
        if not team_playbook.exists() or not PLAYBOOK_FILE.exists():
            return

        remote_content = team_playbook.read_text(encoding="utf-8")
        local_content  = PLAYBOOK_FILE.read_text(encoding="utf-8")
        merged = merge_playbooks(local_content, remote_content)

        if len(merged) > SIZE_LIMIT:
            merged = merged[:SIZE_LIMIT]
            log_team(f"pull ok (truncated to {SIZE_LIMIT} chars)")
        else:
            log_team("pull ok")

        PLAYBOOK_FILE.write_text(merged, encoding="utf-8")

    except subprocess.TimeoutExpired:
        log_team("pull timed out")
    except Exception as e:
        log_team(f"pull error: {e}")


def git_push() -> None:
    """Merge local changes into team repo and push. Silent on failure."""
    config   = load_config()
    repo_url = config.get("team_repo", "").strip()
    if not repo_url or not TEAM_DIR.exists() or not PLAYBOOK_FILE.exists():
        return

    try:
        local_content = PLAYBOOK_FILE.read_text(encoding="utf-8")

        r = subprocess.run(
            ["git", "-C", str(TEAM_DIR), "pull", "--rebase", "--quiet"],
            capture_output=True, text=True, timeout=10,
        )
        if r.returncode != 0:
            log_team(f"pre-push pull failed: {r.stderr[:200]}")

        team_playbook  = TEAM_DIR / "playbook.md"
        remote_content = team_playbook.read_text(encoding="utf-8") if team_playbook.exists() else ""
        merged = merge_playbooks(local_content, remote_content) if remote_content else local_content

        if len(merged) > SIZE_LIMIT:
            log_team(f"push skipped: {len(merged)} chars exceeds {SIZE_LIMIT} cap")
            return

        team_playbook.write_text(merged, encoding="utf-8")
        PLAYBOOK_FILE.write_text(merged, encoding="utf-8")

        subprocess.run(
            ["git", "-C", str(TEAM_DIR), "add", "playbook.md"],
            capture_output=True, text=True, timeout=5,
        )
        hostname = socket.gethostname()
        r = subprocess.run(
            ["git", "-C", str(TEAM_DIR), "commit", "--quiet", "-m",
             f"sync: [{hostname}] {datetime.now().strftime('%Y-%m-%d %H:%M')}"],
            capture_output=True, text=True, timeout=5,
        )
        if "nothing to commit" in (r.stdout + r.stderr):
            log_team("nothing to push")
            return

        r = subprocess.run(
            ["git", "-C", str(TEAM_DIR), "push", "--quiet"],
            capture_output=True, text=True, timeout=15,
        )
        log_team("pushed ok" if r.returncode == 0 else f"push failed: {r.stderr[:200]}")

    except subprocess.TimeoutExpired:
        log_team("push timed out")
    except Exception as e:
        log_team(f"push error: {e}")


# ── Debounced push ────────────────────────────────────────────────────────────

_push_timer: threading.Timer | None = None
_push_lock  = threading.Lock()


def schedule_push() -> None:
    """Schedule a git push 60s after the last write. Resets the timer on each call."""
    global _push_timer
    with _push_lock:
        if _push_timer and _push_timer.is_alive():
            _push_timer.cancel()
        _push_timer = threading.Timer(60.0, git_push)
        _push_timer.daemon = True
        _push_timer.start()


def flush_push() -> None:
    """Cancel debounce timer and push immediately (used on shutdown)."""
    global _push_timer
    with _push_lock:
        if _push_timer and _push_timer.is_alive():
            _push_timer.cancel()
            _push_timer = None
    git_push()


# ── Server lifecycle ──────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(server: FastMCP):
    git_pull()      # sync on connect
    yield
    flush_push()    # push on disconnect


mcp = FastMCP(
    name="claude-learn",
    instructions=(
        "Manages a shared team playbook of scored behavioral rules. "
        "Call get_playbook() at session start to load the protocol and rules. "
        "Call update_rule() or add_rule() when the protocol triggers a capture. "
        "Call sync_now() when the user signals the session is ending."
    ),
    lifespan=lifespan,
)


# ── Resource ──────────────────────────────────────────────────────────────────

@mcp.resource(
    uri="playbook://current",
    name="Team Playbook",
    description="Shared behavioral rules and learning protocol.",
    mime_type="text/markdown",
)
def playbook_resource() -> str:
    if PLAYBOOK_FILE.exists():
        return PLAYBOOK_FILE.read_text(encoding="utf-8")
    return (
        "# Playbook\n\nNo playbook found. "
        "See https://github.com/OutcomeFocusAi/claude-learn for setup instructions."
    )


# ── Tools ─────────────────────────────────────────────────────────────────────

@mcp.tool
def get_playbook() -> str:
    """
    Load the current team playbook (behavioral rules + learning protocol).
    Call this at the start of every session before doing any work.
    """
    if not PLAYBOOK_FILE.exists():
        return (
            "No playbook found. "
            "See https://github.com/OutcomeFocusAi/claude-learn for setup."
        )
    content = PLAYBOOK_FILE.read_text(encoding="utf-8")
    return f"[playbook: {len(content)} chars]\n\n{content}"


@mcp.tool
def update_rule(rule_name: str, new_full_line: str) -> str:
    """
    Update an existing rule's score or description.

    Args:
        rule_name:     Exact name as it appears in **[score] rule-name**: format.
        new_full_line: Complete replacement line including score, name, body, and metadata.
                       Example: - **[3.5] rule-name**: Updated description. (confirmed: 4 | sessions: 3)
    """
    if not PLAYBOOK_FILE.exists():
        return "Error: playbook not found."

    content = PLAYBOOK_FILE.read_text(encoding="utf-8")
    rules   = extract_rules_as_dict(content)

    if rule_name not in rules:
        return f"Rule '{rule_name}' not found. Use add_rule() to create it."

    _, old_line = rules[rule_name]
    new_content = content.replace(old_line, new_full_line, 1)

    if len(new_content) > SIZE_LIMIT:
        return f"Rejected: would exceed {SIZE_LIMIT} char cap. Prune low-scoring rules first."

    PLAYBOOK_FILE.write_text(new_content, encoding="utf-8")
    schedule_push()
    return f"Updated '{rule_name}'."


@mcp.tool
def add_rule(section: str, rule_line: str) -> str:
    """
    Add a new rule to the playbook.

    Args:
        section:   Subsection to add to. One of:
                   Anti-Patterns | Tool Mastery | Workflow Optimizations |
                   User Patterns | Capability Discoveries | Meta-Rules
        rule_line: Complete rule line.
                   Example: - **[2.0] rule-name**: Description. cause: reason. (confirmed: 1 | sessions: 1)
    """
    if not PLAYBOOK_FILE.exists():
        return "Error: playbook not found."

    content = PLAYBOOK_FILE.read_text(encoding="utf-8")

    # Guard: reject if rule name already exists
    name_match = re.search(r'\*\*\[[\d.]+\]\s+([^*]+)\*\*:', rule_line)
    if name_match:
        candidate = name_match.group(1).strip()
        if candidate in extract_rules_as_dict(content):
            return f"Rule '{candidate}' already exists. Use update_rule() instead."

    # Find subsection
    section_pos = content.find(f"### {section}")
    if section_pos == -1:
        valid = (
            "Anti-Patterns, Tool Mastery, Workflow Optimizations, "
            "User Patterns, Capability Discoveries, Meta-Rules"
        )
        return f"Section '### {section}' not found. Valid sections: {valid}"

    # Insert before next heading
    after_header  = section_pos + len(f"### {section}")
    next_heading  = re.search(r'\n(###|##) ', content[after_header:])
    insert_pos    = after_header + next_heading.start() if next_heading else len(content)

    new_content = content[:insert_pos] + "\n" + rule_line + content[insert_pos:]

    if len(new_content) > SIZE_LIMIT:
        return (
            f"Rejected: would reach {len(new_content)} chars (cap {SIZE_LIMIT}). "
            "Prune low-scoring rules first."
        )

    PLAYBOOK_FILE.write_text(new_content, encoding="utf-8")
    schedule_push()
    return f"Added rule to '{section}'."


@mcp.tool
def sync_now() -> str:
    """
    Push local playbook changes to the team repo immediately.
    Call this when the user signals the session is ending.
    """
    config = load_config()
    if not config.get("team_repo"):
        return (
            "No team repo configured. "
            'Add {"team_repo": "<git-url>"} to ~/.claude/.claude-learn-config.json.'
        )
    git_push()
    return "Synced to team repo."


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    mcp.run()
