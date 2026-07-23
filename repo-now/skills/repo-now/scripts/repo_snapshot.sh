#!/bin/sh
set -u

export GIT_OPTIONAL_LOCKS=0
export LC_ALL=C

target=${1:-.}

if [ -x /usr/bin/git ]; then
  git_bin=/usr/bin/git
else
  git_bin=$(command -v git 2>/dev/null || true)
fi

if [ -z "$git_bin" ]; then
  printf '%s\n' "error: git is not available" >&2
  exit 127
fi

root=$("$git_bin" -C "$target" rev-parse --show-toplevel 2>/dev/null) || {
  printf 'error: not a Git worktree: %s\n' "$target" >&2
  exit 2
}

git_repo() {
  "$git_bin" -C "$root" "$@"
}

value_or_none() {
  if [ -n "$1" ]; then
    printf '%s\n' "$1"
  else
    printf '%s\n' "(none)"
  fi
}

branch=$(git_repo branch --show-current 2>/dev/null || true)
head=$(git_repo rev-parse --short=12 HEAD 2>/dev/null || true)
upstream=$(git_repo rev-parse --abbrev-ref --symbolic-full-name '@{upstream}' 2>/dev/null || true)
remote_names=$(git_repo remote 2>/dev/null || true)

printf '%s\n' "== repository =="
printf 'root: %s\n' "$root"
printf 'branch: '
value_or_none "$branch"
printf 'head: '
value_or_none "$head"
printf 'upstream: '
value_or_none "$upstream"
printf 'remotes: '
if [ -n "$remote_names" ]; then
  printf '%s\n' "$remote_names" | paste -sd, -
else
  printf '%s\n' "(none)"
fi

printf '\n%s\n' "== status =="
status=$(git_repo status --short --branch --untracked-files=normal 2>/dev/null || true)
if [ -n "$status" ]; then
  printf '%s\n' "$status" | sed -n '1,100p'
  status_lines=$(printf '%s\n' "$status" | wc -l | tr -d ' ')
  if [ "$status_lines" -gt 100 ]; then
    printf '... %s additional status lines omitted\n' "$((status_lines - 100))"
  fi
else
  printf '%s\n' "(clean)"
fi

printf '\n%s\n' "== worktrees =="
git_repo worktree list --porcelain 2>/dev/null | sed -n '1,120p'

printf '\n%s\n' "== recent commits =="
git_repo log -n 8 --date=short \
  --format='%h %ad %d %s' 2>/dev/null || printf '%s\n' "(no commits)"

default_ref=
default_source=
remote=
if [ -n "$upstream" ]; then
  remote=${upstream%%/*}
fi
if [ -z "$remote" ] && git_repo remote get-url origin >/dev/null 2>&1; then
  remote=origin
fi

if [ -n "$remote" ]; then
  default_ref=$(git_repo symbolic-ref --quiet --short "refs/remotes/$remote/HEAD" 2>/dev/null || true)
  if [ -n "$default_ref" ]; then
    default_source="remote HEAD"
  fi
fi

if [ -z "$default_ref" ]; then
  for candidate in origin/main origin/master main master; do
    if git_repo rev-parse --verify --quiet "$candidate^{commit}" >/dev/null 2>&1; then
      default_ref=$candidate
      default_source="conventional fallback"
      break
    fi
  done
fi

printf '\n%s\n' "== default branch comparison =="
if [ -z "$default_ref" ]; then
  printf '%s\n' "candidate: (unknown)"
  printf '%s\n' "comparison: unavailable"
else
  printf 'candidate: %s (%s)\n' "$default_ref" "$default_source"
  counts=$(git_repo rev-list --left-right --count "$default_ref...HEAD" 2>/dev/null || true)
  if [ -n "$counts" ]; then
    behind=$(printf '%s\n' "$counts" | awk '{print $1}')
    ahead=$(printf '%s\n' "$counts" | awk '{print $2}')
    printf 'ahead: %s\nbehind: %s\n' "$ahead" "$behind"
  else
    printf '%s\n' "ahead/behind: unavailable"
  fi
  printf '%s\n' "-- changed paths --"
  git_repo diff --name-status "$default_ref...HEAD" 2>/dev/null | sed -n '1,100p'
  printf '%s\n' "-- diff stat --"
  git_repo diff --stat "$default_ref...HEAD" 2>/dev/null | sed -n '1,80p'
fi

printf '\n%s\n' "== upstream comparison =="
if [ -z "$upstream" ]; then
  printf '%s\n' "(no upstream configured)"
else
  counts=$(git_repo rev-list --left-right --count "$upstream...HEAD" 2>/dev/null || true)
  if [ -n "$counts" ]; then
    behind=$(printf '%s\n' "$counts" | awk '{print $1}')
    ahead=$(printf '%s\n' "$counts" | awk '{print $2}')
    printf 'upstream: %s\nahead: %s\nbehind: %s\n' "$upstream" "$ahead" "$behind"
  else
    printf '%s\n' "comparison unavailable"
  fi
fi
