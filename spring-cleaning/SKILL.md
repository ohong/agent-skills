---
name: spring-cleaning
description: Inspect Mac disk use, identify recoverable space, and carry out scoped cleanup with verification. Use for low-storage or disk-cleanup requests; keep requests for plans or explanations read-only.
---

# Spring Cleaning

Recover useful disk space and verify the result. A list of suggestions does not
complete an authorized cleanup request. Keep plan-only requests read-only.

## Inspect a bounded scope

1. Establish the requested target, such as enough free space for an update.
   Use the user's report and available local evidence; do not demand a screenshot.
2. Measure current available space on the affected volume. Inspect likely large
   targets first, based on the report and actual directories present.
3. Limit each scan to named paths and a finite timeout. Expand only when results
   justify it. Avoid a recursive whole-home or root scan by default.
4. Preserve permission errors, missing volumes, partial scans, and timeouts.
   An unreadable directory is unknown, not empty. Do not hide stderr.

Use the stdlib helper for explicitly named targets or repositories:

```bash
python3 scripts/inventory.py --path '/absolute/candidate' --repo '/absolute/repository'
```

Paths and repositories can repeat. The helper refuses symlink paths, bounds each
command and the whole run, and emits JSON. It never deletes, fetches, or assigns
a safe-to-delete verdict. Read its errors and limitations before using results.
Directory sizes are estimates of allocated blocks; they are not promised recovery.
Parent/child overlap, APFS clones, snapshots, and shared blocks prevent summing them.

## Select concrete candidates

Present a short, ranked set of exact paths or app-managed objects. For each, state:

- Measured size, or why its size is unknown.
- What it contains and which evidence supports removal or offloading.
- What must be preserved, restored, or checked before removal.
- The exact action and a useful verification check.

Read [category guidance](references/categories.md) only for relevant categories.
Read [the worktree process](references/worktrees.md) before any Git or Codex
worktree removal or metadata pruning. Clean Git status alone never proves disuse.

Favor large, well-understood candidates with low recovery cost. Do not invent
gigabyte estimates, time estimates, or age thresholds that imply safe deletion.
Cloud sync is not an independent backup; deletions may propagate to other devices.
Confirm actual recoverability for valuable data before proposing its removal.

## Execute within the user's scope

Carry existing authorization forward. If exact targets are already authorized,
inspect them and proceed without repetitive blanket approval questions. If scope
is unresolved, finish the read-only inspection and present concrete targets for
the user's decision before deleting them. A screenshot alone authorizes inspection.

Prefer supported app removal and package-manager cleanup over deleting internal
folders. Generate commands only for inspected, exact targets. Use quoted paths,
no broad globs, and no force flags that bypass a discovered protection.
Moving items to Trash is reversible but does not reclaim space until emptied.
Empty only the reviewed items within the user's scope; do not clear unrelated Trash.

After each useful batch, remeasure the same volume and run the relevant functional
check. Stop when the requested target is met. If no target was given, finish the
agreed candidates and report further options without expanding deletion scope.

## Close with evidence

Report actions actually completed and the measured change in available bytes.
Separate verified recovery from candidate-size estimates and remaining blockers.
Concurrent writes and APFS accounting can affect the observed delta; say so when
it prevents attributing recovery. State relevant checks actually run and any
unverified restoration or application behavior. Do not promise future cleanup.

For macOS storage interpretation, consult [Apple's storage guidance](https://support.apple.com/en-us/102624).
“System Data” is a storage category, not a directory to delete.
