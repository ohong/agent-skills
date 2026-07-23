---
name: fieldtheory-research
description: Search, sync, export, and analyze the user's local X bookmarks with the Field Theory CLI while preserving full post text and provenance. Use when the user mentions Field Theory, `ft`, X bookmarks, bookmark folders, remembered saved posts, chronological bookmark exports, or bookmark-grounded research. Do not use for live X search or archiving a single known URL.
---

# Field Theory Research

Use `/opt/homebrew/bin/ft` when present, otherwise resolve `ft` from `PATH`.
These commands were validated with v1.3.19; recheck `ft --help` if the installed
version differs. Keep raw source records distinct from later synthesis.

## Workflow

1. **Orient.** Run `ft path`, `ft status`, and only the focused discovery command
   needed: `ft folders`, `ft search '<query>' --limit <n> --json`, or
   `ft list --folder '<name>' --limit <n> --json`. Resolve folders to their exact
   names before exporting.
2. **Refresh only when requested or freshness matters.** Use a bounded,
   media-free sync:

   ```bash
   /opt/homebrew/bin/ft sync --no-media --yes --max-minutes 5
   /opt/homebrew/bin/ft sync --folder '<exact name>' --no-media --yes --max-minutes 5
   ```

   A bounded interruption or `fetch failed` can leave useful records persisted.
   Do not retry blindly. Run `ft index`, then verify the focused `ft list` count
   and newest timestamps. Treat `ft status` as advisory if it disagrees with the
   indexed records.
3. **Export deterministically.** Use the bundled helper, which calls full-record
   `ft list`, sorts by `postedAt` ascending, renders Markdown, and validates
   provenance and structure:

   ```bash
   uv run scripts/export_bookmarks.py folder '<exact name>' --output bookmarks.md
   uv run scripts/export_bookmarks.py query '<FTS5 query>' --output bookmarks.md
   ```

   Folder exports use
   `ft list --folder '<name>' --limit 20000 --json`. Query exports use the
   equivalent full-record `ft list --query`, while `ft search` remains useful for
   quick discovery. Use `--limit` or `--ft` only when needed.
4. **Analyze after preservation.** Base every theme, candidate, or recommendation
   on the verified export. Link claims to source posts. Separate direct evidence,
   interpretation, and any current-web verification.

## Output contract

- Preserve the full `text`, author name and handle, original `postedAt`, canonical
  X URL, and all folder names. Preserve X Article title and body when present.
- Sort chronologically from oldest to newest. Never silently drop duplicates or
  records with missing required fields.
- When the user asks for recent bookmarks, rank by `postedAt` unless a populated
  `bookmarkedAt` field supports save-time ordering, and state which timestamp won.
- Require one numbered bookmark heading and one unique canonical link per source
  record. Report source, selection, count, and chronology in the document header.
- Validate source metadata, heading count, unique links, required fields, folder
  membership for folder exports, and chronological order before reporting success.
- Never print, archive, or inspect browser cookies, authorization headers, or auth
  tokens. Do not expose Field Theory's private credential state.

## Boundaries

Do not edit repository exports during a cache-only sync request. Do not substitute
live X search for the user's bookmark corpus. If Field Theory is unavailable or
authentication prevents a requested sync, preserve and clearly label any
read-only local-cache result instead of claiming freshness.
