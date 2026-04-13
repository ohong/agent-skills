---
name: start
description: >-
  Begin executing an approved mission plan from milestone 1.
  Requires .mission/plan.md to exist. Runs milestones sequentially
  with validation gates between each. Use /mission:plan first.
disable-model-invocation: true
effort: high
---

# Mission Start — Enter the OODA Cycle

You are beginning execution. Each milestone is its own OODA cycle: orient to the milestone, act on it, observe the results, reorient for the next.

---

## Pre-flight: Orient to the mission

1. Check that `.mission/plan.md` exists. If not: "No mission plan found. Run `/mission:plan <task>` first." Stop.

2. Check that `.mission/progress.md` exists. If not: "No progress file found. Run `/mission:plan <task>` first." Stop.

3. Read `.mission/plan.md` — load the full plan into your orientation.

4. Read `.mission/progress.md` — if milestones are already done, ask: "Previous progress detected. Resume with `/mission:continue`, or restart from milestone 1?"

5. **Mismatch check**: Read the plan's build/test/lint commands and run them once. Do they work? If not, fix the environment before starting. Starting with a broken environment means every observation will be contaminated.

## Execution: The Milestone OODA Loop

Follow the execution protocol in [../../references/execution-protocol.md](../../references/execution-protocol.md) starting from **Milestone 1**.

Each milestone follows the OODA cycle:

### Orient
- Re-read `.mission/plan.md` for this milestone's goal and acceptance criteria
- Re-read `.mission/progress.md` for current state
- Read the source files you'll be modifying — never edit from memory
- If `.mission/learnings.md` exists, check for relevant patterns

### Decide (or act implicitly)
- **Familiar pattern?** Act directly. Standard CRUD, common test setup, well-known library usage — move with implicit guidance.
- **Novel situation?** Deliberate explicitly. Unfamiliar architecture, unexpected file structure, complex integration — slow down, explore with subagents, think before acting.

### Act
- Write code, staying scoped to THIS milestone only
- Commit after each meaningful change: `mission(N/total): {description}`
- Every action is a hypothesis: "I believe this change will make the acceptance criteria pass"

### Observe
- Run ALL acceptance criteria. This is reality speaking to you — listen.
- If they pass: update progress, proceed to next milestone
- If they fail: you have a **mismatch**. Reorient before retrying. See failure recovery below.

## Failure Recovery: Destruction and Creation

When acceptance criteria fail, Boyd's principle applies: **don't retry blindly. Reorient.**

**Level 1 — Fix (attempt 1-3):** Read the error. It's observation data. Orient to what it's telling you. Fix the specific issue. Re-run.

**Level 2 — Destroy and create (after 3 failures):** Your mental model is wrong. Stop coding.
  - Re-read the relevant source files FROM DISK (not from memory)
  - Re-read the error messages — what are they actually saying?
  - What assumption did you make that was wrong?
  - Destroy the old approach. Build a new one from the pieces + new information.
  - If the plan itself is wrong, tell the user: "This milestone needs rethinking. Run `/mission:pivot`."

**Level 3 — Escalate:** Write what you tried to `.mission/progress.md`. State the goal, what failed, your best guess at root cause. Ask the user for direction.

## Context Management

- **After completing a milestone**, if the conversation is long (20+ minutes of work, many file reads): recommend `/clear` → `/mission:continue`. Fresh context is forced reorientation — a feature, not a bug.
- **Delegate heavy exploration** to subagents. Their reads don't bloat your context.
- **Keep the current milestone freshest in context.** Read background files first, then the current milestone details last. LLMs attend most strongly to the end of context (recency anchor).

## Key Rules

- **Never skip validation.** Every action is a hypothesis. Test it.
- **Never self-assess.** "It looks right" is not observation. Run the command.
- **Never expand scope.** Only touch files in THIS milestone. New work = `/mission:pivot`.
- **Commit per milestone.** Each passing milestone gets a checkpoint commit.
