# Git and Codex worktree review

Use [Git's worktree documentation](https://git-scm.com/docs/git-worktree) when
command behavior is uncertain. Worktree removal and metadata pruning are distinct.

1. Identify the owning repository and inspect `git worktree list --porcelain -z`.
   The helper accepts explicit repositories and reports each registered worktree.
   Never delete the `~/.codex/worktrees` root or its children as generic caches.
   For discovery, inspect bounded children of the configured Codex worktree root
   and their `.git` files, then cross-check ownership and registered paths.
   Unregistered folders remain unknown; inspect their contents and provenance.
2. Protect the main checkout, the current checkout, active work, locked worktrees,
   and unavailable external volumes. Inspect available Codex task state and process
   evidence to assess ownership and activity. Clean Git status does not prove
   inactivity. If activity cannot be established, report that uncertainty.
   Use fresh task/process evidence or the user's explicit declaration that the
   target is obsolete. Resolve unknown activity before removing that worktree.
   “Main checkout” means the repository's original checkout, not a branch named main.
3. Inspect branch, HEAD, staged and unstaged changes, untracked files, and ignored
   files. Ignored `.env` files, databases, downloads, or build assets may be unique.
   Status can summarize ignored directories; inspect their actual contents too.
   Preserve required files outside the deletion target and verify the retained copy.
   Check in-progress Git operations, submodules, and nested repositories separately;
   their local changes and commits may not appear in the parent status inventory.
4. Inspect local branches and tags containing HEAD, excluding its own branch.
   No other containing ref exposes commits whose retention needs explicit review,
   even for a clean named branch. Detached commits need a verified retained ref
   before removal. Also verify retained refs will survive the proposed operation.
   Create preservation refs or verified copies within existing preservation authority;
   do not add a new approval step when the user already authorized that preservation.
   The helper does not fetch: local remote-tracking refs may be stale. Distinguish
   proven unpushed commits from unknown remote freshness or publication state.
5. Present the exact worktree path, measured size, ownership evidence, retained
   files/refs, and unresolved checks. Proceed only within authorized target scope.
   Recheck status, HEAD, locks, and activity immediately before removal.
6. Remove an approved linked worktree with `git -C '/repo' worktree remove '/exact/path'`.
   Git can remove a worktree containing ignored files without `--force`; the prior
   ignored-file review is essential even when Git accepts removal. Do not add
   `--force` to bypass dirty or locked worktree protections.
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
