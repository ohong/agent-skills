---
name: transcribe-youtube
description: Transcribe a YouTube video through usetranscribe.io, save the result as timestamped Markdown, and return the local file and hosted transcript links. Use when the user provides a YouTube URL and asks for a transcript, transcription, summary, or transcript-based follow-up.
---

# Transcribe YouTube

Use `https://www.usetranscribe.io/AGENTS.md` as the authoritative service guide. Read it before using the service and link to it in the final response. Use this skill for YouTube URLs only; do not substitute another transcription provider.

## Default workflow

1. Normalize and validate the YouTube URL. Accept `youtube.com`, `m.youtube.com`, `music.youtube.com`, and `youtu.be` video URLs. Reject non-YouTube URLs rather than sending them to the service.
2. Use the existing helper, which implements the service's cache check, SSE parsing, schema normalization, and Markdown rendering:

   ```bash
   python3 /Users/ohong/dev/agent-skills/save2md/skills/save2md/scripts/transcribe_yt.py \
     "<youtube-url>" \
     --out-dir "$HOME/Documents/Saved Articles/YouTube"
   ```

   Use the user's requested destination when one is provided. Use `--output` for an exact file path. If the helper is unavailable, follow the live `AGENTS.md` API instructions directly; do not silently change providers.
3. Inspect the generated Markdown before responding. Confirm that it contains the source URL, the usetranscribe.io permalink, a summary when available, and timestamped transcript lines. Return the absolute local path and hosted permalink.
4. Keep the response concise unless the user asks for the transcript inline. Link the live [usetranscribe.io agent instructions](https://www.usetranscribe.io/AGENTS.md) in the handoff.

## Service invariants

- Use the `www` base URL: `https://www.usetranscribe.io`.
- Cache-check first with `/api/check?platform=youtube&id=<video-id>`; fetch cached data when available instead of starting a new job.
- On a cache miss, consume `/transcribe?url=<url>&summarize=1` as an SSE stream and wait for its `done` event.
- Cached JSON stores segments under `transcript.segments` and the summary in `summary`; the SSE `done` payload stores segments at top level and the summary in `summary_md`.
- Treat a permalink as either a full URL or a path; do not blindly prepend the base URL twice.
- The service has no API key requirement today, accepts videos up to 90 minutes, and is English-tuned.

## Errors and follow-up questions

- Do not retry `too_long`, `unsupported_url`, or `auth_required`; report the blocker clearly.
- For `metadata_failed` or `transcription_failed`, retry with backoff once or twice. On `429`, report the rate-limit scope and stop.
- If the user asks a question about an already-transcribed video, use the service's `POST /yt/<video-id>/ask` SSE endpoint and preserve its timestamp citations. Do not answer from an incomplete or empty transcript.
