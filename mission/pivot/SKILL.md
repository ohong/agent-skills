---
name: mission:pivot
description: >-
  Mid-flight mission plan adjustment. Use when the approach is wrong,
  requirements changed, a milestone needs splitting, or scope needs updating.
  Boyd's "destruction and creation" applied to the plan.
argument-hint: "[reason for pivot]"
effort: high
---

# Mission Pivot — Destruction and Creation

> "To comprehend and cope with our environment we develop mental patterns or concepts of meaning... We destroy and create these patterns to permit us to both shape and be shaped by a changing environment." — John Boyd, "Destruction and Creation"

Something has changed. The current plan no longer matches reality. This is a **mismatch** — the most important signal in Boyd's framework. The correct response is not to force the old plan harder. It's to destroy the parts that don't work and create something new from the pieces + what you've learned.

**Reason:** $ARGUMENTS

---

## The Destruction and Creation Process

### 1. Observe — What triggered the pivot?

Read `.mission/plan.md`, `.mission/progress.md`, and `.mission/learnings.md` (if it exists).

Identify the mismatch. Common types:
- **Scope change** — User wants to add or remove features
- **Milestone too large** — A milestone is taking much longer than estimated
- **Wrong approach** — The technical approach isn't working after repeated attempts
- **Dependency discovered** — A milestone can't proceed without something unexpected
- **Direction change** — User wants to take the project a different way

### 2. Destroy — Break apart the old plan

Don't try to patch a broken plan. Identify what's still valid and what isn't:
- Which completed milestones are solid? (Their work stands.)
- Which upcoming milestones are still correct?
- Which milestones need to change, split, or be replaced?
- What new information from the failed approach should inform the new plan?

### 3. Create — Synthesize a new plan

Boyd's snowmobile: take the engine from the old approach, the frame from new understanding, the insight from the failure, and build something new.

- Add new milestones for added scope
- Split oversized milestones into 2-3 smaller ones
- Replace milestones with wrong approaches
- Insert dependency milestones where needed
- Mark removed milestones as `[~] superseded` (don't delete them — they're history)

### 4. Present and get approval

Show the user:
- What changed and why
- The updated milestone list (with old milestones marked)
- Impact on remaining work

**Get explicit approval before modifying files.** The user's orientation catches things yours can't.

### 5. Save the updated plan

Once approved:
- Update `.mission/plan.md` with the new milestones
- Update `.mission/progress.md` to reflect the new structure
- Write to `.mission/learnings.md`: what changed, why, what was learned

Tell the user: "Plan updated. Run `/mission:continue` to resume from milestone {N}."

---

## Pivot Rules

- **Completed milestones are immutable.** Don't retroactively change milestones that passed validation. If their work needs modification, add a new milestone. History is observation data.
- **Don't pivot and execute in the same breath.** Update the plan, get approval, THEN resume execution in a separate step. Mixing planning and execution is how orientation degrades.
- **Document the why.** The reason for the pivot is the most valuable learning. Write it to `learnings.md`. Future sessions (and future pivots) need this context.
- **A pivot is not a failure.** It's Boyd's destruction and creation in action — the mechanism by which you maintain orientation quality over long horizons. Agents that can't pivot are agents that drift.
