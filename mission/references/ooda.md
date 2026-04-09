# OODA: The Operating Philosophy of Missions

Missions are built on John Boyd's OODA framework — not the oversimplified "observe-orient-decide-act" cycle, but the real system: a web of feedback loops where **Orientation** dominates everything.

---

## Why OODA, Not a Linear Pipeline

Most agent frameworks operate as linear pipelines: plan → execute → verify → repeat. This fails on long tasks because:
- Plans become stale as the environment changes
- Agents can't distinguish familiar from novel situations
- Failures trigger blind retries instead of reorientation
- There's no mechanism to update the mental model mid-flight

Boyd's OODA is different. It's a **continuous, multi-feedback system** where every action updates your understanding, and your understanding shapes what you observe next.

---

## The Four Phases in Mission Context

### Observe
Gather raw data from the environment. In missions, this means:
- Read files from disk (never from memory)
- Run verification commands and read their output
- Check git state
- Read `.mission/progress.md` and `.mission/plan.md`
- Notice what changed since last you looked

**Key insight**: Orientation shapes observation. You see what your mental model primes you to see. Deliberately look for things that *contradict* your expectations — that's where mismatches hide.

### Orient (THE schwerpunkt)
Boyd called Orientation the center of gravity. It shapes how you observe, what you decide, and how you act. In missions, orientation means:
- Understanding the codebase architecture and conventions
- Understanding the current milestone's goal and constraints
- Incorporating learnings from previous milestones
- Recognizing patterns from past experience (`.mission/learnings.md`)
- Performing analysis & synthesis when the situation doesn't match expectations

**Orientation has five inputs (Boyd's model):**
1. **Previous experience** → patterns from earlier milestones, learnings.md
2. **New information** → what you just observed (test results, file state, errors)
3. **Cultural traditions** → project conventions, CLAUDE.md, team patterns
4. **Analysis & synthesis** → breaking apart a failed approach and building a new one
5. **Genetic heritage** → your foundational capabilities and constraints as an LLM

**The critical operation within orientation is destruction and creation**: when your current mental model produces a mismatch with reality, you must *destroy* the old model and *create* a new one from the pieces plus new information. This is Boyd's paper "Destruction and Creation" in action. Don't patch a broken model — rebuild it.

### Decide
Form an explicit plan of action. In missions, this means:
- Choosing which files to modify
- Choosing the implementation approach
- Choosing what to verify

**Key insight**: For well-understood situations, skip this phase entirely. Go from orientation directly to action via **implicit guidance**. Only invoke explicit deliberation for novel or surprising situations. This is how experts operate — they recognize and act, reserving deliberation for the unfamiliar.

### Act
Execute. Write code, run commands, modify files, commit.

**Key insight**: Every action is a hypothesis test. You act, then observe the result. Did reality respond as your orientation predicted? If yes, continue. If no, you have a mismatch — reorient before acting again.

---

## The Feedback Loops That Matter

Boyd's real OODA isn't a simple cycle. These feedback paths are what make it work:

```
    ┌─────────────────────────────────────────┐
    │           Unfolding Environment          │
    └────────────┬───────────────────────┬─────┘
                 │                       │
                 ▼                       │
           ┌──────────┐                  │
           │ OBSERVE  │◄────────────┐    │
           └────┬─────┘             │    │
                │                   │    │
    ┌───────────▼──────────────┐    │    │
    │         ORIENT           │    │    │
    │  ┌───────────────────┐   │    │    │
    │  │ Analysis/Synthesis │   │    │    │
    │  │ Previous Experience│   │    │    │
    │  │ New Information    │   │    │    │
    │  │ Project Conventions│   │    │    │
    │  └───────────────────┘   │    │    │
    └──┬──────────────┬────────┘    │    │
       │              │             │    │
       │ implicit     │ explicit    │    │
       │ guidance     ▼             │    │
       │        ┌──────────┐       │    │
       │        │  DECIDE  │       │    │
       │        └────┬─────┘       │    │
       │             │             │    │
       ▼             ▼             │    │
    ┌──────────────────┐          │    │
    │       ACT        ├──────────┘    │
    └──────────────────┴───────────────┘
         action changes environment,
         results feed back to observation
```

1. **Action → Observation**: You run a test. You read the result. This is hypothesis testing.
2. **Observation → Orientation**: Test failure updates your understanding of the code.
3. **Orientation → Observation**: Your understanding shapes what you look for next. After a type error, you look for type mismatches. After a logic error, you trace the logic path.
4. **Orientation → Action (implicit)**: For familiar patterns, skip deliberation. If you've seen this error before, fix it directly.
5. **Environment → Observation**: The codebase is not static. Other processes, git changes, and the user's actions alter the environment.

---

## The Seven Principles for Missions

### 1. Orientation is the most valuable investment

Spending time understanding the codebase, reading conventions, and researching before coding is not overhead — it's the highest-leverage activity. A well-oriented agent writes correct code on the first try. A poorly-oriented agent writes fast but wrong code and spends 10x fixing it.

**In practice**: The planning phase (`/mission:plan`) is where most value is created. The codebase research step is not optional. Skipping orientation to "save time" is the most expensive mistake.

### 2. Detect mismatches early, reorient immediately

A mismatch is a gap between what you expect and what you observe. Mismatches are the most important signal in the system — they mean your orientation is wrong.

**In practice**: At each milestone boundary, explicitly check: "Does the current state match what I expected?" If not, stop and reorient before continuing. Read files from disk. Run verification. Update your understanding. Don't paper over surprises.

### 3. Implicit guidance for the familiar, explicit deliberation for the novel

Experienced operators go from orientation directly to action for recognized situations. They only invoke full deliberation for genuinely new problems. This is how tempo is maintained.

**In practice**: If you've seen this pattern before (a standard CRUD endpoint, a familiar test setup, a common error), act decisively. If the situation is genuinely novel (unfamiliar architecture, unexpected behavior, a pattern you haven't seen), slow down: read more code, explore with subagents, think before acting.

### 4. Every action is a hypothesis test

You don't write code and hope. You write code, run verification, and observe. The test result is reality talking to you.

**In practice**: Run acceptance criteria after every milestone. Run incremental checks during implementation. Read error messages carefully — they are the most valuable observation data you'll get.

### 5. Failure demands destruction and creation, not retry

When something fails, the temptation is to retry with a small tweak. But repeated failure means your mental model is wrong. You need to *destroy* the model (admit you don't understand the situation) and *create* a new one (re-read the code, re-examine assumptions, build a fresh understanding from the pieces + new information).

Boyd's snowmobile analogy: take the parts of what you know (the engine from approach A, the frame from approach B, the insight from the error message), and synthesize something new.

**In practice**: After 3 failed attempts, DO NOT try a 4th variation. Stop. Re-read the relevant files from disk. Re-examine your assumptions. What did the error actually say? What did you assume that might be wrong? Build a new approach from the ground up. This is `/mission:pivot` in action.

### 6. File-based state is shared orientation

Boyd's organizational OODA relies on shared orientation — team members who share a mental model can coordinate implicitly without explicit communication. In missions, the `.mission/` files serve this function across context refreshes.

**In practice**: `.mission/plan.md` is the shared intent. `.mission/progress.md` is the shared situation awareness. `.mission/learnings.md` is the shared experience. After `/clear`, the new context inherits shared orientation by reading these files. Nothing is lost.

### 7. Control tempo, don't just maximize speed

Boyd's tempo advantage is not about raw speed. It's about operating at a pace the problem demands — fast for familiar work, deliberate for novel challenges — while maintaining orientation quality throughout.

**In practice**: Small milestones on well-understood code → move fast, minimal deliberation. Large milestones on unfamiliar architecture → slow down, explore with subagents, orient thoroughly before acting. Context refresh between milestones is not a delay — it's a forced reorientation that IMPROVES quality.

---

## Mismatch Detection Checklist

At each milestone boundary, check for these mismatches:

- [ ] **File state mismatch**: Do the files on disk match what you expect? Re-read before editing.
- [ ] **Test state mismatch**: Do existing tests still pass? Run them before adding new code.
- [ ] **Plan mismatch**: Does the milestone's plan still make sense given what you learned? Re-read the plan.
- [ ] **Scope mismatch**: Are you touching files outside this milestone's scope? If so, stop.
- [ ] **Assumption mismatch**: Is anything surprising about the current state? If so, investigate before proceeding.

Any mismatch detected → reorient before continuing.
