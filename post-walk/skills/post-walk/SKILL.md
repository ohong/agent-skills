---
name: post-walk
description: Process a local Apple Voice Memo into an archived transcript, project notes, tasks, todos, and drafts. Use only when explicitly asked to process a walk or commute memo.
---

# Post-Walk Memo Processor

Turn one voice memo into project context, engineering tasks, personal todos, and drafts — memo to final report with no pauses in between. Do not launch follow-on work unless explicitly asked.

## Pick the memo

- Argument is a file path → use it (expand `~`, verify it exists).
- Otherwise → newest `*.m4a` by mtime in `~/Library/Group Containers/group.com.apple.VoiceMemos.shared/Recordings/`. A non-path argument is a hint for naming/context/prioritization only.
- Report path, recording timestamp, and duration (`mdls`, `stat`, `ffprobe`, or `afinfo`). If older than ~12h, flag as possibly stale and proceed.

## Transcribe

Run `${CLAUDE_PLUGIN_ROOT}/skills/post-walk/scripts/transcribe.sh <audio-file> [output.txt]` (path is relative to this skill directory outside Claude Code). It transcribes via fal.ai Wizper, requires `FAL_KEY` (env, `./.env`, `./.env.local`, or `~/.zshenv`/`~/.zprofile`/`~/.zshrc`), accepts m4a, prints only the transcript path on success, and errors to stderr. Don't paste raw API responses into the report unless explaining a failure.

## Archive

One walk folder: `docs/walks/YYYY-MM-DD-<short-slug>/` inside a git repo, else `~/walks/YYYY-MM-DD-<short-slug>/`. Slug = strongest memo theme (or the user's hint); fall back to `walk-notes`.

Files:

- `transcript.raw.txt` — raw helper output, unchanged.
- `transcript.md` — cleaned transcript (fix obvious ASR errors, add paragraph breaks, preserve the speaker's words) plus a short summary and a `Misc` section for anything unclassifiable.
- `docs/<n>-<slug>.md` — one standalone agent-context doc per substantial idea/theme.
- `tasks.md` — engineering tasks.
- `todos.md` — only for items Things MCP couldn't take.
- `drafts.md` — sendable/postable drafts.

## Buckets

Read the whole transcript before partitioning. Nothing gets dropped; never invent content.

- **Context docs**: per substantial idea, write broad, deep agent context — problem, background, goals, constraints, useful facts, possible approaches, open questions. Don't compress away nuance. Open each with: `> AI-written doc derived from voice memo <date>, intended as context for agents.`
- **Eng tasks**: each needs title, spec, acceptance criteria, context-doc links, and a readiness label — `ready` (agent can start unaided) or `needs-input` (ambiguous).
- **Todos**: personal/non-code items → Things via `mcp__things__add_todo`; if unavailable or an add fails, list those items in `todos.md`.
- **Drafts**: emails, tweets, messages, essays as clean sendable drafts in `drafts.md`, separated by destination/audience.
- **Misc**: real but unclassifiable content → `transcript.md` under `Misc`.

## Optional task handoff

Only when explicitly requested, and only after the artifacts above exist:

1. Write a self-contained prompt file per task at `agent-prompts/<task-slug>.md`: embedded context-doc content, spec, acceptance criteria, repo/path hints, constraints, deliverables.
2. Launch only `ready` tasks, via the current Codex task mechanism (no pinned companion or model path); `needs-input` tasks stay as files.
3. Record each launch, prompt path, and check-back instructions in the report.

If launching fails, leave the prompt files and report the exact blocker.

## Autonomy

One interaction point: the final report. Choose conservative defaults, log deviations, surface unresolved ambiguity at the end. Stop early only for hard blockers (missing audio, failed transcription, unwritable archive, tool failure that would corrupt outputs) — then report what was tried and what exact input is needed.

## Final report

One concise summary: memo picked (path, timestamp, duration, stale warning); transcript and walk-folder paths; context docs created; tasks by readiness; todos filed in Things vs `todos.md`; drafts written; any requested launches and how to check them; open questions. Link paths — no large transcript excerpts.
