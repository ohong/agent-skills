#!/bin/bash

GIT=/usr/bin/git
repo=${1:-.}
export GIT_OPTIONAL_LOCKS=0

root=$("$GIT" -C "$repo" rev-parse --show-toplevel 2>/dev/null) || {
  printf 'error=not-a-git-worktree\n' >&2
  exit 2
}

append_unique() {
  local value=$1
  local item
  for item in "${uncommitted_paths[@]}"; do
    if [[ "$item" == "$value" ]]; then
      return
    fi
  done
  uncommitted_paths+=("$value")
}

print_paths() {
  local label=$1
  shift
  local path
  printf '%s_count=%d\n' "$label" "$#"
  for path in "$@"; do
    printf '%s_path=%q\n' "$label" "$path"
  done
}

print_local_remote_overlap() {
  local matches=()
  local left_path right_path

  for left_path in "${local_paths[@]}"; do
    for right_path in "${remote_paths[@]}"; do
      if [[ "$left_path" == "$right_path" ]]; then
        matches+=("$left_path")
        break
      fi
    done
  done
  print_paths local_remote_overlap "${matches[@]}"
}

print_local_uncommitted_overlap() {
  local matches=()
  local left_path right_path

  for left_path in "${local_paths[@]}"; do
    for right_path in "${uncommitted_paths[@]}"; do
      if [[ "$left_path" == "$right_path" ]]; then
        matches+=("$left_path")
        break
      fi
    done
  done
  print_paths local_uncommitted_overlap "${matches[@]}"
}

print_remote_uncommitted_overlap() {
  local matches=()
  local left_path right_path

  for left_path in "${remote_paths[@]}"; do
    for right_path in "${uncommitted_paths[@]}"; do
      if [[ "$left_path" == "$right_path" ]]; then
        matches+=("$left_path")
        break
      fi
    done
  done
  print_paths remote_uncommitted_overlap "${matches[@]}"
}

branch=$("$GIT" -C "$root" symbolic-ref --quiet --short HEAD 2>/dev/null || true)
upstream=$("$GIT" -C "$root" rev-parse --abbrev-ref --symbolic-full-name '@{upstream}' 2>/dev/null || true)
head_oid=$("$GIT" -C "$root" rev-parse --verify HEAD 2>/dev/null || true)
git_dir=$("$GIT" -C "$root" rev-parse --absolute-git-dir)

operation=none
if [[ -f "$git_dir/MERGE_HEAD" ]]; then
  operation=merge
elif [[ -d "$git_dir/rebase-merge" || -d "$git_dir/rebase-apply" ]]; then
  operation=rebase
elif [[ -f "$git_dir/CHERRY_PICK_HEAD" ]]; then
  operation=cherry-pick
elif [[ -f "$git_dir/REVERT_HEAD" ]]; then
  operation=revert
fi

printf 'repository=%q\n' "$root"
printf 'branch=%q\n' "${branch:-DETACHED}"
printf 'upstream=%q\n' "${upstream:-NONE}"
printf 'head=%q\n' "${head_oid:-UNBORN}"
printf 'operation=%s\n' "$operation"
printf '%s\n' 'status_begin'
"$GIT" -C "$root" status --short --branch
printf '%s\n' 'status_end'
printf '%s\n' 'worktrees_begin'
"$GIT" -C "$root" worktree list --porcelain
printf '%s\n' 'worktrees_end'

staged_paths=()
while IFS= read -r -d '' path; do
  staged_paths+=("$path")
done < <("$GIT" -C "$root" diff --cached --name-only -z)

unstaged_paths=()
while IFS= read -r -d '' path; do
  unstaged_paths+=("$path")
done < <("$GIT" -C "$root" diff --name-only -z)

untracked_paths=()
while IFS= read -r -d '' path; do
  untracked_paths+=("$path")
done < <("$GIT" -C "$root" ls-files --others --exclude-standard -z)

uncommitted_paths=()
for path in "${staged_paths[@]}" "${unstaged_paths[@]}" "${untracked_paths[@]}"; do
  append_unique "$path"
done

local_paths=()
remote_paths=()
merge_base=
ahead=0
behind=0

if [[ -n "$head_oid" && -n "$upstream" ]]; then
  counts=$("$GIT" -C "$root" rev-list --left-right --count "HEAD...$upstream")
  ahead=${counts%%[[:space:]]*}
  behind=${counts##*[[:space:]]}
  merge_base=$("$GIT" -C "$root" merge-base HEAD "$upstream" 2>/dev/null || true)

  if [[ -n "$merge_base" ]]; then
    while IFS= read -r -d '' path; do
      local_paths+=("$path")
    done < <("$GIT" -C "$root" diff --name-only -z "$merge_base" HEAD)
    while IFS= read -r -d '' path; do
      remote_paths+=("$path")
    done < <("$GIT" -C "$root" diff --name-only -z "$merge_base" "$upstream")
  else
    while IFS= read -r -d '' path; do
      local_paths+=("$path")
    done < <("$GIT" -C "$root" ls-tree -r --name-only -z HEAD)
    while IFS= read -r -d '' path; do
      remote_paths+=("$path")
    done < <("$GIT" -C "$root" ls-tree -r --name-only -z "$upstream")
  fi
fi

printf 'ahead=%s\n' "$ahead"
printf 'behind=%s\n' "$behind"
printf 'merge_base=%q\n' "${merge_base:-NONE}"
printf '%s\n' 'local_commits_begin'
if [[ -n "$head_oid" && -n "$upstream" ]]; then
  "$GIT" -C "$root" log --format='%H %s' "$upstream..HEAD"
fi
printf '%s\n' 'local_commits_end'
printf '%s\n' 'remote_commits_begin'
if [[ -n "$head_oid" && -n "$upstream" ]]; then
  "$GIT" -C "$root" log --format='%H %s' "HEAD..$upstream"
fi
printf '%s\n' 'remote_commits_end'
print_paths staged "${staged_paths[@]}"
print_paths unstaged "${unstaged_paths[@]}"
print_paths untracked "${untracked_paths[@]}"
print_paths local_only "${local_paths[@]}"
print_paths remote_only "${remote_paths[@]}"
print_local_remote_overlap
print_local_uncommitted_overlap
print_remote_uncommitted_overlap

recommendation=stop
reason=review-required
if [[ "$operation" != none ]]; then
  reason=operation-in-progress
elif [[ -z "$branch" ]]; then
  reason=detached-or-unborn
elif [[ -z "$upstream" ]]; then
  reason=no-upstream
elif [[ -z "$merge_base" ]]; then
  reason=no-common-ancestor
elif (( ${#uncommitted_paths[@]} > 0 )); then
  reason=uncommitted-work
elif (( ahead == 0 && behind == 0 )); then
  recommendation=none
  reason=up-to-date
elif (( ahead == 0 && behind > 0 )); then
  recommendation=ff-only
  reason=behind-only-clean
elif (( ahead > 0 && behind > 0 )); then
  recommendation=merge
  reason=diverged-clean
elif (( ahead > 0 && behind == 0 )); then
  reason=ahead-only-push-is-separate
fi

printf 'recommendation=%s\n' "$recommendation"
printf 'reason=%s\n' "$reason"
