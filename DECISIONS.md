# Decisions

## 2026-08-03 — Use usetranscribe.io for YouTube transcription

- Decision: route YouTube transcription through usetranscribe.io and reuse the existing `save2md` helper for cache checks, SSE parsing, and Markdown output.
- Rationale: this follows the user's requested service, preserves the service's permalink and timestamped output, and avoids duplicating fragile API parsing.
- Decision source: user-directed.
