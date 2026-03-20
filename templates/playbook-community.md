# Community Playbook — Collective Intelligence
<!-- Last updated: {date} | Contributors: 0 | Rules: seed | Version: 1.0 -->
<!-- This file ships with claude-learn and updates with the plugin. -->
<!-- Contribute your proven rules: /learn contribute -->

## What This Is

These are behavioral rules validated by multiple independent users across different projects. A rule that works for one person might be coincidence. A rule that works for many people across many projects is a **universal truth** about how AI coding assistants work best.

**How it grows:**
1. You use Claude. Rules accumulate in your personal playbook.
2. Rules that reach "proven" status (score 3.0+, sessions >= 3) are candidates for contribution.
3. You run `/learn contribute` → selects your proven, generalized rules → submits them.
4. Maintainers review and merge. Plugin update delivers them to all users.
5. Your Claude validates them independently. Good rules persist. Bad ones decay per-user.

**Your personal playbook takes priority.** If a community rule contradicts your personal rule, your personal rule wins. Community rules start at score 1.0 on your system and must prove themselves.

---

## Universal Rules (seed)

These are starting rules derived from patterns observed across many Claude Code sessions. They'll be validated or deprecated by real usage.

- **[1.0] read-before-edit**: Always read a file before editing it. Never assume file contents from memory or context — the file may have changed since you last saw it. (confirmed: 0 | sessions: 0 | ctx: universal)

- **[1.0] verify-paths-exist**: Before writing, editing, or referencing a file path, verify it exists. Don't construct paths from assumptions — use Glob or ls. Wrong paths waste time and create confusing errors. (confirmed: 0 | sessions: 0 | ctx: universal)

- **[1.0] test-after-change**: After making code changes, run the relevant test suite before declaring done. "It should work" is not verification. (confirmed: 0 | sessions: 0 | ctx: universal)

- **[1.0] retry-means-wrong-approach**: If you've retried the same operation 3+ times, the APPROACH is wrong, not the execution. Stop. Step back. Try something fundamentally different. (confirmed: 0 | sessions: 0 | ctx: universal)

- **[1.0] one-question-not-five**: When the user's request is ambiguous, ask ONE focused clarifying question. Don't present a menu of 5 options — it shifts the cognitive load to the user. (confirmed: 0 | sessions: 0 | ctx: universal)

- **[1.0] measure-before-assume**: When a task depends on external values (file sizes, API responses, audio durations, image dimensions), measure them first. Never estimate or hardcode. (confirmed: 0 | sessions: 0 | ctx: universal)

- **[1.0] error-message-is-the-answer**: When a command fails, read the error message carefully — it usually tells you exactly what's wrong. Don't retry the same command or guess at fixes before reading the error. (confirmed: 0 | sessions: 0 | ctx: universal)

- **[1.0] small-steps-verify-each**: For multi-step changes, make one change at a time and verify it works before proceeding. Large batched changes create cascading failures that are harder to debug than the original task. (confirmed: 0 | sessions: 0 | ctx: universal)

---

## How To Contribute

Run `/learn contribute` in Claude Code. It will:
1. Show your proven rules (score 3.0+, sessions >= 3)
2. Filter out rules with `ctx:` tags too specific to your setup
3. Generalize the wording for universal applicability
4. Format them for submission
5. Create a GitHub issue or PR on the claude-learn repo

Maintainers review for quality, dedup against existing community rules, and merge.

---

## Contribution Criteria

A community rule must be:
- **Generalized**: applies across projects, languages, and users
- **Specific enough to act on**: not "be careful" but "do X before Y because Z"
- **Validated**: proven in the contributor's personal playbook (score 3.0+, 3+ sessions)
- **Causal when possible**: explains WHY, not just WHAT
- **Not user-specific**: no personal preferences, workflow quirks, or project-specific details
