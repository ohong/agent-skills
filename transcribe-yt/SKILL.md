---
name: transcribe-yt
description: Save video or podcast transcripts as local Markdown files using the usetranscribe.io YouTube transcript API. Use when the user asks for a YouTube video transcript, podcast transcript, interview transcript, lecture transcript, episode transcript, or any video/audio transcript that should be downloaded as .md; for podcast links, first find an equivalent YouTube upload when one exists because the API only accepts YouTube URLs.
---

# Transcribe YouTube

Save a YouTube transcript as a local Markdown file through `https://www.usetranscribe.io`. The service only accepts YouTube URLs; never submit Spotify, Apple Podcasts, RSS, or generic podcast URLs directly.

## Workflow

1. Identify the YouTube URL.
   - If the user gives a YouTube URL, use it directly.
   - If the user gives a podcast episode link, search the web or YouTube for the same episode title, show name, guest, and date.
   - Prefer official podcast, host, publisher, or guest-channel uploads. If several plausible YouTube uploads exist, choose the closest title/date match and mention the assumption.
   - If no YouTube version exists, report that `usetranscribe.io` only supports YouTube and do not fabricate a transcript.

2. Run the bundled helper from this skill directory.

```bash
python3 scripts/transcribe_yt.py "https://www.youtube.com/watch?v=VIDEO_ID"
```

By default it writes to:

```text
./transcripts/<title-slug>.md
```

Use a requested destination when the user provides one:

```bash
python3 scripts/transcribe_yt.py "https://youtu.be/VIDEO_ID" --out-dir /path/to/transcripts
python3 scripts/transcribe_yt.py "https://youtu.be/VIDEO_ID" --output /path/to/episode.md
```

3. Inspect the Markdown before responding.
   - Confirm it contains source URL, Transcribe permalink, summary when available, and timestamped transcript lines.
   - If the API returns `too_long`, `unsupported_url`, or `auth_required`, do not retry; report the blocker.
   - If the API returns transient `metadata_failed` or `transcription_failed`, retry with backoff once or twice.
   - If rate-limited, report the 429 scope and stop.

4. Final response: keep it short and include the absolute path to the `.md` file. Mention any ambiguity in a podcast-to-YouTube match.

## Helper Behavior

`scripts/transcribe_yt.py` implements the fragile API details:

- Extracts video IDs from common YouTube URL shapes.
- Checks `/api/check?platform=youtube&id=...` before transcribing.
- Fetches cached JSON from `/yt/{video_id}/...?format=json` when present.
- Uses the `/transcribe?url=...&summarize=1` SSE stream only on cache misses.
- Handles the cached JSON shape and SSE `done` shape, which differ.
- Writes a Markdown transcript with metadata, summary, and timestamps.

Useful validation commands:

```bash
python3 scripts/transcribe_yt.py --help
python3 scripts/transcribe_yt.py --check-only "https://www.youtube.com/watch?v=DULfEcPR0Gc"
```
