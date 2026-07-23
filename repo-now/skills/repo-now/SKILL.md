---
name: repo-now
description: Produce a grounded, read-only operational briefing for the current Git repository or branch. Use when the user asks what a repo or branch is for, what is outstanding, what work is in progress, where things stand, or what to work on next. Do not use for a walkthrough of a selected change (use explain) or a comprehensive repository health audit (use audit-and-improve).
---

# Repo Now

Give the user a current briefing from repository, Git, and GitHub evidence. Observe only unless the user separately authorizes changes.

## Guardrails

- Do not edit, clean, stage, commit, switch branches, fetch, pull, push, or change external systems.
- Do not run tests, builds, formatters, installers, or generators by default because they may change the worktree or caches.
- Treat uncommitted and untracked files as user-owned. Never infer permission to alter them.
- Prefer explicit unknowns over guesses. Label interpretations as inference.

## Workflow

1. Establish scope.
   - Use the current working directory unless the user names another repository or worktree.
   - Find and read the closest applicable `AGENTS.md` or equivalent repository instructions.
   - Run `scripts/repo_snapshot.sh [path]` for the standard bounded Git snapshot.

2. Understand purpose and intended work.
   - Inspect the root README, manifest, task runner, and only the relevant specs, plans, roadmap, or design docs.
   - Inspect recent commits and the diff summary against the default-branch candidate.
   - Search for focused TODOs only when they help answer the request; a TODO count is not a roadmap.

3. Add remote evidence when available.
   - If `gh` exists, is authenticated, and the repository is on GitHub, use read-only `gh repo view`, `gh pr view` or `gh pr list`, and `gh run list` queries.
   - Confirm the default branch from GitHub when possible. Otherwise call the helper result a candidate.
   - Report unavailable or stale remote evidence; never fetch merely to refresh it.

4. Assess validation evidence.
   - Read the task runner and `.github/workflows` when test commands or CI coverage are unclear.
   - Use existing CI results and repository artifacts as evidence. State that local tests were not run unless the user asked for them.

5. Synthesize.
   - Separate observed facts from inference and unresolved questions.
   - Explain dirty worktree state without claiming ownership or completion.
   - Rank at most three next actions by leverage, dependency order, and ability to unblock current work.
   - If the evidence does not support a recommendation, say what single missing check would resolve it.

## Output

Lead with a concise answer to the user's exact question, then cover:

- **Now:** purpose, branch, worktree condition, and current line of work.
- **Outstanding:** concrete unfinished, blocked, review, CI, or roadmap items with evidence.
- **Next:** one to three ranked actions, each with the reason it comes next.
- **Unknowns:** only material gaps or stale evidence.

Keep the briefing proportional. This skill orients current work; it does not perform a deep audit or narrate every changed line.
