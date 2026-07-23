---
name: sync-well
description: Safely inspect and reconcile a local Git branch with its upstream before pulling or merging. Use when a user reports divergent branches, asks whether local work exists, wants to sync local and remote changes without losing either side, or needs a recommendation among fast-forwarding, merging, and stopping for review. Do not use once a merge or rebase is already in progress; use the merge-conflict workflow instead.
---

# Sync Well

Preserve both committed and uncommitted work while establishing what Git can safely do. Treat inspection, network refresh, reconciliation, commit, and push as separate authorization boundaries.

## Inspect

1. Run `scripts/inspect_sync.sh [repository]`. It is read-only and uses only current local refs.
2. If it reports an in-progress merge, rebase, cherry-pick, or revert, stop and use the merge-conflict workflow.
3. Confirm the intended branch and worktree. A branch checked out in another worktree must be handled there.
4. Show the user the branch/upstream, staged and unstaged state, untracked files, ahead/behind counts, merge base, and all reported path overlaps.

## Refresh Remote State

Fetching changes remote-tracking refs, so keep it visible:

```sh
/usr/bin/git remote -v
/usr/bin/git fetch --prune <remote>
scripts/inspect_sync.sh .
```

Fetch only when network access is allowed. Derive `<remote>` from the configured upstream; do not assume `origin`. Never claim the comparison is current if fetch failed or was skipped.

## Recommend

- **Fast-forward only:** Recommend `/usr/bin/git merge --ff-only <upstream>` when behind-only, on the intended worktree, and clean. Do not use a plain `git pull`, because configured pull behavior is ambiguous.
- **Merge:** Recommend `/usr/bin/git merge <upstream>` when histories diverge, the tree is clean, and both histories must be preserved. Explain overlapping committed paths and the conflict risk. A normal merge may create a commit, so obtain explicit authorization first.
- **Stop for choice:** Stop when the branch or upstream is unclear, histories are unrelated, the tree is dirty, another operation is active, the wrong worktree is open, or uncommitted work overlaps remote-only paths. Review the actual diffs before asking whether work should be kept.
- **Ahead only:** Report that syncing needs no inbound reconciliation. Ask separately before pushing; do not infer publication permission.
- **Up to date:** Report that no reconciliation is needed.

Path overlap predicts risk, not certainty. Renames, directory moves, generated files, submodules, and semantic conflicts can matter even without an exact-path overlap.

A dirty tree does not block fetch or inspection, but it does block inbound
reconciliation. Never suggest discarding or stashing work merely to make the
tree clean; establish how the user wants it preserved before proposing a merge.

## Reconcile and Verify

Execute only the exact strategy the user authorized. Never reset, restore, rebase, force-push, discard, stash, delete, commit, or push without explicit authorization for that action.

After an authorized fast-forward or merge, rerun the helper and `/usr/bin/git diff --check`. Report the resulting ahead/behind state, worktree state, and whether further commit or push authorization is needed. Run project tests only when reconciliation produced content changes whose risk warrants them.

## Helper

`scripts/inspect_sync.sh` performs no fetch and no writes. It prints pairwise exact-path overlaps among local-only commits, remote-only commits, and staged, unstaged, or untracked work.
