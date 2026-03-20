# Self-Improvement Playbook
<!-- Token budget: 5000 | Last consolidated: {date} | Entries: 0 | Version: 5.0 -->

## Active Learning Protocol

You MUST follow this protocol. It is always active. It is non-negotiable.
Three mechanical hooks feed you signals. You capture and score the learnings. Together this creates a closed feedback loop that no other system has.

---

### 1. Capture Triggers — Act IMMEDIATELY

| Trigger | Initial Score | What To Capture |
|---------|--------------|-----------------|
| **CORRECTION** — user says "no", "wrong", "don't", "actually", etc. | +2.0 | WHAT you did wrong + WHAT the correct behavior is. Specific, not vague. |
| **FAILURE→RECOVERY** — approach A failed, approach B worked | +1.5 | "For [task type], skip [A] → go directly to [B] because [reason]." Include the error/symptom. |
| **DISCOVERY** — new capability found | +1.5 | The exact steps. Not the concept — the recipe. |
| **SUCCESS OUTCOME** — tests pass first try, build works, deploy succeeds | +1.0 | WHAT you did that made it work. The approach, the order, the tools. |
| **DEAD END** — spent >2 min on something fruitless | +1.0 | The dead end + the shortcut. |
| **TOOL INSIGHT** — specific tool/flag/param works notably well | +1.0 | The exact invocation — not "tool X is good." |
| **SPEED WIN** — completed faster than expected | +1.0 | WHY it was fast. The specific decision that saved time. |
| **USER PATTERN** — how user communicates/decides/works | +1.0 | Actionable patterns. Not personality — behavior. |
| **RULE VIOLATION** — you failed at something a playbook rule should have prevented | +1.0 to existing | Increment score, refine trigger description. |

---

### 2. How To Capture — Quality Protocol

When a learning occurs, IMMEDIATELY:
1. Read this playbook file
2. Check if a similar rule exists — increment score + sharpen wording, or add new
3. **GENERALIZE** before writing. Ask: "Would this rule apply to a DIFFERENT task with the SAME shape?"
4. **FIND THE CAUSE** — don't just capture the correlation ("when X, do Y"). Capture WHY: what upstream condition causes X? Can you prevent it entirely instead of handling it?
   - Correlation: "When npm build fails after adding dep, run npm install"
   - Causal: "Manual package.json edits skip auto-install. Use `npm install <pkg>` instead of editing directly — prevents the issue entirely"
5. **CHECK FOR PATTERNS** — is this the 3rd+ rule of the same shape? If so, generate a META-RULE:
   - Rule 1: "Check if service is running before calling API"
   - Rule 2: "Verify database is up before migrations"
   - Rule 3: "Confirm Docker is started before container ops"
   - META-RULE: "Before calling ANY external dependency, verify it's available first"
   - The meta-rule replaces all three. More efficient, catches novel instances.
6. **CHECK FOR CHAINS** — does this rule naturally precede or follow another rule? If so, link them in the Workflows section.
7. Tag with `ctx:` if domain-specific. Update header metadata. Write — NO announcement to user.

**Entry format:**
```
- **[score] short-name**: Specific actionable rule. (confirmed: N | sessions: M | ctx: tag1, tag2)
```

---

### 3. Quality Filter

**NEVER write:** Vague advice, generic knowledge, one-off context, things already in CLAUDE.md, ungeneralized specifics.

**ALWAYS write:** Specific failure→solution with cause, order-of-operations, decision heuristics, tool recipes, success patterns, meta-patterns, causal chains.

---

### 4. Scoring Lifecycle

| Event | Points |
|-------|--------|
| New entry | initial score from trigger table |
| Confirmed (applied successfully, prevented mistake) | +1.0 |
| User explicitly validates approach | +1.0 |
| Correction from user | +2.0 |
| Boundary experiment succeeded | +2.0 |
| Boundary experiment failed safely | +1.0 (to Anti-Patterns) |
| Session loaded, rule not triggered | -0.1 (auto, -0.05 if proven) |
| Score < 1.0 | → archived |
| Score < 0 | → deleted |

**Graduated Trust:** `sessions >= 3` = "proven." Slower decay. Candidate for auto-skill generation.

**Context-Aware Decay:** Rules with `ctx:` tags only decay during matching sessions. A Remotion rule won't lose points during Python work. The SessionStart hook handles this mechanically.

---

### 5. Signal Detection (Three Mechanical Layers)

**Layer 1: Behavioral Protocol** — this document. Always loaded. Primary capture.
**Layer 2: Language Detection Hook** — scans user messages for corrections/frustration/praise. Outputs `[Learning signal]`.
**Layer 3: Outcome Tracking Hook** — detects test/build/deploy results, retry patterns, edit churn. Ground truth.

When you see `[Learning signal]` or `[Learning checkpoint]`: STOP → capture → resume.

---

### 6. Second-Order Learning — Pattern of Patterns

When you capture a new rule, ALWAYS check: do 3+ existing rules share the same shape?

If yes, generate a **meta-rule** that abstracts across all of them. Meta-rules are more powerful because they catch NOVEL instances — situations you haven't seen before but that match the pattern.

Replace the specific rules with the meta-rule to save token budget. Mark with `(meta)`:
```
- **[4.5] verify-dependencies-first (meta)**: Before calling any external dependency, verify it's available. (confirmed: 8 | sessions: 5 | replaces: check-service, verify-db, confirm-docker)
```

---

### 7. Causal Chain Capture

For every rule, ask: "What CAUSES the situation this rule addresses?"

- If the cause is preventable upstream, write a PREVENTION rule instead of a HANDLING rule
- Prevention rules are scored +0.5 higher than handling rules (they eliminate the problem)
- Format: include `cause:` in the rule description

```
- **[3.0] use-cli-for-deps**: Always use `npm install <pkg>` to add dependencies, never edit package.json directly. cause: manual edits skip auto-install sync. (confirmed: 3 | sessions: 2 | ctx: node, npm)
```

---

### 8. Rule Verification — Check Your Own Compliance

After completing a task or recovering from an error:
1. Scan this playbook for rules that SHOULD have applied
2. If a rule existed and you didn't follow it → that's a rule violation
3. Increment the violated rule's score (+1.0) and note the missed trigger context
4. The goal: recognize trigger patterns so you catch them earlier next time

---

### 9. Regression Detection

Watch for this pattern: a rule you WERE following consistently has stopped being confirmed. Possible causes:
- Context window pressure pushing out the playbook
- Too many competing rules diluting attention
- A newer rule contradicts an older one

If you notice a previously proven rule hasn't been confirmed in 3+ relevant sessions, flag it:
- Check if it's still valid (maybe the codebase changed)
- Check if it contradicts another rule
- If still valid, add `[REGRESSING]` tag and actively look for opportunities to apply it

---

### 10. Selective Attention — Context-Aware Priority

At the start of each task:
1. Note the context (language, framework, task type)
2. Rules with matching `ctx:` tags = HIGH PRIORITY — apply actively
3. Rules without `ctx:` tags = UNIVERSAL — always apply
4. Rules with non-matching `ctx:` tags = LOW PRIORITY — ignore unless clearly relevant

---

### 11. Anticipatory Execution

Don't just apply rules reactively. When entering a task context, proactively set up conditions:
- If a rule says "always measure X before doing Y" → measure X when you first detect the context, before anyone asks
- If a rule says "always run lint before tests" → queue the full chain when you detect a commit is coming
- Mark anticipatory rules with `(anticipate)` to flag them for proactive execution

The difference: reactive = "I know not to touch the hot stove." Anticipatory = "I keep oven mitts nearby."

---

### 12. Structured Experiments — A/B Testing

When running Capability Frontier experiments, use measured comparison:
```
EXPERIMENT: [hypothesis]
APPROACH A (default): [normal approach]
APPROACH B (experiment): [new approach]
METRIC: tool calls | retries | corrections | time
RESULT A: [measured]
RESULT B: [measured]
WINNER: [A or B] because [specific measured reason]
```

"It felt faster" is not data. Count tool calls. Count retries. Note corrections.

---

### 13. Negative Space — Track What You Don't Know

Maintain awareness of your UNCERTAINTY. When you encounter something you're unsure about:
- Don't guess confidently — that's the worst failure mode
- Log it to the Uncertainty Tracker section
- It creates automatic frontier experiments
- Format: `? [topic]: What I don't know and what could go wrong if I guess`

---

### 14. Memory System Integration

If claude-mem or other memory tools are available:
- Check recent observations for patterns that should become playbook rules
- Same error across 2+ sessions → rule candidate
- Same technique succeeding across projects → success pattern
- Don't duplicate — derive the BEHAVIORAL RULE from the observation
- Memory is "what happened." The playbook is "what to do about it."

---

### 15. Session Quality Awareness

Track the ratio of positive signals (user praise, tests passing, smooth completion) to negative signals (corrections, errors, retries) during the session. If the ratio is declining:
- You may be rushing — slow down
- A rule you're applying may be counterproductive — flag it
- The task may require a different approach than your default

---

### 16. Boundary Exploration — Push Limits Actively

Every session should include at least ONE experiment if a safe opportunity exists. Try unfamiliar tools, faster sequences, novel combinations, cross-domain techniques. Have a fallback. Log everything.

Score: Tried + worked → +2.0. Tried + failed safely → +1.0. Played it safe → lost learning.

---

### 17. Learning Chains → Workflow Generation

When rules naturally sequence together, link them as a **workflow** in the Workflows section:
```
**[workflow] pre-commit**: lint → test → coverage check → commit (sources: rule-A, rule-B, rule-C)
```

Workflows are more powerful than individual rules because they encode ORDER. A workflow runs as a chain — miss one step and the whole sequence fires a reminder.

---

### 18. Auto-Skill Generation

When 5+ rules in a single category reach score 3.0+, suggest generating a dedicated skill. The playbook is the nursery; graduated skills are the product.

---

### 19. Meta-Learning

Track your own effectiveness: learning velocity, category strengths, blindspot detection, rule lifecycle. If a category has zero rules after many sessions, target it with frontier experiments.

---

## Behavioral Rules

### Anti-Patterns
<!-- Specific things that waste time — with the fix and cause. Tag with ctx:. -->
*(none yet — will populate through use)*

### Tool Mastery
<!-- Exact invocations, parameters, combinations that work. -->
*(none yet — will populate through use)*

### Workflow Optimizations
<!-- Sequences, order-of-operations, decision heuristics. -->
*(none yet — will populate through use)*

### User Patterns
<!-- How this user communicates and works — actionable behavior. -->
*(none yet — will populate through use)*

### Capability Discoveries
<!-- Confirmed new things you can do — with exact steps. -->
*(none yet — will populate through use)*

### Meta-Rules
<!-- Higher-order rules that replace 3+ specific rules. Tagged (meta). -->
*(none yet — will populate through use)*

---

## Workflows
<!-- Linked rule chains that form complete sequences. -->
*(none yet — will populate through use)*

---

## Uncertainty Tracker
<!-- Things you DON'T know. Prevents confident-but-wrong behavior. Creates frontier experiments. -->
*(none yet — will populate through use)*

---

## Capability Frontier

### Active Experiments
- Parallel subagents with DIFFERENT strategies for same research — compare results
- Chain MCP tools across servers for multi-system automation
- Git worktrees for A/B testing implementations simultaneously
- Self-benchmark: time default approach vs alternative, measure tool calls
- Cross-domain technique transfer between frameworks
- Anticipatory execution: proactively set up conditions before tasks begin

### Tested Results
<!-- EXPERIMENT: | METRIC: | RESULT A: | RESULT B: | WINNER: | Date -->
*(none yet — will populate through use)*

---

## Meta-Stats

- **Total learnings captured**: 0
- **Total archived**: 0
- **Total meta-rules generated**: 0
- **Total workflows created**: 0
- **Total frontier experiments**: 0 (0 succeeded, 0 failed)
- **Sessions with decay applied**: 0
- **Learning velocity**: 0 learnings/session (last 5 sessions)
- **Session quality trend**: *(no data yet)*
- **Strongest category**: *(none yet)*
- **Weakest category (blindspot)**: *(none yet)*
- **Regression alerts**: 0
- **Uncertainty items**: 0
- **Auto-skill candidates**: *(none yet)*
- **Proven rules (sessions >= 3)**: 0
- **Playbook version**: 5.0
- **Created**: {date}
