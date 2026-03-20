# Community Playbook — Collective Intelligence
<!-- Last updated: {date} | Contributors: 0 | Rules: 8 seed | Version: 2.0 -->
<!-- This file ships with claude-learn and updates with the plugin. -->
<!-- Your personal playbook always takes priority over community rules. -->

## How This Works

These are behavioral rules validated by multiple independent users. The more people who validate a rule, the higher its starting score when you install it.

**Scoring based on independent validation:**

| Contributors | Your Starting Score | What It Means |
|-------------|-------------------|---------------|
| 1 (proposer only) | 1.0 | Unvalidated — must prove itself on YOUR system |
| 3+ users validated | 2.0 | Multiple independent confirmations |
| 5+ users validated | 3.0 | Widely proven — high confidence |

**Your Claude still validates independently.** A community rule at score 3.0 can still decay on YOUR system if it doesn't apply to your workflow. Your personal playbook always wins conflicts.

**How scores go UP in this file:**
1. Users run `/learn contribute` — reports their local scores on existing community rules
2. Maintainer sees 3+ users independently validate the same rule → bumps template score to 2.0
3. 5+ users validate → score becomes 3.0
4. Plugin update delivers the higher score to all new installs

This means: **every time someone validates a community rule and contributes, the rule gets stronger for everyone.**

---

## How To Contribute

```
/learn contribute
```

This does two things:
1. **Proposes your new proven rules** (score 3.0+, sessions >= 3) for community inclusion
2. **Reports your validation of existing community rules** — which ones worked for you and at what score

Both get submitted as a GitHub issue. The maintainer reviews and updates the template.

### Contribution Criteria
- **Generalized**: works across projects and languages
- **Specific**: not "be careful" but "do X before Y because Z"
- **Proven**: score 3.0+ on your system, 3+ session confirmations
- **Causal**: explains WHY when possible
- **Not user-specific**: no personal paths, tool preferences, or project details

---

## Universal Rules

### Validated by community (score reflects contributor count)

- **[1.0] read-before-edit**: Always read a file before editing it. Never assume file contents — the file may have changed. cause: stale context leads to broken edits that need multiple fix rounds. (contributors: 1 | validated_by: seed)

- **[1.0] verify-paths-exist**: Before writing, editing, or referencing a file path, verify it exists with Glob or ls. cause: constructed paths from assumptions fail silently or create files in wrong locations. (contributors: 1 | validated_by: seed)

- **[1.0] test-after-change**: After making code changes, run the relevant test suite before declaring done. cause: "it should work" is not verification — untested changes create compounding bugs. (contributors: 1 | validated_by: seed)

- **[1.0] retry-means-wrong-approach**: If you've retried the same operation 3+ times, the APPROACH is wrong, not the execution. Stop. Step back. Try something fundamentally different. cause: persistence on a wrong approach wastes more time than restarting with a new one. (contributors: 1 | validated_by: seed)

- **[1.0] one-question-not-five**: When the user's request is ambiguous, ask ONE focused clarifying question. Don't present 5 options. cause: option menus shift cognitive load to the user — they asked you to help, not to choose. (contributors: 1 | validated_by: seed)

- **[1.0] measure-before-assume**: When a task depends on external values (file sizes, API responses, durations, dimensions), measure them first. Never estimate or hardcode. cause: estimated values cause subtle bugs that are harder to debug than the original task. (contributors: 1 | validated_by: seed)

- **[1.0] error-message-is-the-answer**: When a command fails, read the error message carefully before retrying or guessing. cause: the error message usually contains the exact fix — retrying without reading it wastes time. (contributors: 1 | validated_by: seed)

- **[1.0] small-steps-verify-each**: For multi-step changes, make one change at a time and verify before proceeding. cause: batched changes create cascading failures harder to debug than the original task. (contributors: 1 | validated_by: seed)
