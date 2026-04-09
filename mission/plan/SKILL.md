---
name: mission:plan
description: >-
  Interactive mission planning — research the codebase, ask clarifying questions,
  decompose work into milestones with acceptance criteria, and save an approved plan.
  Start here before /mission:start. Invoke with /mission:plan <task description>.
argument-hint: "<task description>"
effort: high
---

# Mission Planning — The Orientation Phase

> "Orientation is the Schwerpunkt. It shapes the way we interact with the environment — hence orientation shapes the way we observe, the way we decide, the way we act." — John Boyd

You are entering the **Orientation** phase — the most important phase of a mission. Boyd found that the quality of orientation determines everything downstream. A fighter pilot who understands the situation writes the outcome before the fight begins. An agent who understands the codebase writes correct code on the first attempt.

**Do not rush this phase.** Time spent orienting is the highest-leverage investment in the entire mission.

**Task:** $ARGUMENTS

---

## Step 1: Observe — Gather raw information

If `$ARGUMENTS` is empty or vague, ask: "What would you like me to build? Describe the end state."

If a `.mission/plan.md` already exists, read it and ask: "An existing mission plan was found. Do you want to (a) replace it with a new plan, or (b) refine the existing plan?"

## Step 2: Orient — Probe for the full picture

Before planning, build your orientation. Ask 3-7 focused questions covering:

- **Scope boundaries**: What's explicitly OUT of scope?
- **Existing code**: Are there patterns, conventions, or architecture I should follow?
- **Verification**: How will we know each piece works? (existing tests, manual check, specific commands?)
- **Dependencies**: Are there external services, APIs, or packages involved?
- **Priority**: If this runs long, what's the MVP vs. nice-to-have?

**Do NOT proceed until the user answers. Do NOT guess at constraints.** Your orientation is only as good as the information you build it from.

## Step 3: Orient deeper — Research the codebase

Boyd's orientation has five inputs. Map them:

1. **Project conventions** (cultural traditions) — Read `CLAUDE.md`, `README.md`, `package.json` / `pyproject.toml`. What are the team's norms?
2. **Existing architecture** (previous experience) — Use subagents (`Agent` tool with `subagent_type: Explore`) to map the relevant codebase. This keeps heavy exploration out of your context.
3. **New information** — What did the user tell you? What did you discover that wasn't obvious?
4. **Build/test/lint commands** — Identify the verification tools. These are how reality will talk to you.
5. **Analysis & synthesis** — Does the task fit cleanly into the existing architecture, or does something need to change? If there's tension, name it now.

## Step 4: Decide — Draft the mission plan

Create the plan using the template at [../references/mission-plan-template.md](../references/mission-plan-template.md).

Key rules:
- **3-7 milestones.** Fewer than 3 = milestones too large (context collapse risk). More than 7 = over-decomposition (coordination overhead).
- **Each milestone has runnable acceptance criteria.** At least one command that exits 0 on success. This is how you'll test your hypotheses.
- **Each milestone is independently verifiable.** No milestone depends on self-assessment.
- **Milestones define intent, not scripts.** Specify the GOAL and ACCEPTANCE CRITERIA, not step-by-step instructions. The agent executing each milestone has autonomy in how to achieve the goal — this is Boyd's *Auftragstaktik* (mission-type orders).
- **Order by dependency.** Foundational work first, integration last.
- **Final milestone is always integration.** Full verification sweep.
- **Size honestly.** S (< 15 min), M (15-45 min), L (45-90 min). If any milestone is XL, break it down.

## Step 5: Iterate — Test the plan against the user's orientation

Present the plan to the user. Ask: "Does this plan look right? Any milestones to add, remove, or reorder?"

The user has orientation you don't — domain knowledge, business context, past failures. Their feedback is observation data. Incorporate it.

Iterate until the user explicitly approves. **The plan is not approved until they say so.**

## Step 6: Act — Save the approved plan

Once approved:

1. Create the `.mission/` directory in the project root
2. Write the plan to `.mission/plan.md`
3. Create `.mission/progress.md` with all milestones listed as pending:

```markdown
# Mission Progress

**Mission:** {title}
**Started:** {date}
**Status:** Planning complete. Ready to execute.

## Milestones

- [ ] Milestone 1: {title}
- [ ] Milestone 2: {title}
- [ ] Milestone 3: {title}
...
```

4. Confirm: "Plan saved to `.mission/plan.md`. Run `/mission:start` to begin execution."

---

## Planning Anti-Patterns (Orientation Failures)

- **Vague acceptance criteria.** "The API works" is not verification. "`curl localhost:3000/api/users` returns 200 with a JSON array" is. Without concrete criteria, you can't test your hypotheses.
- **Script milestones instead of intent milestones.** Detailed step-by-step instructions become stale as soon as reality diverges. Specify the goal and let the executor orient.
- **Monolith milestones.** If a milestone touches more than 5-7 files, it's too big. A large milestone is where context collapse happens.
- **No risk register.** Risks are future mismatches you can anticipate. Name them now so they don't surprise you mid-flight.
- **Skipping the user.** The user's orientation catches things yours can't. Never auto-approve.
