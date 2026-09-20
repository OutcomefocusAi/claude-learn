# Claude Learn — Session Protocol

You have the **claude-learn** MCP server connected. It manages a shared team playbook of scored behavioral rules that persist and improve across every session.

## Required: Session Start

**Call `get_playbook()` before doing anything else in this conversation.** Read the full content it returns. The playbook contains:

1. **Active Learning Protocol** (19 sections) — your complete operating instructions for how to capture, score, generalize, and evolve rules
2. **Behavioral Rules** — your team's currently validated rules to follow right now

Follow both exactly. The protocol inside the playbook is your primary guide.

## Capturing Learnings

The protocol defines when to capture. The core triggers:

| Signal | Score | What to capture |
|--------|-------|-----------------|
| User correction ("no", "wrong", "don't", "actually") | +2.0 | What you did wrong + correct behavior |
| Approach A failed, approach B worked | +1.5 | Skip A → go directly to B, with reason |
| New capability or tool works notably well | +1.5 | Exact steps — the recipe, not the concept |
| Tests pass, build succeeds, clean completion | +1.0 | What made it work — approach, order, tools |

When triggered, call immediately (don't wait):
- **Existing rule** — update score or description: `update_rule(rule_name, new_full_line)`
- **New rule**: `add_rule(section, rule_line)`

**Rule format:**
```
- **[score] rule-name**: Specific actionable description. cause: why this matters. (confirmed: N | sessions: M | ctx: tag)
```

**Sections:** Anti-Patterns | Tool Mastery | Workflow Optimizations | User Patterns | Capability Discoveries | Meta-Rules

## Session End

When the user signals they are done ("that's all", "done for now", "thanks", "bye"), call `sync_now()` to push changes to the shared team repo. Every team member gets your learnings on their next session.

## Notes

- Rules below score 1.0 are automatically archived — low scores are fine for new rules, they earn their place
- If `add_rule()` or `update_rule()` returns a cap warning, prune low-scoring rules before adding more
- Score wins on merge: if you and a teammate both update the same rule, the higher score is kept
