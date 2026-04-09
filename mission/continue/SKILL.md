---
name: mission:continue
description: >-
  Resume a mission from the last completed milestone. Use after /clear,
  in a new session, or when context is getting long. Reads plan and
  progress from .mission/ files and picks up where you left off.
effort: high
---

# Mission Continue — Forced Reorientation

> Context refresh is not a limitation — it's Boyd's reorientation in action.

You are resuming a mission with **fresh context**. This is the most powerful moment in the OODA cycle: your old context, with its accumulated drift, stale assumptions, and lost-in-the-middle effects, is gone. You start clean. The `.mission/` files carry your shared orientation forward.

---

## Reorientation procedure

### 1. Observe — Read the state from disk

Read these files in order (background first, current task last — recency anchoring):

1. `.mission/plan.md` — the full plan (shared intent)
2. `.mission/learnings.md` — if it exists, patterns from earlier work (shared experience)
3. `.mission/progress.md` — current state (shared situation awareness) — **read this last** so it's freshest in context

If `.mission/plan.md` doesn't exist: "No mission plan found. Run `/mission:plan <task>` first." Stop.

### 2. Orient — Build your mental model

From the files, identify:
- Which milestones are completed (`[x]`)
- Which milestone is next (first `[ ]` or `[>]`)
- Any notes about blockers, partial work, or discoveries
- The acceptance criteria for the next milestone

### 3. Announce — Confirm orientation

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MISSION RESUMED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Completed: {N}/{total} milestones
Resuming:  Milestone {N+1}: {title}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 4. Mismatch check

If progress notes mention partially completed work:
- Read the relevant source files from disk
- Run a quick verification — does the current state match what progress.md claims?
- If there's a mismatch between progress notes and actual file state, trust the FILES. Update progress.md to reflect reality.

### 5. Execute — Enter the OODA cycle

Follow the execution protocol in [../references/execution-protocol.md](../references/execution-protocol.md) starting from the **next incomplete milestone**.

## The principle

**You have fresh context. This is an advantage, not a handicap.** You don't carry forward stale assumptions, accumulated drift, or mid-context attention degradation. You start with a clean orientation built from ground truth (the files).

- Re-read source files before editing them. Don't assume you know what they contain.
- Re-read the plan before each milestone. Don't assume you remember the criteria.
- If something feels off, it probably is. Investigate the mismatch.
