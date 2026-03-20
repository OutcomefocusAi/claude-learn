#!/usr/bin/env python3
"""PostToolUse hook: Track success AND failure outcomes mechanically.

This is NOT about user language — it's about what actually happened.
Detects: test pass/fail, build outcomes, deploy results, retry patterns,
install operations, and first-try successes.

Writes outcome signals to ~/.claude/.learning-signals.jsonl with
source="outcome" so the playbook protocol can distinguish them
from user-language signals.

Must complete in <200ms. Must always exit 0.
"""

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

SIGNAL_FILE = Path.home() / ".claude" / ".learning-signals.jsonl"
RETRY_FILE = Path.home() / ".claude" / ".learning-retries.json"

# Tools to skip entirely
SKIP_TOOLS = {
    "Read", "Glob", "Grep", "WebFetch", "WebSearch",
    "TaskList", "TaskGet", "TaskCreate", "TaskUpdate", "TaskStop", "TaskOutput",
    "AskUserQuestion", "EnterPlanMode", "ExitPlanMode",
    "ListMcpResourcesTool", "ReadMcpResourceTool",
    "Skill", "NotebookEdit", "ToolSearch",
}

# Command classification
TEST_COMMANDS = [
    "npm test", "npm run test", "npx jest", "npx vitest",
    "pytest", "python -m pytest", "py -m pytest",
    "jest", "vitest", "mocha",
    "cargo test", "go test", "dotnet test",
    "make test", "yarn test", "pnpm test",
]

BUILD_COMMANDS = [
    "npm run build", "npx tsc", "npx next build", "npx vite build",
    "cargo build", "go build", "dotnet build",
    "make build", "make", "cmake --build",
    "webpack", "rollup", "esbuild",
    "yarn build", "pnpm build",
]

DEPLOY_COMMANDS = [
    "wrangler pages deploy", "wrangler deploy", "wrangler publish",
    "npx wrangler", "vercel deploy", "netlify deploy",
    "docker push", "docker build",
    "git push", "gh pr create",
    "aws deploy", "gcloud deploy", "az deploy",
    "fly deploy", "railway deploy",
    "npm publish", "cargo publish",
]

INSTALL_COMMANDS = [
    "npm install", "npm i ", "npm ci",
    "pip install", "uv pip install", "uv add",
    "cargo add", "go get",
    "yarn add", "pnpm add",
    "brew install", "apt install", "choco install",
]

LINT_COMMANDS = [
    "eslint", "prettier", "ruff", "black", "flake8",
    "clippy", "golint", "rubocop",
    "npm run lint", "yarn lint",
]

TRIVIAL_BASH = {
    "ls", "dir", "pwd", "cd", "echo", "cat", "head", "tail",
    "date", "whoami", "which", "where", "where.exe", "test",
    "true", "false", "wc", "sort", "uniq", "diff", "type",
    "set", "export", "env", "printenv", "mkdir",
}

READ_PREFIXES = [
    "grep ", "rg ", "find ", "git log", "git status", "git diff",
    "git show", "git branch", "git remote", "nssm status",
    "tasklist", "netstat", "ipconfig", "systeminfo",
    "nvidia-smi", "wmic ", "docker ps", "docker logs",
]


def classify_command(cmd_lower: str) -> tuple[str, list]:
    """Classify a bash command and return (category, matched_commands)."""
    for cmd in TEST_COMMANDS:
        if cmd in cmd_lower:
            return ("test", [cmd])
    for cmd in BUILD_COMMANDS:
        if cmd in cmd_lower:
            return ("build", [cmd])
    for cmd in DEPLOY_COMMANDS:
        if cmd in cmd_lower:
            return ("deploy", [cmd])
    for cmd in INSTALL_COMMANDS:
        if cmd in cmd_lower:
            return ("install", [cmd])
    for cmd in LINT_COMMANDS:
        if cmd in cmd_lower:
            return ("lint", [cmd])
    return ("other", [])


def extract_bash_outcome(tool_input: dict, tool_response) -> dict | None:
    """Detect success/failure patterns in bash command outcomes."""
    command = ""
    if isinstance(tool_input, dict):
        command = tool_input.get("command", "")
    elif isinstance(tool_input, str):
        command = tool_input

    if not command or len(command.strip()) < 5:
        return None

    cmd_lower = command.strip().lower()

    # Skip trivial and read-only commands
    first_word = cmd_lower.split()[0].strip("'\"")
    if first_word in TRIVIAL_BASH:
        return None
    for rp in READ_PREFIXES:
        if cmd_lower.startswith(rp):
            return None

    # Extract exit code and output
    exit_code = 0
    stdout = ""
    stderr = ""
    if isinstance(tool_response, dict):
        for key in ("exitCode", "exit_code", "code", "returnCode"):
            val = tool_response.get(key)
            if val is not None:
                try:
                    exit_code = int(val)
                except (ValueError, TypeError):
                    pass
                break
        if exit_code == 0 and tool_response.get("success") is False:
            exit_code = 1
        stderr = str(tool_response.get("stderr", ""))[:500]
        stdout = str(tool_response.get("stdout",
                     tool_response.get("output",
                     tool_response.get("content", ""))))[:500]
    elif isinstance(tool_response, str):
        stdout = tool_response[:500]

    combined = (stdout + " " + stderr).lower()
    category, _ = classify_command(cmd_lower)

    if category == "test":
        if exit_code == 0 and any(w in combined for w in ["pass", "passed", "ok", "success", "✓", "✔"]):
            # Count test results if available
            test_count = ""
            count_match = re.search(r'(\d+)\s*(?:pass|passed|tests?\s+pass)', combined)
            if count_match:
                test_count = f" ({count_match.group(0).strip()})"
            return {
                "type": "success", "category": "test_pass", "severity": "normal",
                "message_preview": f"Tests passed{test_count}: `{command[:100]}`",
                "source": "outcome",
            }
        elif exit_code != 0:
            fail_detail = ""
            fail_match = re.search(r'(\d+)\s*(?:fail|failed)', combined)
            if fail_match:
                fail_detail = f" ({fail_match.group(0).strip()})"
            return {
                "type": "failure", "category": "test_fail", "severity": "high",
                "message_preview": f"Tests failed{fail_detail}: `{command[:100]}` — {(stderr or stdout)[:150]}",
                "source": "outcome",
            }

    elif category == "build":
        if exit_code == 0:
            return {
                "type": "success", "category": "build_pass", "severity": "normal",
                "message_preview": f"Build succeeded: `{command[:100]}`",
                "source": "outcome",
            }
        else:
            return {
                "type": "failure", "category": "build_fail", "severity": "high",
                "message_preview": f"Build failed: `{command[:100]}` — {(stderr or stdout)[:150]}",
                "source": "outcome",
            }

    elif category == "deploy":
        if exit_code == 0:
            return {
                "type": "success", "category": "deploy_pass", "severity": "normal",
                "message_preview": f"Deploy succeeded: `{command[:100]}`",
                "source": "outcome",
            }
        else:
            return {
                "type": "failure", "category": "deploy_fail", "severity": "high",
                "message_preview": f"Deploy failed: `{command[:100]}` — {(stderr or stdout)[:150]}",
                "source": "outcome",
            }

    elif category == "install":
        if exit_code != 0:
            return {
                "type": "failure", "category": "install_fail", "severity": "high",
                "message_preview": f"Install failed: `{command[:100]}` — {(stderr or stdout)[:150]}",
                "source": "outcome",
            }

    elif category == "lint":
        if exit_code != 0:
            return {
                "type": "failure", "category": "lint_fail", "severity": "normal",
                "message_preview": f"Lint errors: `{command[:100]}` — {(stderr or stdout)[:150]}",
                "source": "outcome",
            }
        elif exit_code == 0:
            return {
                "type": "success", "category": "lint_pass", "severity": "normal",
                "message_preview": f"Lint clean: `{command[:100]}`",
                "source": "outcome",
            }

    # General errors for non-trivial commands
    if exit_code != 0 and category == "other":
        # Check for heuristic errors in output too
        error_indicators = [
            "error:", "fatal:", "traceback", "exception",
            "command not found", "permission denied",
            "no such file", "failed to", "enoent", "eacces",
        ]
        has_error = exit_code != 0 or any(ind in combined for ind in error_indicators)

        if has_error:
            return {
                "type": "failure", "category": "command_error", "severity": "normal",
                "message_preview": f"Command failed (exit {exit_code}): `{command[:100]}` — {(stderr or stdout)[:150]}",
                "source": "outcome",
            }

    return None


def track_retries(tool_name: str, tool_input: dict) -> dict | None:
    """Detect retry patterns — same tool+target called multiple times = struggling."""
    try:
        fingerprint = tool_name
        if tool_name == "Bash":
            cmd = tool_input.get("command", "") if isinstance(tool_input, dict) else str(tool_input)
            words = cmd.strip().split()[:3]
            fingerprint = f"Bash:{' '.join(words)}"
        elif tool_name in ("Edit", "Write"):
            fp = tool_input.get("file_path", "") if isinstance(tool_input, dict) else ""
            fingerprint = f"{tool_name}:{Path(fp).name}"

        retries = {}
        if RETRY_FILE.exists():
            try:
                retries = json.loads(RETRY_FILE.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                retries = {}

        count = retries.get(fingerprint, 0) + 1
        retries[fingerprint] = count

        if len(retries) > 50:
            retries = dict(list(retries.items())[-25:])

        RETRY_FILE.write_text(json.dumps(retries), encoding="utf-8")

        if count == 3:
            return {
                "type": "retry_pattern", "category": "struggling", "severity": "high",
                "message_preview": f"Retried `{fingerprint}` {count}x — likely wrong approach, not wrong execution",
                "source": "outcome",
            }
        elif count == 5:
            return {
                "type": "retry_pattern", "category": "dead_end", "severity": "high",
                "message_preview": f"Retried `{fingerprint}` {count}x — STOP. This approach is a dead end. Try something fundamentally different.",
                "source": "outcome",
            }

    except Exception:
        pass

    return None


def track_edit_churn(tool_name: str, tool_input: dict) -> dict | None:
    """Detect editing the same file repeatedly — potential sign of unclear approach."""
    if tool_name not in ("Edit", "Write"):
        return None

    try:
        fp = tool_input.get("file_path", "") if isinstance(tool_input, dict) else ""
        if not fp:
            return None

        fingerprint = f"edit:{Path(fp).name}"
        retries = {}
        if RETRY_FILE.exists():
            try:
                retries = json.loads(RETRY_FILE.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                retries = {}

        count = retries.get(fingerprint, 0) + 1
        retries[fingerprint] = count
        RETRY_FILE.write_text(json.dumps(retries), encoding="utf-8")

        if count == 5:
            return {
                "type": "edit_churn", "category": "struggling", "severity": "normal",
                "message_preview": f"Edited `{Path(fp).name}` {count}x this session — consider stepping back to rethink approach",
                "source": "outcome",
            }
    except Exception:
        pass

    return None


def main():
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            sys.exit(0)

        data = json.loads(raw)
        tool_name = data.get("tool_name", "")

        if tool_name in SKIP_TOOLS:
            sys.exit(0)

        tool_input = data.get("tool_input", {})
        tool_response = data.get("tool_response", {})

        signals = []

        if tool_name == "Bash":
            outcome = extract_bash_outcome(tool_input, tool_response)
            if outcome:
                signals.append(outcome)

        # Track retries for all non-skipped tools
        retry = track_retries(tool_name, tool_input)
        if retry:
            signals.append(retry)

        # Track edit churn
        churn = track_edit_churn(tool_name, tool_input)
        if churn:
            signals.append(churn)

        if signals:
            SIGNAL_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(SIGNAL_FILE, "a", encoding="utf-8") as f:
                for sig in signals:
                    sig["timestamp"] = datetime.now(timezone.utc).isoformat()
                    f.write(json.dumps(sig) + "\n")

            for sig in signals:
                if sig["severity"] == "high":
                    if sig["type"] == "retry_pattern":
                        print(f"[Learning signal: {sig['category']} — {sig['message_preview'][:100]}]")
                    elif sig["type"] == "failure":
                        print(f"[Learning signal: {sig['category']} — capture what went wrong and the fix]")

    except Exception:
        pass

    sys.exit(0)


if __name__ == "__main__":
    main()
