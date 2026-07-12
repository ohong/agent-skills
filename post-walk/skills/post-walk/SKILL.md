---
name: post-walk
description: Process a local Apple Voice Memo into an archived transcript, project notes, tasks, todos, and drafts. Use only when explicitly asked to process a walk or commute memo.
---

# Post-Walk Memo Processor

Turn one long Apple Voice Memo into durable project context, engineering tasks, personal todos, and writing drafts. Run from the memo to the final report without launching additional work unless the user explicitly asks.

## Inputs

| Source | Rule |
|---|---|
| User argument is a file path | Use that audio file. Expand `~`; verify it exists before transcribing. |
| No file path argument | Pick the newest `*.m4a` by mtime in `~/Library/Group Containers/group.com.apple.VoiceMemos.shared/Recordings/`. |
| User argument is not a file path | Treat it as a hint for naming, context, or prioritization; still auto-locate the newest voice memo. |

When selecting the memo, report the picked file, recording timestamp, and duration. Use `mdls`, `stat`, `ffprobe`, `afinfo`, or QuickTime metadata as available. If the newest memo is more than about 12 hours old, flag that it may be stale and proceed.

## Transcribe

Run the bundled helper:

Run `scripts/transcribe.sh <audio-file> [output.txt]`, resolving it relative to
this skill directory. In Claude Code the full path is
`${CLAUDE_PLUGIN_ROOT}/skills/post-walk/scripts/transcribe.sh`.

The helper uses ElevenLabs Scribe v1 and requires `ELEVENLABS_API_KEY`. It accepts m4a directly, prints only the transcript path on success, and uses stderr for errors. Do not paste raw API responses into the final report unless needed to explain a failure.

## Archive

Create one walk folder:

| Current location | Archive folder |
|---|---|
| Inside a git repo | `docs/walks/YYYY-MM-DD-<short-slug>/` |
| Outside a git repo | `~/walks/YYYY-MM-DD-<short-slug>/` |

Use a short slug from the strongest memo theme, or from the user's hint if useful. If uncertain, use `walk-notes`.

Write:

| File | Contents |
|---|---|
| `transcript.raw.txt` | Raw helper output, unchanged. |
| `transcript.md` | Cleaned transcript with obvious ASR errors fixed, paragraph breaks added, the speaker's words preserved, plus a short summary. Put any unclassifiable material in a `Misc` section. |
| `docs/<n>-<slug>.md` | One standalone agent-context document per substantial idea or project theme. |
| `tasks.md` | Engineering tasks with specs, acceptance criteria, and readiness labels. |
| `todos.md` | Only when Things MCP todo creation is unavailable or partially unavailable. |
| `drafts.md` | Sendable/postable drafts for emails, tweets, essays, messages, or other writing. |

Nothing gets dropped. If an item does not fit a bucket, put it in `transcript.md` under `Misc`.

## Buckets

Read the entire transcript before partitioning it.

| Bucket | Output rule |
|---|---|
| Context docs | For each substantial idea/project theme, create `docs/<n>-<slug>.md`. Write broad, deep agent context: problem, background, goals, constraints, useful facts, possible approaches, and open questions. Start each doc with: `> AI-written doc derived from voice memo <date>, intended as context for agents.` Do not compress away nuance. |
| Eng tasks | Add to `tasks.md`. Each task needs a title, spec, acceptance criteria, relevant context-doc links, and readiness label: `ready` when an agent can start without more input, `needs-input` when ambiguous. |
| Todos | Personal/non-code tasks go to Things via `mcp__things__add_todo` when that tool is available. If unavailable, or if any add fails, list those items in `todos.md`. |
| Drafts | Write emails, tweets, messages, notes, or other prose as clean sendable/postable drafts in `drafts.md`, clearly separated by destination or audience. |
| Misc | Put unclassifiable but real memo content in `transcript.md` under `Misc`. Never invent missing content. |

## Optional Task Handoff

Do not launch agents or background tasks unless the user explicitly asks. Always create the task artifacts first.

When launching is explicitly requested:

1. Create a self-contained prompt file in the walk folder, such as `agent-prompts/<task-slug>.md`.
2. Embed the relevant context doc content, task spec, acceptance criteria, repo/path hints, constraints, and expected deliverables.
3. Launch only tasks labeled `ready`; leave `needs-input` tasks as files.
4. Use the current Codex task mechanism instead of a pinned companion or model path.
5. Record each launched task, prompt path, and check-back instructions in the final report.

If launching is unavailable, leave the self-contained prompt files in place and report the exact blocker.

## Autonomy

This workflow has one interaction point by default: the final report. Do not pause before transcription, archiving, or bucketing. Choose conservative defaults, log deviations, and surface unresolved ambiguity at the end.

Stop early only for hard blockers such as missing audio, failed transcription with no viable fallback, unwritable archive location, or tool/runtime failure that would corrupt outputs. When blocked, report what was tried and what exact input or permission is needed.

## Final Report

Return one concise summary:

- Memo picked: path, timestamp, duration, and stale warning if applicable.
- Transcript location and walk folder.
- Context docs created.
- Engineering tasks: `ready` vs `needs-input`, plus launches only when explicitly requested.
- Todos filed in Things or written to `todos.md`.
- Drafts written.
- Any explicitly requested launches and how to check on them.
- Open questions needing the user's input.

Do not include large transcript excerpts in the final report. Link paths instead.
