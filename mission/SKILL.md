---
name: mission
description: >-
  Run long-horizon, multi-hour coding tasks without context collapse.
  Decomposes projects into milestones with validation gates,
  fresh context per step, and file-based state that survives compaction.
  Use when a task will take more than 30 minutes or spans multiple features.
disable-model-invocation: true
user-invocable: true
---

# Mission Control

A structured execution framework for long-horizon coding tasks, built on John Boyd's OODA loop.

## Operating Philosophy: OODA

Missions follow Boyd's core insight: **Orientation is the schwerpunkt** — the center of gravity. The quality of your understanding determines everything downstream. A well-oriented agent writes correct code on the first attempt. A poorly-oriented agent writes fast, wrong code and spends 10x the effort fixing it.

The OODA cycle in missions:
- **Observe** — Read files from disk, run commands, check state. Never operate from memory.
- **Orient** — Understand context, conventions, and constraints. This is where value is created. Don't rush it.
- **Decide** — For novel situations, deliberate explicitly. For familiar patterns, skip to action via implicit guidance.
- **Act** — Execute. Every action is a hypothesis test — observe the result and reorient.

Three operating principles that follow:
1. **Mismatch detection over blind execution.** At every milestone boundary, check: does reality match expectations? If not, reorient before continuing.
2. **Destruction and creation over retry.** When an approach fails 3 times, don't try a 4th variation. Destroy the mental model. Rebuild from the pieces + new information.
3. **Tempo control over constant speed.** Fast for familiar work, deliberate for novel challenges. Context refresh between milestones is a forced reorientation that improves quality.

See [references/ooda.md](references/ooda.md) for the full OODA framework.

## Subcommands

| Command | OODA Phase | Purpose |
|---|---|---|
| `/mission:plan <task>` | Orient | **Start here.** Research, decompose, approve, save the plan. |
| `/mission:start` | Act | Begin execution from milestone 1. Requires an approved plan. |
| `/mission:continue` | Re-orient | Resume with fresh context from last checkpoint. |
| `/mission:status` | Observe | Show current progress. |
| `/mission:pivot` | Destroy & Create | Mid-flight plan adjustment when the model is wrong. |
| `/mission:validate` | Observe | Run acceptance criteria — let reality speak. |

## Lifecycle

```
/mission:plan "build auth system"     ← ORIENT: research, plan, get approval
        │
/mission:start                        ← ACT: execute milestone by milestone
        │                                     (each milestone is its own OODA cycle)
    (context getting long?)
        │
/clear → /mission:continue            ← RE-ORIENT: fresh context, re-read state, continue
        │
    (approach isn't working?)
        │
/mission:pivot                        ← DESTROY & CREATE: rebuild the plan from new understanding
        │
/mission:validate                     ← OBSERVE: let verification commands tell you the truth
        │
    (all milestones done)             ← Mission complete
```

## State as Shared Orientation

Boyd's organizational OODA relies on shared orientation — team members with a shared mental model coordinate implicitly. In missions, `.mission/` files serve this function across context boundaries:

```
.mission/
├── plan.md          # Shared intent — what we're building and why
├── progress.md      # Shared situation awareness — what's done, what's next
└── learnings.md     # Shared experience — patterns discovered during execution
```

After `/clear` or context compaction, `/mission:continue` re-reads these files and inherits full orientation. Nothing is lost — the files ARE your memory.
