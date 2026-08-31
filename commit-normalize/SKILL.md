---
name: commit-normalize
description: >
  Standardize commit messages to Conventional Commits format. Use this skill when
  the user runs /commit, asks to commit changes, or requests commit message cleanup.
  Detects informal, inconsistent, or freeform commit messages and rewrites them
  following the type(scope): description convention. Also trigger when reviewing
  git history and finding inconsistent message styles, or when the user asks to
  "fix commit messages," "clean up commits," "normalize commits," or "rewrite
  commit messages."
---

# Commit Message Normalizer

Rewrite commit messages to follow the [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) specification. Every commit message must match:

```
type(scope): subject

[optional body]

[optional footer(s)]
```

## Type Classification

Choose the most specific type. When in doubt, prefer `fix` over `chore` and `feat` over `refactor`.

| Type | When to use |
|------|-------------|
| `feat` | New feature, capability, or user-facing behavior |
| `fix` | Bug fix, error correction, regression fix |
| `refactor` | Code restructuring with no behavior change |
| `chore` | Maintenance — deps, configs, tooling, CI scripts |
| `docs` | Documentation only — README, comments, JSDoc, docstrings |
| `test` | Adding or updating tests with no production code change |
| `ci` | CI/CD pipeline changes — GitHub Actions, CircleCI, Jenkins |
| `style` | Formatting, whitespace, semicolons — no logic change |
| `perf` | Performance improvement with no behavior change |
| `build` | Build system changes — webpack, vite, tsconfig, Makefile |
| `revert` | Reverting a previous commit |

## Scope Inference

Derive scope from the files changed. Use the most specific meaningful scope:

- **Single directory changed:** Use that directory name — `feat(auth): ...`, `fix(api): ...`
- **Single file changed:** Use the module or component name — `fix(login-form): ...`, `docs(readme): ...`
- **Multiple directories in one domain:** Use the domain — `refactor(payments): ...`
- **Cross-cutting change:** Omit scope — `chore: update dependencies`
- **Monorepo packages:** Use the package name — `feat(web): ...`, `fix(cli): ...`

Keep scopes lowercase, kebab-case, and short (1-2 words). Use consistent scopes across a project — check recent git history for established scope names before inventing new ones.

## Subject Line Rules

1. **Lowercase start** — `fix(auth): handle expired tokens` not `Fix(auth): Handle expired tokens`
2. **Imperative mood** — "add," "fix," "remove" not "added," "fixes," "removing"
3. **No trailing period**
4. **72 characters max** (type + scope + colon + space + subject combined)
5. **Describe the what, not the how** — `feat(search): add fuzzy matching` not `feat(search): implement Levenshtein distance algorithm`

## Body

Optional. Use when the subject alone doesn't explain **why** the change was made.

- Separate from subject with one blank line
- Wrap at 72 characters
- Explain motivation and contrast with previous behavior
- Use bullet points for multiple items

## Footer

Optional. Use for:

- **Breaking changes:** `BREAKING CHANGE: removed legacy auth endpoint`
- **Issue references:** `Closes #123`, `Fixes #456`
- **Co-authors:** `Co-Authored-By: Name <email>`
- **Custom trailers:** As required by project conventions (e.g., `Nightshift-Task:`, `Signed-off-by:`)

Preserve any existing trailers/footers from the original message.

## Breaking Changes

Two ways to denote:

1. `!` after type/scope: `feat(api)!: change response format`
2. Footer: `BREAKING CHANGE: response format changed from XML to JSON`

Use both when the breaking change needs explanation.

## Pattern Reference

Common informal patterns and their conventional equivalents:

| Informal Message | Normalized |
|-----------------|------------|
| `updated README` | `docs(readme): update README` |
| `fixed bug` / `bugfix` | `fix: resolve [describe the actual bug]` |
| `WIP` / `work in progress` | `wip: [describe what's in progress]` — or better, squash before merge |
| `misc changes` / `various fixes` | Split into separate commits by type, or `chore: [describe the actual changes]` |
| `added new feature X` | `feat: add X` |
| `updated deps` / `bump packages` | `chore(deps): update dependencies` |
| `cleanup` / `refactoring` | `refactor: [describe what was restructured]` |
| `typo` / `fix typo` | `docs: fix typo in [location]` or `style: fix typo in [location]` |
| `linting` / `prettier` | `style: apply formatting` |
| `tests` / `add tests` | `test: add tests for [subject]` |
| `initial commit` | `chore: initialize project` |
| `remove unused code` | `refactor: remove unused [what]` |
| `oops` / `forgot to add` | Amend previous commit instead of creating a new one |
| `PR feedback` / `address comments` | `refactor: [describe the actual change made]` |
| `v2.1.0` / version-only | `chore(release): bump version to 2.1.0` |
| `merge branch X` | Keep as merge commit — do not rewrite merge messages |

## Rewriting Process

When normalizing a commit message:

1. **Read the diff** — Understand what actually changed. The diff is the source of truth, not the original message.
2. **Classify the type** — Match the change to the type table above.
3. **Infer scope** — Derive from changed files using the scope rules.
4. **Write the subject** — Imperative mood, lowercase, concise, no period.
5. **Add body if needed** — Only when the "why" isn't obvious from the subject.
6. **Preserve footers** — Keep existing trailers, issue refs, and co-author lines.
7. **Validate length** — Subject line must be ≤72 characters total.

## Examples

### Simple feature
```
Before: Added dark mode toggle to settings page
After:  feat(settings): add dark mode toggle
```

### Bug fix with context
```
Before: fix the login issue that users reported
After:  fix(auth): prevent session expiry during active use

        Users were being logged out mid-session because the token
        refresh timer was not reset on activity.

        Fixes #892
```

### Dependency update
```
Before: updated packages
After:  chore(deps): update react to 19.1 and next to 15.3
```

### Breaking change
```
Before: changed API response format
After:  feat(api)!: return JSON arrays instead of wrapped objects

        BREAKING CHANGE: all list endpoints now return raw arrays
        instead of { data: [], meta: {} } wrappers. Clients must
        update their response parsing.
```

### Multi-file refactor
```
Before: refactoring
After:  refactor(payments): extract shared validation logic

        Moved duplicate card validation from checkout and billing
        into a shared validator module.
```

## When NOT to Rewrite

- **Merge commits** — Leave auto-generated merge messages as-is.
- **Revert commits** — Keep the `Revert "..."` format generated by git.
- **Squash commits** — These are already being cleaned up as part of the squash.
- **Messages that already follow Conventional Commits** — Don't touch them.
