---
name: explain
description: Walk the user through code changes made by coding agents so they understand what changed, why decisions were made, what trade-offs were accepted, what alternatives were or could have been considered, and what risks or follow-up choices remain. Use when the user invokes /explain, asks to understand an agent-made diff, branch, PR, commit, worktree, implementation, refactor, migration, feature, bug fix, or "what happened here" in a project.
---

# /explain

Help the user build enough understanding to participate in the next loop, not merely approve or reject a diff. Treat the output as a guided walkthrough of agent-made work: background first, intuition before details, code in a sensible order, and explicit checks for understanding.

## Operating Principles

- Ground every claim in the real repo state. Read the diff, surrounding code, tests, plans, PR text, commit messages, and relevant docs before explaining.
- Preserve the user's worktree. Do not modify code, regenerate files, or clean up artifacts unless the user explicitly asks for edits.
- Separate evidence from inference. Say "the diff shows", "the commit message says", "I infer", or "unknown" instead of inventing rationale.
- Explain to create participation. The goal is that the user can suggest the next change, spot a weak assumption, or discuss the design fluently.
- Prefer a literate diff over file-order narration. Group changes by concept, data flow, user flow, or decision, not alphabetically by path.
- Use small examples, diagrams, tables, and concrete before/after behavior when they reduce mental load.

## Scope Discovery

1. Determine the change set.
   - If the user names a PR, branch, commit, range, file, or worktree, use that scope.
   - If no scope is named, inspect the current repo: `git status --short`, current branch, default branch, merge base, uncommitted diff, and commits ahead of the base branch.
   - In multi-worktree repos, run `git worktree list` before assuming the current checkout is the whole story.
   - If there is no Git repo or no clear change set, ask one concise question for the scope.

2. Gather source material.
   - Diff/stat: `git diff --stat`, `git diff`, `git diff --cached`, or `git diff <base>...HEAD`.
   - History: `git log --oneline --decorate --graph --max-count=30` and relevant `git show` output.
   - Project intent: README, docs, plans, ADRs, issue links, PR description, TODOs, and agent notes.
   - Verification: tests run, snapshots, build logs, lint results, CI status, manual browser checks, and any failing commands.
   - Surrounding implementation: call sites, types, tests, migrations, config, and previous patterns the change builds on or breaks.

3. Identify the audience and depth.
   - Default to a concise walkthrough first, then drill down.
   - If the change is large, open with a two-minute map and ask which area the user wants to unpack first.
   - If the user is preparing to review, merge, hand off, or continue implementation, bias toward risks, decision points, and next actions.

## Walkthrough Structure

Use this order unless the user asks for a different format:

1. **Context**
   - What this part of the system did before.
   - The vocabulary, data model, lifecycle, or user flow needed to understand the change.
   - The smallest useful mental model of the system.

2. **Intent**
   - The problem the agent appears to be solving.
   - The user-visible or developer-visible behavior that should change.
   - Any stated requirements from plans, issues, prompts, or commit messages.

3. **Change Map**
   - Group files by role: entry points, domain logic, state/data layer, UI, tests, config, migrations, scripts, docs.
   - Explain the dependency order: what calls what, what data moves where, and which parts are supporting changes.
   - Call out what did not change if that boundary matters.

4. **Decision Log**
   - List the meaningful implementation decisions.
   - For each decision, include:
     - Decision: what was chosen.
     - Evidence: file/line, diff hunk, commit text, test, or plan that proves it.
     - Rationale: why this choice likely fits the goal.
     - Trade-off: what became simpler, harder, faster, slower, safer, or riskier.
     - Alternatives: options shown in the source material, or plausible alternatives clearly labeled as analysis.
     - Residual risk: what would need testing, monitoring, or future cleanup.

5. **Code Walk**
   - Walk the code in execution order or concept order.
   - Quote only small snippets when needed; otherwise reference files and line numbers.
   - Explain non-obvious control flow, state transitions, data transformations, error handling, and edge cases.
   - For UI changes, connect component state to the visible interaction and include screenshots or browser checks when useful.

6. **Verification**
   - State what was actually verified and by which command or UI action.
   - Distinguish passing tests from untested assumptions.
   - Explain what the tests prove and what they do not prove.

7. **Understanding Check**
   - Ask 3-5 medium-difficulty questions or prompts that reveal whether the user understands the change.
   - Make the questions practical, not gotchas: "What would break if...", "Where would you add...", "Why did this branch need...".
   - Provide answers after the user tries, or include collapsed/clearly separated answers if producing a written packet.

## Decision Analysis Heuristics

Look for decisions at these pressure points:

- Public API shape, route contracts, CLI flags, schemas, migrations, generated types, and backward compatibility.
- State ownership, cache invalidation, persistence, optimistic updates, retries, and error boundaries.
- Framework conventions versus custom abstractions.
- Shared helper extraction versus local duplication.
- Compatibility with existing tests, fixtures, seed data, mocks, and analytics.
- Security, privacy, auth, permissions, and secret handling.
- Performance choices: query shape, bundling, hydration, streaming, pagination, concurrency, background jobs.
- Operational behavior: logging, metrics, feature flags, rollback paths, deployment config, and data migrations.

When alternatives are not documented, present them as "alternatives worth comparing now", not as things the agent definitely considered.

## Teaching Tools

Use the lightest tool that helps understanding:

- **Diagram:** Use Mermaid for system flow, sequence, or state-machine diagrams when relationships are easier to see than read.
- **Toy example:** Create a tiny input/output example for parsing, transforms, queries, reducers, permissions, or scheduling logic.
- **Trace:** Follow one realistic request, click, command, event, or record through the changed code.
- **Micro-world:** For complex algorithms or stateful behavior, propose or create a temporary scratch reproduction only when the user wants an interactive understanding aid. Keep it outside the repo unless asked.
- **Comparison table:** Use for alternatives, trade-offs, before/after behavior, or changed responsibilities.

## Output Modes

Default to a conversational walkthrough in the current thread.

If the user asks for a durable artifact, create a Markdown explainer outside the repo by default, named `/tmp/YYYY-MM-DD-explain-<slug>.md`, unless they request a repo doc or another destination. Include:

- Summary
- Background
- Intent
- Change map
- Decision log
- Literate code walkthrough
- Verification and open risks
- Understanding check

If the user asks for an HTML, Notion, or other rich packet, adapt the same structure. Make rich outputs self-contained and readable on mobile, but do not let formatting work replace repo investigation.

## Final Response Shape

End with:

- The strongest mental model of the change in 2-4 sentences.
- The highest-leverage decision or trade-off to discuss next.
- Any unverified assumptions or missing evidence.
- A short invitation to drill into one named area when a large change still has branches worth unpacking.
