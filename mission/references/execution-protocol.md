# Execution Protocol

The milestone OODA loop. Referenced by `mission:start` and `mission:continue`.

---

## The Milestone OODA Cycle

Each milestone is a complete OODA cycle: orient to the goal, act on it, observe the results, reorient for what's next.

### 1. Orient — Load the milestone

Print a header:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MILESTONE {N}/{TOTAL}: {title}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Build your orientation:
- Read `.mission/progress.md` to confirm current state
- Read `.mission/plan.md` to load this milestone's goal and acceptance criteria
- Read the source files you'll be modifying — **never edit from memory**
- If `.mission/learnings.md` exists, check for relevant patterns

**Mismatch check**: Does the current state of the code match what you expect based on previous milestones? If anything is surprising, investigate before proceeding. A mismatch at the start means compounding errors downstream.

### 2. Decide — Choose your approach

Apply Boyd's implicit/explicit split:

- **Familiar pattern** (standard CRUD, common test setup, well-known library): Act with implicit guidance. Move decisively. Don't over-deliberate on solved problems.
- **Novel situation** (unfamiliar architecture, unexpected behavior, complex integration): Deliberate explicitly. Explore with subagents. Read more code. Think before acting. Slowing down here saves time downstream.

The milestone's acceptance criteria tell you the goal. How you get there is your call — this is *Auftragstaktik* (mission-type orders). The plan specifies intent, not scripts.

### 3. Act — Implement

Write the code for this milestone. Rules:

- **Stay scoped.** Only touch files relevant to THIS milestone. Do not refactor adjacent code. Do not add features from future milestones. Scope discipline prevents context collapse.
- **Commit incrementally.** Commit after each meaningful change: `mission(N/total): {description}`. Commits are rollback checkpoints.
- **Every action is a hypothesis.** You write code because you believe it will make the acceptance criteria pass. You'll test that belief next.
- **Re-read before editing.** The file may have changed. Disk is truth; memory is a stale cache.

### 4. Observe — Validate (THE critical step)

Run EVERY acceptance criterion listed in the plan for this milestone. This is reality speaking to you.

**Rules:**
- Run each command. Skip none.
- If a command fails, you have a **mismatch** between your hypothesis and reality. Reorient before retrying.
- After 3 failed attempts at the same fix, escalate to destruction and creation (see failure recovery below).
- Never say "tests pass" without running them. Never say "build succeeds" without building. Self-assessment is the opposite of observation.

### 5. Reorient — Update state and assess

After validation passes, update `.mission/progress.md`:

```markdown
- [x] Milestone 1: Set up database schema ✅ (verified: tests pass, migrations run)
- [x] Milestone 2: Implement API routes ✅ (verified: all endpoints return expected responses)
- [>] Milestone 3: Build frontend components (in progress)
- [ ] Milestone 4: Integration testing
```

**Feed forward**: What did you learn in this milestone that changes your orientation for the next? Write notable discoveries to `.mission/learnings.md`. This is Boyd's feedback loop from action back to orientation.

### 6. Tempo check — Manage context

Assess context health after each milestone:

- **Context is heavy** (20+ minutes of work, many file reads, failed attempts): Tell the user: "Context is getting heavy. I recommend `/clear` then `/mission:continue` for fresh context." A forced reorientation here IMPROVES quality — you shed accumulated drift and stale assumptions.
- **Context is clean**: Proceed directly to the next milestone.
- **The milestone was novel/hard**: Even if context seems okay, consider a refresh. Novel situations consume more context than routine ones.

---

## After All Milestones — Final Observation

1. Run a **full verification sweep**: all tests, build, lint, type-check. This is your final mismatch check against the full plan.

2. Update `.mission/progress.md` with final status.

3. Print:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MISSION COMPLETE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Milestones: {completed}/{total}
Files changed: {list key files}
Verification: {all checks passed / issues remaining}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

4. Ask the user: commit, create a PR, or continue with additional work.

---

## Failure Recovery — Destruction and Creation

When acceptance criteria fail, Boyd's principle applies: failure means a mismatch between your mental model and reality. The response depends on how deep the mismatch is.

### Level 1: Reorient and fix (attempts 1-3)

The error message is observation data. Read it carefully — what is reality telling you? Orient to the specific issue. Fix it. Re-run. This is the tight OODA loop: act → observe → reorient → act.

### Level 2: Destroy and create (after 3 failures)

Three failures on the same issue means your mental model is wrong. Retrying with variations won't help — you need destruction and creation:

1. **Stop coding.** More action without reorientation makes things worse.
2. **Observe from scratch.** Re-read the relevant source files FROM DISK. Re-read the error messages. What do they actually say, without your assumptions layered on top?
3. **Destroy the old model.** What assumption was wrong? Name it explicitly.
4. **Create a new model.** Take the pieces that still hold + the new information from the errors + fresh reading of the code. Synthesize a new approach.
5. If the plan itself is wrong, tell the user to run `/mission:pivot`.

### Level 3: Escalate

If destruction and creation doesn't resolve it:
1. Write what you tried to `.mission/progress.md`
2. State: the goal, what failed, what you tried, your best hypothesis about root cause
3. Ask the user for direction. Do NOT continue autonomously.

**Never silently work around a failure.** A validation gate exists to catch mismatches early. Bypassing it means the mismatch compounds downstream.

---

## Context Management Rules

1. **The plan file is the source of truth.** Not your memory. Not the conversation. The file.
2. **Re-read files before editing.** Disk is ground truth; your memory is a stale cache.
3. **Progress lives in `.mission/progress.md`.** Update after every milestone. Read before every milestone.
4. **After `/clear`, you lose nothing.** Plan, progress, learnings, and code are all on disk. The files carry your orientation forward.
5. **Delegate exploration to subagents.** Heavy file reads bloat your context. Subagents keep exploration isolated.
6. **Recency-anchor the current task.** Read background files first, then the current milestone details last. LLMs attend most strongly to the end of context.
