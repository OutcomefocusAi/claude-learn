#!/usr/bin/env python3
"""SessionStart hook: Initialize playbooks, apply decay, detect regressions, report status.

- Creates personal + community playbooks from templates on first run
- Applies context-aware decay (rules only lose points when relevant)
- Detects regression patterns (proven rules no longer being confirmed)
- Syncs community playbook from plugin templates on update
- Reports status line

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
COMMUNITY_FILE = RULES_DIR / "playbook-community.md"
ARCHIVE_FILE = Path.home() / ".claude" / "playbook-archive.jsonl"
SIGNAL_FILE = Path.home() / ".claude" / ".learning-signals.jsonl"
RETRY_FILE = Path.home() / ".claude" / ".learning-retries.json"
DECAY_MARKER = Path.home() / ".claude" / ".playbook-last-decay"
REGRESSION_FILE = Path.home() / ".claude" / ".playbook-regression.json"

# Template directory — relative to this script (in plugin cache)
TEMPLATE_DIR = Path(__file__).parent.parent / "templates"


def get_template(name: str) -> str:
    """Load template file, replacing {date} placeholder."""
    template_path = TEMPLATE_DIR / name
    if not template_path.exists():
        return ""
    content = template_path.read_text(encoding="utf-8")
    return content.replace("{date}", datetime.now().strftime("%Y-%m-%d"))


def create_playbook():
    """Create personal playbook from template."""
    RULES_DIR.mkdir(parents=True, exist_ok=True)
    content = get_template("playbook.md")
    if content:
        PLAYBOOK_FILE.write_text(content, encoding="utf-8")


def sync_community_playbook():
    """Sync community playbook from plugin template.
    Only overwrites if plugin version is newer (checks version comment)."""
    template_content = get_template("playbook-community.md")
    if not template_content:
        return

    if not COMMUNITY_FILE.exists():
        COMMUNITY_FILE.write_text(template_content, encoding="utf-8")
        return

    # Check if template version is newer
    existing = COMMUNITY_FILE.read_text(encoding="utf-8")
    template_ver = re.search(r'Version:\s*([\d.]+)', template_content)
    existing_ver = re.search(r'Version:\s*([\d.]+)', existing)

    if template_ver and existing_ver:
        if template_ver.group(1) > existing_ver.group(1):
            # Newer version — update but preserve any user-added scores
            COMMUNITY_FILE.write_text(template_content, encoding="utf-8")


def detect_session_context() -> set:
    """Detect context tags for current session from working directory."""
    tags = set()
    cwd = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())

    checks = {
        "react": ["package.json", "src/App.tsx", "src/App.jsx", "next.config.js", "next.config.ts"],
        "python": ["pyproject.toml", "setup.py", "requirements.txt", "Pipfile"],
        "rust": ["Cargo.toml"],
        "go": ["go.mod"],
        "remotion": ["remotion.config.ts", "remotion.config.js", "src/Root.tsx"],
        "docker": ["Dockerfile", "docker-compose.yml", "docker-compose.yaml"],
        "terraform": ["main.tf", "terraform.tfvars"],
        "node": ["package.json", "node_modules"],
        "typescript": ["tsconfig.json"],
    }

    for tag, files in checks.items():
        for f in files:
            if os.path.exists(os.path.join(cwd, f)):
                tags.add(tag)
                break

    name_hints = {
        "frontend": ["frontend", "web", "ui", "dashboard", "app"],
        "backend": ["backend", "api", "server", "service"],
        "infra": ["infra", "deploy", "terraform", "kubernetes", "k8s"],
        "video": ["remotion", "video", "media"],
    }

    dir_name = os.path.basename(cwd).lower()
    for tag, hints in name_hints.items():
        if any(h in dir_name for h in hints):
            tags.add(tag)

    return tags


def extract_rules(content: str) -> list:
    """Extract all scored rules with their metadata from playbook content."""
    rules = []
    pattern = r'\*\*\[(\d+\.?\d*)\]\s+([^*]+)\*\*:\s*(.+)'
    for match in re.finditer(pattern, content):
        score = float(match.group(1))
        name = match.group(2).strip()
        rest = match.group(3)

        confirmed = 0
        sessions = 0
        ctx_tags = set()

        cm = re.search(r'confirmed:\s*(\d+)', rest)
        if cm:
            confirmed = int(cm.group(1))
        sm = re.search(r'sessions:\s*(\d+)', rest)
        if sm:
            sessions = int(sm.group(1))
        ctm = re.search(r'ctx:\s*([^)]+)\)', rest)
        if ctm:
            ctx_tags = {t.strip() for t in ctm.group(1).split(",")}

        rules.append({
            "name": name, "score": score, "confirmed": confirmed,
            "sessions": sessions, "ctx": ctx_tags,
            "full_match": match,
        })
    return rules


def detect_regressions(rules: list) -> list:
    """Detect rules that were being confirmed but stopped.
    Returns list of regressing rule names."""
    regressions = []

    # Load previous state
    prev_state = {}
    if REGRESSION_FILE.exists():
        try:
            prev_state = json.loads(REGRESSION_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            prev_state = {}

    new_state = {}
    for rule in rules:
        name = rule["name"]
        confirmed = rule["confirmed"]
        prev = prev_state.get(name, {})
        prev_confirmed = prev.get("confirmed", 0)
        prev_stale = prev.get("stale_sessions", 0)

        if confirmed > prev_confirmed:
            # Rule is being confirmed — reset stale counter
            new_state[name] = {"confirmed": confirmed, "stale_sessions": 0}
        else:
            # Confirmed count hasn't changed
            stale = prev_stale + 1
            new_state[name] = {"confirmed": confirmed, "stale_sessions": stale}

            # If rule was previously active (confirmed >= 3) and stale for 3+ sessions
            if confirmed >= 3 and stale >= 3:
                regressions.append(name)

    REGRESSION_FILE.write_text(json.dumps(new_state), encoding="utf-8")
    return regressions


def apply_decay(session_ctx: set):
    """Apply context-aware session decay with regression detection."""
    if DECAY_MARKER.exists():
        try:
            last = float(DECAY_MARKER.read_text().strip())
            if (datetime.now(timezone.utc).timestamp() - last) < 3600:
                return False, []
        except (ValueError, OSError):
            pass

    if not PLAYBOOK_FILE.exists():
        return False, []

    content = PLAYBOOK_FILE.read_text(encoding="utf-8")
    rules = extract_rules(content)

    if not rules:
        DECAY_MARKER.write_text(str(datetime.now(timezone.utc).timestamp()))
        return False, []

    # Detect regressions before modifying
    regressions = detect_regressions(rules)

    # Apply decay — only to actual rules in Behavioral Rules section,
    # NOT to examples in the protocol documentation above it
    rules_section_start = content.find("## Behavioral Rules")
    if rules_section_start == -1:
        DECAY_MARKER.write_text(str(datetime.now(timezone.utc).timestamp()))
        return False, regressions

    pattern = r'\*\*\[(\d+\.?\d*)\]\s+'
    matches = [m for m in re.finditer(pattern, content) if m.start() >= rules_section_start]

    archived_rules = []
    new_content = content

    for match in reversed(matches):
        old_score = float(match.group(1))

        line_end = content.find("\n", match.end())
        if line_end == -1:
            line_end = len(content)
        line_text = content[match.start():line_end]

        sessions_match = re.search(r'sessions:\s*(\d+)', line_text)
        sessions = int(sessions_match.group(1)) if sessions_match else 0

        # Context-aware: skip decay for irrelevant rules
        ctx_match = re.search(r'ctx:\s*([^)]+)\)', line_text)
        if ctx_match:
            rule_tags = {t.strip() for t in ctx_match.group(1).split(",")}
            if rule_tags and session_ctx and not rule_tags.intersection(session_ctx):
                continue

        decay = 0.05 if sessions >= 3 else 0.1
        new_score = round(old_score - decay, 2)

        if new_score < 1.0:
            line_start = content.rfind("\n", 0, match.start()) + 1
            rule_text = content[line_start:line_end].strip()
            archived_rules.append({
                "rule": rule_text, "score": new_score,
                "archived": datetime.now().strftime("%Y-%m-%d"), "reason": "decay",
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

    return len(archived_rules) > 0, regressions


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

        # Sync community playbook
        sync_community_playbook()

        if not ARCHIVE_FILE.exists():
            ARCHIVE_FILE.write_text("", encoding="utf-8")

        # Clear retry tracker at session start
        if RETRY_FILE.exists():
            RETRY_FILE.unlink()

        # Detect context and apply decay
        session_ctx = detect_session_context()
        had_archives, regressions = apply_decay(session_ctx)

        entries = count_entries()
        pending = count_pending_signals()
        archived = count_archive()

        parts = []
        if created:
            parts.append("[claude-learn] Playbook initialized — learning system active")
        else:
            parts.append(f"[claude-learn] Playbook: {entries} rules | {archived} archived")

        if session_ctx:
            parts.append(f"(ctx: {', '.join(sorted(session_ctx))})")

        if had_archives:
            parts.append("| decayed rules archived")
        if regressions:
            parts.append(f"| REGRESSION: {', '.join(regressions[:3])}")
        if pending > 0:
            parts.append(f"| {pending} pending signals")

        print(" ".join(parts))

    except Exception:
        pass

    sys.exit(0)


if __name__ == "__main__":
    main()
