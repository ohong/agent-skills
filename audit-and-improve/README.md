# Audit & Improve

A Claude Code plugin that deeply analyzes a repository and produces an honest,
evidence-based audit plus a prioritized, actionable improvement plan.

It works in four phases — **Repo Map → Audit Report → Improvement Strategy →
Task Plan** — grounding every finding in real `file:line` citations, rating each
by severity, and ending with a milestone'd execution plan and flagged quick wins.
The audit is **analysis-only** (it never edits code) and finishes by offering to
execute the plan as a separate, opt-in step.

The instructions are tool-agnostic — they rely only on reading files, searching
the codebase, and running read-only shell commands — so the same skill works in
Claude Code, Codex, Cursor, and other AI coding agents.

## Installation (Claude Code)

### From the marketplace

```
/plugin marketplace add ohong/agent-skills
/plugin install audit-and-improve@ohong-skills
```

### From a local clone

```bash
git clone https://github.com/ohong/agent-skills.git
claude --plugin-dir ./agent-skills/audit-and-improve
```

Or, in a running session:

```
/plugin install --dir /path/to/agent-skills/audit-and-improve
```

## Installation (Codex CLI)

Codex doesn't use Claude Code plugins, but the skill is just a markdown prompt.
Drop its body into Codex's custom-prompts directory to expose it as a slash
command:

```bash
mkdir -p ~/.codex/prompts
# copy the skill body (the YAML frontmatter is Claude-specific and can stay or be trimmed)
cp /path/to/agent-skills/audit-and-improve/skills/audit-and-improve/SKILL.md \
   ~/.codex/prompts/audit-and-improve.md
```

Then run `/audit-and-improve` inside Codex.

## Usage

```
/audit-and-improve:audit-and-improve            # audit the current repo
/audit-and-improve:audit-and-improve src/core   # scope to a subdirectory
/audit-and-improve:audit-and-improve --focus security
```

The full report is written to `docs/audit-<YYYY-MM-DD>.md` (or `AUDIT.md` at the
repo root); the Executive Summary and quick wins are posted in chat.
