# Git and Codex worktree review

Use [Git's worktree documentation](https://git-scm.com/docs/git-worktree) when
command behavior is uncertain. Worktree removal and metadata pruning are distinct.

1. Identify the owning repository and inspect `git worktree list --porcelain -z`.
   The helper accepts explicit repositories and reports each registered worktree.
   Never delete the `~/.codex/worktrees` root or its children as generic caches.
2. Protect the main checkout, the current checkout, active work, locked worktrees,
   and unavailable external volumes. Inspect available Codex task state and process
   evidence to assess ownership and activity. Clean Git status does not prove
   inactivity. If activity cannot be established, report that uncertainty.
3. Inspect branch, HEAD, staged and unstaged changes, untracked files, and ignored
   files. Ignored `.env` files, databases, downloads, or build assets may be unique.
   Preserve required files outside the deletion target and verify the retained copy.
4. Inspect local branches and tags containing HEAD, excluding its own branch.
   No other containing ref exposes commits whose retention needs explicit review,
   even for a clean named branch. Detached commits need a verified retained ref
   before removal. Also verify retained refs will survive the proposed operation.
   The helper does not fetch: local remote-tracking refs may be stale. Distinguish
   proven unpushed commits from unknown remote freshness or publication state.
5. Present the exact worktree path, measured size, ownership evidence, retained
   files/refs, and unresolved checks. Proceed only within authorized target scope.
   Recheck status, HEAD, locks, and activity immediately before removal.
6. Remove an approved linked worktree with `git -C '/repo' worktree remove '/exact/path'`.
   Do not add `--force` to bypass dirty, locked, or ignored-file protections.
   Resolve refusal through preservation or a narrower action. Branch deletion is
   separate intent; do not couple it to worktree cleanup.
7. Verify registration and path removal, retained refs/files, and the same volume's
   available-space delta. Check the surviving project when relevant.

For metadata pruning, first run `git -C '/repo' worktree prune --dry-run --verbose`.
Inspect every candidate in the preview. Missing paths can mean an unmounted drive,
not stale registration. Lock legitimate unavailable worktrees only if authorized;
do not unlock them for cleanup. Prune only after the preview scope is justified
and authorized, then verify registrations. Pruning removes administrative records;
it does not remove existing working directories or promise meaningful disk recovery.

The helper is an inventory aid, not a removal gate. It cannot establish app activity,
backup quality, remote freshness, recursive submodule state, or file recoverability.
