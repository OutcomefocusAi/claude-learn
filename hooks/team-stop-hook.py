#!/usr/bin/env python3
"""Stop hook: Push local playbook changes to the team repo.

Runs at session end. Pulls latest from team repo, merges with local
(score wins for overlapping rules, local-only rules are appended),
then commits and pushes. Silent on all failures — never disrupts the session.

Must always exit 0.
"""

import json
import re
import socket
import subprocess
import sys
from datetime import datetime
from pathlib import Path

PLAYBOOK_FILE = Path.home() / ".claude" / "rules" / "playbook.md"
CONFIG_FILE = Path.home() / ".claude" / ".claude-learn-config.json"
TEAM_DIR = Path.home() / ".claude" / ".claude-learn-team"
TEAM_LOG = Path.home() / ".claude" / ".claude-learn-team.log"
SIZE_LIMIT = 38_000


def load_config() -> dict:
    if not CONFIG_FILE.exists():
        return {}
    try:
        return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def log_team(msg: str):
    try:
        with open(TEAM_LOG, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [stop] {msg}\n")
    except OSError:
        pass


def extract_rules_as_dict(content: str) -> dict:
    """Extract scored rules from Behavioral Rules section as {name: (score, full_line)}."""
    result = {}
    rules_start = content.find("## Behavioral Rules")
    if rules_start == -1:
        return result
    rules_content = content[rules_start:]
    pattern = r'\*\*\[(\d+\.?\d*)\]\s+([^*]+)\*\*:'
    for match in re.finditer(pattern, rules_content):
        score = float(match.group(1))
        name = match.group(2).strip()
        abs_pos = rules_start + match.start()
        line_start = content.rfind('\n', 0, abs_pos) + 1
        line_end = content.find('\n', abs_pos)
        if line_end == -1:
            line_end = len(content)
        full_line = content[line_start:line_end]
        result[name] = (score, full_line)
    return result


def merge_playbooks(local_content: str, remote_content: str) -> str:
    """Merge local playbook into remote. Score wins for overlapping rules.
    Local-only rules are appended before the Workflows section."""
    local_rules = extract_rules_as_dict(local_content)
    remote_rules = extract_rules_as_dict(remote_content)

    result = remote_content

    for name, (local_score, local_line) in local_rules.items():
        if name in remote_rules:
            remote_score, remote_line = remote_rules[name]
            if local_score > remote_score:
                result = result.replace(remote_line, local_line, 1)

    new_lines = [
        line for name, (_, line) in local_rules.items()
        if name not in remote_rules
    ]
    if new_lines:
        markers = ["## Workflows", "## Uncertainty Tracker", "## Capability Frontier", "## Meta-Stats"]
        insert_pos = len(result)
        for marker in markers:
            pos = result.find(f"\n{marker}")
            if pos != -1:
                insert_pos = pos
                break
        result = result[:insert_pos] + "\n" + "\n".join(new_lines) + result[insert_pos:]

    return result


def push_to_team_repo(config: dict):
    repo_url = config.get("team_repo", "").strip()
    if not repo_url or not TEAM_DIR.exists() or not PLAYBOOK_FILE.exists():
        return

    try:
        local_content = PLAYBOOK_FILE.read_text(encoding="utf-8")

        # Pull latest before merging to avoid push conflicts
        r = subprocess.run(
            ["git", "-C", str(TEAM_DIR), "pull", "--rebase", "--quiet"],
            capture_output=True, text=True, timeout=10,
        )
        if r.returncode != 0:
            log_team(f"pre-push pull failed: {r.stderr[:200]}")

        # Merge local into the now-current remote
        team_playbook = TEAM_DIR / "playbook.md"
        if team_playbook.exists():
            remote_content = team_playbook.read_text(encoding="utf-8")
            merged = merge_playbooks(local_content, remote_content)
        else:
            merged = local_content

        # Enforce 38k cap — skip push if over limit
        if len(merged) > SIZE_LIMIT:
            log_team(f"push skipped: merged content {len(merged)} chars exceeds {SIZE_LIMIT} cap")
            print(f"[claude-learn] Team sync skipped: playbook at {len(merged)} chars, over 38k cap. Prune rules to re-enable.")
            return

        # Write merged result to both locations
        team_playbook.write_text(merged, encoding="utf-8")
        PLAYBOOK_FILE.write_text(merged, encoding="utf-8")

        # Commit
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
            log_team("nothing new to push")
            return

        # Push
        r = subprocess.run(
            ["git", "-C", str(TEAM_DIR), "push", "--quiet"],
            capture_output=True, text=True, timeout=15,
        )
        if r.returncode == 0:
            log_team("pushed ok")
        else:
            log_team(f"push failed: {r.stderr[:200]}")

    except subprocess.TimeoutExpired:
        log_team("push timed out")
    except Exception as e:
        log_team(f"push error: {e}")


def main():
    try:
        config = load_config()
        if config.get("team_repo"):
            push_to_team_repo(config)
    except Exception:
        pass
    sys.exit(0)


if __name__ == "__main__":
    main()
