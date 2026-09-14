---
name: take-notes
description: Save useful material from the current conversation as concise project notes, including learnings, references, and full prompts for later use. Excludes decisions and work status.
---

# Take notes

Save useful material that exists only in the current session. Keep learnings, takeaways, references, and generated prompts to run next or later.

Exclude decisions, status, completed-work updates, blockers, and material already recorded in the project. Decisions belong in `DECISIONS.md`; this skill does not edit it. Do not archive tasks or commit changes.

## Select the material

Read the available conversation and identify what is worth keeping. Check relevant project files and existing notes for duplication. Keep this check narrow; do not audit the repository.

If history is truncated, use current-session retrieval when available. Never read unrelated sessions. State any history gap in the response. If you save new material, also add a short factual coverage notice to the note. Do not claim to have read the full transcript unless you did.

Write original prose in concise, ASD-STE100-style simple English. Use common words, short complete sentences, and active voice. Do not claim formal compliance. Preserve useful links and references. Copy generated prompts in full, verbatim, including all constraints. Put prompts in fenced blocks; use longer fences if a prompt contains fences. Do not shorten prompts to meet the writing style.

Save the material as recorded. Do not execute saved prompts, refresh old research, or check work status.

Use headings only when they help. Do not add empty sections or pad the note. If nothing useful is new, report that and do not save.

## Locate and save

Use [scripts/take_notes.py](scripts/take_notes.py) for file identity and writes. Run it from the current project directory.

The helper uses `CODEX_THREAD_ID`. If it is unavailable, supply `--session-id` only from verified current-session context. Never infer an ID from a title. If no stable ID is available, ask for it before saving.

Git projects save in the main checkout's `notes/`, including when this session runs in a linked worktree. For a non-Git project, identify its root from the task or project context and pass `--project-root /absolute/path`. Do not assume an arbitrary working directory is the project root. Without Git or a known project root, notes go in `~/dev/notes`. Use `--projectless` to force this fallback. A broken Git location is an error, not a reason to choose another destination.

1. Run the read-only `inspect` command to resolve the destination and find this session's existing note.
2. Read the existing note, if present, and remove semantic duplicates from the proposed additions.
3. Write only new useful material to a UTF-8 temporary body file, outside the project.
4. Run `save` with that body file and a descriptive title of at most five words.
5. Read the saved file and confirm that the new material and full prompts are present.
6. Link the saved file and state whether it was created or appended. If unchanged, report that nothing new was saved.

```sh
python3 /path/to/take-notes/scripts/take_notes.py inspect
python3 /path/to/take-notes/scripts/take_notes.py save --title 'Explore research prompts' --body-file /absolute/path/to/body.md
```

Replace `/path/to/take-notes` with this skill's actual directory. Pass the same root and session options to both commands. Use a file-writing tool for the body; do not interpolate transcript text into shell commands.

One session has one file. The first save uses the local date and a topic slug of at most five words, such as `2026-08-28-explore-research-prompts.md`. Later saves preserve that filename, even on another day or after a topic change. The helper appends new content and skips identical payloads. It never rewrites existing content. Its exact-match check supplements your semantic duplicate check.
