# Mission Patterns & Anti-Patterns

Patterns that prevent context collapse over long-horizon tasks, and recovery procedures when things go wrong. Derived from research on Factory Missions, SWE-Agent, AutoCodeRover, Devin, and academic work on long-horizon LLM agents.

---

## Why Agents Fail on Long Tasks

Context collapse has five failure modes. Knowing them helps you catch them early:

1. **Lost-in-the-middle**: Information in the middle of long contexts gets less attention. Your plan from 30 minutes ago is effectively invisible unless you re-read it from a file.

2. **Compounding drift**: Small misunderstandings compound. After 50+ steps, your mental model diverges from the actual file state. You edit based on stale memory.

3. **Goal dilution**: As context fills with tool outputs and file contents, the original task gets buried. You start "doing things" without connection to the goal.

4. **State confusion**: After editing file A, reading file B, then returning to file A — you operate on your memory of file A *before* the edit.

5. **False success**: In 97% of agent failures, the agent *believes* it has solved the task (Factory Legacy-Bench finding). Self-assessment is fundamentally unreliable.

---

## Patterns That Work

### P1: The Environment is Truth, Not Your Memory

Files on disk, git state, test results, and build output are ground truth. Your context window is a *view* into reality that degrades over time.

**Practice:**
- Re-read any file before editing it, even if you "just" read it
- Run verification commands instead of inspecting your own code
- Check git status before committing to understand actual state
- After `/clear`, you've lost nothing — the files ARE your memory

### P2: Construct Context, Don't Accumulate It

Effective agents build a fresh, focused context for each step rather than dragging along full history.

**Practice:**
- At each milestone start, re-read: plan file, progress file, relevant source files
- Don't rely on what you "remember" from earlier milestones
- Use subagents for exploratory file reads (their context doesn't bloat yours)
- After `/clear`, load only what the current milestone needs

### P3: Recency Anchor Your Current Task

LLMs attend most strongly to the beginning and end of context. The current milestone should always be the most recently processed information.

**Practice:**
- Read the mission plan AFTER reading background files, so the current task is freshest
- Update progress AFTER completing work, so it's the last thing processed
- When announcing a new milestone, re-state its goal and acceptance criteria

### P4: Fail Fast, Fail Loud

An error caught in the current step costs 1 step to fix. An error caught 10 steps later may require backtracking all 10.

**Practice:**
- Run acceptance criteria after EVERY milestone, no exceptions
- Run incremental checks during implementation (type-check after adding types, test after adding a test)
- If something feels wrong, stop and investigate NOW, not later
- Never weaken a test to make it pass

### P5: Failure Triggers Replanning, Not Retrying

When something doesn't work, go back to the plan with new information rather than blindly retrying the same approach.

**Practice:**
- After 3 failed attempts at the same fix: stop, re-read the error, re-read the relevant code, reassess the approach
- Ask: "Am I solving the right problem?" before trying again
- If the approach is fundamentally wrong, update the plan (with user approval)
- Write what you learned to `.mission/learnings.md` so it survives context refresh

### P6: Scope Is Sacred

Milestone boundaries exist to prevent context collapse. Crossing them is the #1 cause of long-session failures.

**Practice:**
- Only touch files listed in the current milestone's "files to touch"
- If you discover new work needed, add it as a new milestone — don't expand the current one
- If fixing milestone 3 requires changing milestone 1's work, that's a new milestone, not a retroactive edit
- Resist the urge to "quickly fix" something in a future milestone's scope

### P7: Git Is Your Checkpoint System

Every meaningful state change should be a commit. Commits are rollback points.

**Practice:**
- Commit after each milestone passes validation
- Use descriptive commit messages that reference the milestone: "mission(2/5): implement user API routes"
- If a milestone goes badly wrong, you can `git diff` or `git stash` to recover
- Never commit code that fails its acceptance criteria

---

## Anti-Patterns That Cause Failure

### A1: "It Looks Right to Me" (Self-Assessment)

**What happens:** You read your own code, decide it's correct, and move on. The code has a bug that tests would have caught.

**Why it's dangerous:** LLMs have a coherence bias — they tend to believe their own output is correct. This is the #1 cause of false success.

**Fix:** Run the verification command. Every time. No exceptions. If there's no verification command for this milestone, the plan is incomplete — add one before continuing.

### A2: Boiling the Ocean (Scope Creep)

**What happens:** While working on milestone 3, you notice something in an unrelated file that "should be fixed." You fix it. This leads to another fix. Now you're deep in code that has nothing to do with the current milestone, and your context is bloated.

**Why it's dangerous:** Every file you read and edit outside the current scope consumes context and increases the chance of compounding drift.

**Fix:** If you see something that needs fixing but it's outside the current milestone, write a one-line note in `.mission/learnings.md` and move on. It can be a future milestone.

### A3: Silent Failure (Weakening Validation)

**What happens:** A test fails. Instead of fixing the underlying code, you modify the test to pass. Or you catch an exception and swallow it. The original problem is still there, hidden.

**Why it's dangerous:** The validation gate exists specifically to catch problems early. Bypassing it means the problem compounds downstream and becomes 10x harder to fix.

**Fix:** If a test fails, the CODE is wrong (not the test), unless you can prove the test itself has a bug. If acceptance criteria seem wrong, discuss with the user before changing them.

### A4: Context Hoarding (Memory Over Files)

**What happens:** You try to keep the entire project architecture in your head instead of re-reading files when needed. After 30+ minutes, your mental model is stale.

**Why it's dangerous:** Context degrades over time (lost-in-the-middle effect). Your "memory" of a file from 20 minutes ago may be wrong.

**Fix:** Re-read files before editing. Use `Read` tool liberally — it's cheap. The disk is always right; your memory might not be.

### A5: Planning Aversion (Jumping to Code)

**What happens:** The task "seems simple" so you skip planning and start coding. Thirty minutes later, you realize the architecture doesn't support what you need, and you have to redo everything.

**Why it's dangerous:** Writing code in the wrong place or with the wrong approach is the most expensive kind of mistake. 10 minutes of planning saves hours of rework.

**Fix:** Always complete Phase 1, even for "simple" tasks. The plan can be brief (3 milestones), but it must exist and be approved.

### A6: Milestone Creep (Expanding Scope Mid-Flight)

**What happens:** A milestone was sized as M but keeps growing as you discover edge cases, additional files to modify, or "one more thing." The milestone balloons to XL size, and your context is exhausted before you finish.

**Why it's dangerous:** Large milestones are where context collapse happens. The whole point of milestones is keeping each chunk small enough to execute in focused context.

**Fix:** If a milestone is clearly larger than planned, stop. Split it into two milestones. Update the plan. Then continue with the smaller scope.

### A7: Infinite Retry Loop

**What happens:** A test fails. You try a fix. It fails again. You try another fix. Same error. You try a third variation. Still failing. You keep going, consuming context on repeated failures.

**Why it's dangerous:** After 3 attempts at the same problem, you likely have a fundamental misunderstanding. More attempts won't help — they'll just burn context.

**Fix:** After 3 failed attempts, invoke Level 2 recovery: stop coding, re-read the error AND the relevant source code from disk, and reassess the approach entirely. If still stuck, escalate to the user (Level 3).

---

## Recovery Procedures

### Recovering from a wrong approach

1. Stop implementing
2. `git stash` or `git diff` to capture current state
3. Re-read `.mission/plan.md` — is the milestone correctly defined?
4. Re-read the relevant source files from disk (not from memory)
5. Identify what assumption was wrong
6. If the plan needs updating, propose changes to the user
7. If just the approach was wrong, try a different approach (max 2 more attempts before escalating)

### Recovering from context exhaustion

1. Update `.mission/progress.md` with current state (what's done, what's in progress, what failed)
2. Commit any working changes
3. Tell the user: "Context is getting long. I recommend running `/clear` and then `/mission continue` to resume with fresh context."
4. After `/clear`, re-read plan and progress files, then continue from the current milestone

### Recovering from a cascading failure

When a fix in milestone N breaks something from milestone N-1:

1. Stop work on milestone N
2. Add a new milestone between N-1 and N: "Fix regression in {what broke}"
3. Git diff against the last known-good commit to understand what changed
4. Fix the regression first, verify with milestone N-1's acceptance criteria
5. Only then resume milestone N

### Recovering from user direction change

1. Update `.mission/plan.md` with the new direction
2. Mark affected milestones as superseded in `.mission/progress.md`
3. Add new milestones for the changed work
4. Get user approval on the updated plan
5. Continue from the first affected milestone
