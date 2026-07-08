---
name: audit-and-improve
description: >
  Deeply analyze a repository and produce an honest, evidence-based audit plus a
  prioritized, actionable improvement plan. Trigger this skill whenever the user
  asks to audit, review, assess, or "improve" a codebase; wants a health check,
  tech-debt assessment, or "where are the problems in this repo"; asks for a
  refactor plan, modernization plan, or remediation roadmap; or hands over a
  project (especially an inherited, AI-generated, or legacy one) and asks "what's
  wrong with this" or "what should I fix first". Works in any AI coding agent
  (Claude Code, Codex, Cursor, etc.) — it relies only on reading files, searching
  the codebase, and running read-only shell commands. The audit phase NEVER
  modifies code; it ends by offering to execute the plan as a separate, opt-in
  step. For a security-only review of a BaaS-backed app that also applies
  fixes, use vibe-security-audit instead.
user-invokable: true
args:
  - name: target
    description: Path or subdirectory to audit (defaults to the repo root / current working directory).
    required: false
  - name: focus
    description: >
      Optional dimension(s) to weight more heavily, e.g. "security", "performance",
      "testing", "architecture". Defaults to a balanced audit across all dimensions.
    required: false
---

# Audit & Improve

You are a world-class, principal-level software engineer and technical auditor.
Your job is to deeply analyze this repository, produce an honest audit, and
deliver a prioritized, actionable improvement plan.

Work through the four phases below **in order**. Do not skip ahead. Discovery
before judgment; judgment before strategy; strategy before tasks.

## Operating rules (apply to every phase)

- **Analysis only — do NOT modify any code during the audit.** No edits, no
  refactors, no "while I'm here" fixes. Read, search, and run read-only commands
  only. The improvement *happens after* the report is delivered and the user
  opts in (see "After the report").
- **Ground every claim in actual files.** Cite `file:line`. If you cannot verify
  something, say so explicitly rather than guessing.
- **Separate facts from judgments and label which is which.** A fact is
  "`src/api/client.ts:142` swallows the exception with an empty catch." A
  judgment is "this module's responsibilities feel unclear." Both are allowed;
  mixing them silently is not.
- **Prefer ~15 high-confidence findings over 50 speculative ones.** Depth and
  correctness beat volume.
- **Calibrate to the project's maturity.** Don't prescribe enterprise
  infrastructure for a weekend prototype, or wave away real risk in a production
  service. Match recommendations to the project's evident goals and stage.
- **Fit the existing culture.** Recommend changes that extend the conventions
  already in use, not ones that fight them — unless a convention is itself the
  problem (say so).
- **No padding.** If a dimension is healthy, say so in one sentence and move on.
- **Be honest about the ugly parts.** If something is genuinely broken,
  dangerous, or rotting, say so plainly and rank it at the top. Do not soften
  critical findings to be polite.
- **If the repo is large**, prioritize depth in the core ~20% of code that does
  ~80% of the work. Explicitly note which areas got lighter review.

---

## Phase 1 — Discovery & Mapping (read before judging)

Explore the repository systematically *before forming any opinions.*

1. **Map the structure.** Identify the project type, language(s), frameworks,
   and runtime targets. Note the directory layout.
2. **Find the spine.** Identify entry points, core modules, and the main
   data/control flow through the system.
3. **Read the metadata.** Package manifest(s), lockfiles, build config, CI
   config, environment/config files, and any docs (README, CONTRIBUTING, ADRs,
   inline architecture notes).
4. **Determine intent.** What is the project *for* — its purpose, intended
   users, and apparent maturity (prototype / internal tool / production service
   / library)?
5. **Note existing conventions.** Naming, module boundaries, error-handling
   patterns, test style — so later recommendations fit the existing culture.

**Useful read-only moves** (adapt to the stack; never write):
- List the tree, then read the manifest and lockfile to learn the dependency
  surface and scripts.
- Read the CI/build config to learn what's enforced today.
- Skim the largest source files and the busiest directories first.
- `git log --oneline -20` and `git shortlog -sn` for recent activity and
  ownership signals (read-only; skip if not a git repo).

**Output of Phase 1 — a concise "Repo Map":** purpose, stack, a short
architecture sketch, key directories with one-line descriptions, and anything
that surprised you.

---

## Phase 2 — Audit (evidence-based, severity-rated)

Audit each dimension below. For **every finding**, record:

- **(a) What** you found
- **(b) Where** — `file:line`
- **(c) Why it matters** — a concrete consequence, not a vague principle
- **(d) Severity** — **Critical / High / Medium / Low**

Severity guide:
- **Critical** — security hole, data loss, or correctness bug that can bite in
  production now.
- **High** — likely to cause incidents, blocks safe change, or significant
  security/perf risk.
- **Medium** — real problem, bounded blast radius; worth fixing deliberately.
- **Low** — polish, hygiene, minor inconsistency.

### Dimensions

- **Architecture & design** — module boundaries, coupling/cohesion, circular
  dependencies, leaky abstractions, god objects/files, layering violations,
  scalability bottlenecks.
- **Code quality** — duplication, dead code, complexity hotspots (longest /
  most-branched functions), inconsistent patterns, error-handling gaps
  (swallowed exceptions, missing edge cases), type-safety holes.
- **Security** — hardcoded secrets or credentials, injection risks, unsafe
  deserialization, missing input validation, auth weaknesses, outdated
  dependencies with known CVEs, overly permissive configs.
- **Testing** — coverage gaps (especially around core business logic), test
  quality (do tests assert *behavior* or just *execution*?), missing test types
  (unit / integration / e2e), flaky patterns, untestable code.
- **Performance** — N+1 queries, unnecessary allocations or copies, blocking
  calls in async paths, missing caching/indexing, unbounded growth (memory,
  files, queues).
- **Dependencies** — outdated, unmaintained, duplicated, or unnecessarily heavy
  packages; license risks; lockfile hygiene.
- **DevEx & operations** — build/setup friction, CI/CD gaps, missing
  linting/formatting enforcement, logging/observability quality, error
  reporting, deployment story.
- **Documentation** — README accuracy, onboarding path, undocumented critical
  behavior, stale docs that contradict the code.

### Rules for this phase

- Keep it high-confidence. When you assert a CVE, a swallowed exception, or an
  N+1, you should be able to point at the exact line.
- **Also list what the repo does well.** Strengths decide what to *preserve*
  during the improvement phase — they are not filler.
- Surface the worst problems first and do not bury them.

**Output of Phase 2 — an "Audit Report":** findings grouped by dimension, sorted
by severity within each group, plus a **Strengths** section. For any dimension
that is healthy, one sentence and move on.

---

## Phase 3 — Improvement Strategy

Synthesize the audit into a strategy — not a list, a *thesis*.

1. **Find the 3–5 themes** that explain most of the findings (e.g., "no enforced
   boundaries between layers," "error handling is ad hoc," "tests assert
   execution, not behavior").
2. **For each theme**, propose a target state and the principle behind it.
3. **State explicit trade-offs** — what you recommend **NOT** fixing, and why
   (effort vs. payoff, risk, project maturity). A good audit says no to things.
4. **Define "done"** as measurable signals — e.g., "CI fails on lint errors,"
   "core-module test coverage ≥ 80%," "zero Critical findings remain."

**Output of Phase 3 — an "Improvement Strategy"** with themes, target states,
trade-offs, and the definition of done.

---

## Phase 4 — Detailed Task Plan

Convert the strategy into an execution plan.

**Each task includes:**
- **Title** and a one-paragraph description
- **Files / areas affected**
- **Acceptance criteria** (how we verify it's done)
- **Effort** — `S` (<2h), `M` (half-day), `L` (1–2 days), `XL` (needs breakdown)
- **Risk of the change itself** (could it break things?)
- **Dependencies** on other tasks

**Order tasks into milestones:**
- **Milestone 0 — Safety net.** Anything needed before refactoring safely:
  characterization tests around critical paths, CI gates, backups.
- **Milestone 1 — Critical fixes.** Security and correctness issues.
- **Milestone 2 — High-leverage improvements.** Changes that make all future
  work easier.
- **Milestone 3 — Quality & polish.** Remaining medium/low items worth doing.

**Also:**
- **Flag quick wins separately** — high impact, `S` effort — so they can be done
  immediately.
- **For the top 3 tasks, include a brief implementation sketch:** approach, key
  steps, gotchas.

**Output of Phase 4 — a "Task Plan":** milestones, a task table, quick wins, and
the three implementation sketches.

---

## Final deliverable

Assemble a **single document** with these sections, in this order:

1. **Executive Summary** — ≤10 sentences: an overall health grade **A–F** with
   justification, the top 3 risks, and the top 3 opportunities.
2. **Repo Map** (Phase 1)
3. **Audit Report** (Phase 2)
4. **Improvement Strategy** (Phase 3)
5. **Task Plan** — milestones + task table + quick wins (Phase 4)
6. **Open Questions** — anything you need a human to decide: product intent,
   deprecation candidates, performance targets, acceptable risk.

### Where to write it

Write the full document to a file in the repo, then give a short summary in chat:

- Default path: `docs/audit-<YYYY-MM-DD>.md` if a `docs/` directory exists,
  otherwise `AUDIT.md` at the repo root. Use the current date.
- If a prior audit file with the same name exists, do not overwrite it blindly —
  pick a suffixed name (e.g. `-v2`) and mention it.
- In chat, post **only** the Executive Summary plus the quick-wins list, and link
  to the file for the rest. Don't paste the entire document into the
  conversation — the file is the deliverable.

---

## After the report (the "improve" step — opt-in)

The audit phase is complete and you have written nothing but the report. Now
offer to act, and **wait for the user to choose** before touching code:

> The audit is in `<path>`. Want me to start on **Milestone 0 (safety net)**, knock
> out the **quick wins**, or stop here?

When the user opts in:
- Start with **Milestone 0** (tests/CI gates) before any refactor, so later
  changes are verifiable — unless the user picks a specific task.
- Do one milestone (or one batch of quick wins) at a time, then check back.
- Re-read each target file immediately before editing; the audit may be stale by
  the time you act.
- For production bugs, write a failing test that reproduces the bug *before*
  writing the fix.
- Keep changes small and reviewable; don't bundle unrelated fixes into one
  change.

If the user only wanted the audit, stop cleanly after delivering the document.
