---
name: status
description: >-
  Show current mission progress — milestones completed, current milestone,
  remaining work, and any blockers. Pure observation, no execution.
disable-model-invocation: true
---

# Mission Status — Observe

Pure observation. Read the state, report it, suggest next action. Do not execute any work.

---

## Procedure

1. Check if `.mission/plan.md` exists. If not: "No active mission. Run `/mission:plan <task>` to start one."

2. Read `.mission/plan.md` and `.mission/progress.md`. If `.mission/learnings.md` exists, read it too.

3. Print:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MISSION STATUS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Mission:   {title}
Progress:  {completed}/{total} milestones

  ✅ Milestone 1: {title} — {verification notes}
  ✅ Milestone 2: {title} — {verification notes}
  ▶  Milestone 3: {title} — {in progress / next up}
  ⬜ Milestone 4: {title}
  ⬜ Milestone 5: {title}

Blockers:  {any noted blockers, or "None"}
Learnings: {count} entries in .mission/learnings.md
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

4. Suggest next action:
   - No milestones started → "Run `/mission:start` to begin."
   - In progress → "Run `/mission:continue` to resume from milestone {N}."
   - All complete → "All milestones done. Mission complete."
