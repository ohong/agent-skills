#!/usr/bin/env python3
"""Save a usetranscribe.io YouTube transcript as Markdown."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Iterator


BASE_URL = "https://www.usetranscribe.io"
USER_AGENT = "Codex save2md skill/1.0 (+https://www.usetranscribe.io/AGENTS.md)"


class TranscribeError(RuntimeError):
    """Raised for API and input failures."""


def extract_video_id(url: str) -> str:
    parsed = urllib.parse.urlparse(url.strip())
    host = parsed.netloc.lower().replace("www.", "")
    path_parts = [part for part in parsed.path.split("/") if part]

    if host in {"youtube.com", "m.youtube.com", "music.youtube.com"}:
        query = urllib.parse.parse_qs(parsed.query)
        if query.get("v"):
            return validate_video_id(query["v"][0])
        if len(path_parts) >= 2 and path_parts[0] in {"embed", "shorts", "live", "v"}:
            return validate_video_id(path_parts[1])

    if host == "youtu.be" and path_parts:
        return validate_video_id(path_parts[0])

    raise TranscribeError(
        "Unsupported URL. usetranscribe.io accepts YouTube URLs only; find a YouTube upload first."
    )


def validate_video_id(value: str) -> str:
    value = value.strip()
    if re.fullmatch(r"[A-Za-z0-9_-]{11}", value):
        return value
    raise TranscribeError(f"Could not parse a valid YouTube video ID from: {value!r}")


def canonical_youtube_url(video_id: str) -> str:
    return f"https://www.youtube.com/watch?v={video_id}"


def request_url(url: str, params: dict[str, Any] | None = None) -> str:
    if not params:
        return url
    separator = "&" if urllib.parse.urlparse(url).query else "?"
    return f"{url}{separator}{urllib.parse.urlencode(params)}"


def http_get_bytes(url: str, params: dict[str, Any] | None = None, timeout: int = 60) -> bytes:
    full_url = request_url(url, params)
    request = urllib.request.Request(full_url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.read()
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise TranscribeError(f"HTTP {exc.code} for {full_url}: {body}") from exc
    except urllib.error.URLError as exc:
        raise TranscribeError(f"Request failed for {full_url}: {exc.reason}") from exc


def http_get_json(url: str, params: dict[str, Any] | None = None, timeout: int = 60) -> dict[str, Any]:
    body = http_get_bytes(url, params=params, timeout=timeout)
    try:
        data = json.loads(body.decode("utf-8"))
    except json.JSONDecodeError as exc:
        raise TranscribeError(f"Expected JSON from {request_url(url, params)}") from exc
    if not isinstance(data, dict):
        raise TranscribeError(f"Expected JSON object from {request_url(url, params)}")
    return data


def absolutize_permalink(permalink: str) -> str:
    return permalink if permalink.startswith("http") else urllib.parse.urljoin(BASE_URL, permalink)


def cache_check(video_id: str) -> dict[str, Any]:
    return http_get_json(f"{BASE_URL}/api/check", {"platform": "youtube", "id": video_id})


def fetch_cached_json(permalink: str) -> dict[str, Any]:
    return http_get_json(absolutize_permalink(permalink), {"format": "json"}, timeout=120)


def iter_sse(url: str, params: dict[str, Any], timeout: int) -> Iterator[tuple[str, str]]:
    full_url = request_url(url, params)
    request = urllib.request.Request(full_url, headers={"User-Agent": USER_AGENT, "Accept": "text/event-stream"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            event = "message"
            data_lines: list[str] = []
            for raw_line in response:
                line = raw_line.decode("utf-8", errors="replace").rstrip("\r\n")
                if line == "":
                    if data_lines:
                        yield event, "\n".join(data_lines)
                    event = "message"
                    data_lines = []
                    continue
                if line.startswith(":"):
                    continue
                if line.startswith("event:"):
                    event = line.split(":", 1)[1].strip()
                    continue
                if line.startswith("data:"):
                    data = line.split(":", 1)[1]
                    if data.startswith(" "):
                        data = data[1:]
                    data_lines.append(data)
            if data_lines:
                yield event, "\n".join(data_lines)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise TranscribeError(f"HTTP {exc.code} for {full_url}: {body}") from exc
    except urllib.error.URLError as exc:
        raise TranscribeError(f"SSE request failed for {full_url}: {exc.reason}") from exc


def transcribe(video_url: str, timeout: int, verbose: bool) -> dict[str, Any]:
    done_payload: dict[str, Any] | None = None
    for event, data in iter_sse(f"{BASE_URL}/transcribe", {"url": video_url, "summarize": 1}, timeout=timeout):
        if event in {"stage", "meta"} and verbose:
            print(f"{event}: {data}", file=sys.stderr)
        if event == "error":
            try:
                payload = json.loads(data)
            except json.JSONDecodeError:
                raise TranscribeError(f"Transcribe API error: {data}") from None
            code = payload.get("code", "error")
            message = payload.get("message", "")
            raise TranscribeError(f"{code}: {message}".strip())
        if event == "done":
            try:
                parsed = json.loads(data)
            except json.JSONDecodeError as exc:
                raise TranscribeError("Could not parse SSE done payload as JSON") from exc
            if not isinstance(parsed, dict):
                raise TranscribeError("Expected SSE done payload to be a JSON object")
            done_payload = parsed
            break

    if done_payload is None:
        raise TranscribeError("Transcription stream ended without a done event")
    return done_payload


def seconds_to_timestamp(value: Any) -> str:
    try:
        total = int(float(value))
    except (TypeError, ValueError):
        total = 0
    hours, rem = divmod(total, 3600)
    minutes, seconds = divmod(rem, 60)
    if hours:
        return f"{hours}:{minutes:02d}:{seconds:02d}"
    return f"{minutes:02d}:{seconds:02d}"


def maybe_float(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def duration_label(value: Any) -> str:
    if value in (None, ""):
        return ""
    return seconds_to_timestamp(value)


def slugify(value: str, fallback: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return (slug[:96].strip("-") or fallback)


def demote_headings(markdown: str) -> str:
    return re.sub(r"^(#{1,5})\s", r"\1# ", markdown.strip(), flags=re.MULTILINE)


def clean_inline(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def append_segment_text(current: str, addition: str) -> str:
    addition = clean_inline(addition)
    if not addition:
        return current
    if not current:
        return addition
    if re.match(r"^[,.;:!?%)\]}]", addition):
        return current + addition
    if current.endswith(("(", "[", "{", "$")):
        return current + addition
    return f"{current} {addition}"


def group_segments(segments: list[Any]) -> list[dict[str, Any]]:
    grouped: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None

    def flush() -> None:
        nonlocal current
        if current and current.get("text"):
            grouped.append(current)
        current = None

    for item in segments:
        if not isinstance(item, dict):
            continue
        text = clean_inline(item.get("text"))
        if not text:
            continue
        start = maybe_float(item.get("start"))
        end = maybe_float(item.get("end"))
        speaker = clean_inline(item.get("speaker"))

        if current is None:
            current = {"start": start if start is not None else 0.0, "end": end, "speaker": speaker, "text": text}
            continue

        current_end = maybe_float(current.get("end"))
        current_text = str(current.get("text") or "")
        same_speaker = speaker == clean_inline(current.get("speaker"))
        gap = (start - current_end) if start is not None and current_end is not None else 0.0
        should_break = False
        if speaker or current.get("speaker"):
            should_break = not same_speaker
        if gap > 2.0:
            should_break = True
        if len(current_text) >= 700:
            should_break = True
        if len(current_text) >= 260 and re.search(r"[.!?]['\")\]]?$", current_text):
            should_break = True

        if should_break:
            flush()
            current = {"start": start if start is not None else 0.0, "end": end, "speaker": speaker, "text": text}
        else:
            current["text"] = append_segment_text(current_text, text)
            if end is not None:
                current["end"] = end

    flush()
    return grouped


def normalize_from_cached(data: dict[str, Any], video_id: str) -> dict[str, Any]:
    transcript = data.get("transcript") if isinstance(data.get("transcript"), dict) else {}
    return {
        "video_id": video_id,
        "platform": data.get("platform") or "youtube",
        "title": data.get("title") or f"YouTube Transcript {video_id}",
        "creator": data.get("creator") or "",
        "duration_seconds": data.get("duration_seconds"),
        "thumbnail_url": data.get("thumbnail_url") or "",
        "source_url": data.get("source_url") or canonical_youtube_url(video_id),
        "published_at": data.get("published_at"),
        "language": transcript.get("language") or "",
        "segments": transcript.get("segments") or [],
        "summary": data.get("summary") or "",
        "permalink": absolutize_permalink(str(data.get("permalink") or f"/yt/{video_id}")),
        "pipeline_version": data.get("pipeline_version") or "",
        "source": "cached",
    }


def normalize_from_done(data: dict[str, Any], video_id: str, source_url: str) -> dict[str, Any]:
    metadata = data.get("metadata") if isinstance(data.get("metadata"), dict) else {}
    return {
        "video_id": video_id,
        "platform": "youtube",
        "title": metadata.get("title") or f"YouTube Transcript {video_id}",
        "creator": metadata.get("creator") or metadata.get("channel") or "",
        "duration_seconds": metadata.get("duration_seconds"),
        "thumbnail_url": metadata.get("thumbnail_url") or "",
        "source_url": metadata.get("source_url") or source_url,
        "published_at": metadata.get("published_at"),
        "language": data.get("language") or "",
        "segments": data.get("segments") or [],
        "summary": data.get("summary_md") or "",
        "permalink": absolutize_permalink(str(data.get("permalink") or f"/yt/{video_id}")),
        "pipeline_version": data.get("pipeline_version") or "",
        "source": data.get("source") or "transcribe",
    }


def render_markdown(data: dict[str, Any]) -> str:
    title = clean_inline(data.get("title")) or f"YouTube Transcript {data['video_id']}"
    generated = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()
    lines = [f"# {title}", ""]
    metadata = [
        ("Source", data.get("source_url")),
        ("Transcribe permalink", data.get("permalink")),
        ("Creator", data.get("creator")),
        ("Duration", duration_label(data.get("duration_seconds"))),
        ("Published", data.get("published_at")),
        ("Language", data.get("language")),
        ("Video ID", data.get("video_id")),
        ("Transcript source", data.get("source")),
        ("Generated", generated),
    ]
    for label, value in metadata:
        cleaned = clean_inline(value)
        if cleaned:
            lines.append(f"- **{label}:** {cleaned}")
    lines.append("")

    summary = str(data.get("summary") or "").strip()
    if summary:
        lines.extend(["## Summary", "", demote_headings(summary), ""])

    segments = data.get("segments") or []
    lines.extend(["## Transcript", ""])
    if not isinstance(segments, list) or not segments:
        lines.append("_No transcript segments were returned._")
    else:
        for segment in group_segments(segments):
            if not isinstance(segment, dict):
                continue
            start = seconds_to_timestamp(segment.get("start"))
            text = clean_inline(segment.get("text"))
            if not text:
                continue
            speaker = clean_inline(segment.get("speaker"))
            if speaker:
                lines.append(f"[{start}] **{speaker}:** {text}")
            else:
                lines.append(f"[{start}] {text}")
            lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def unique_path(path: Path) -> Path:
    if not path.exists():
        return path
    stem = path.stem
    suffix = path.suffix
    for index in range(2, 1000):
        candidate = path.with_name(f"{stem}-{index}{suffix}")
        if not candidate.exists():
            return candidate
    raise TranscribeError(f"Could not find a free filename near {path}")


def output_path(args: argparse.Namespace, data: dict[str, Any]) -> Path:
    if args.output:
        path = Path(args.output).expanduser().resolve()
    else:
        out_dir = Path(args.out_dir).expanduser().resolve() if args.out_dir else (Path.cwd() / "transcripts").resolve()
        title = clean_inline(data.get("title"))
        slug = slugify(title, f"youtube-{data['video_id']}")
        path = out_dir / f"{slug}.md"
    if path.suffix.lower() != ".md":
        path = path.with_suffix(".md")
    if not args.overwrite:
        path = unique_path(path)
    return path


def load_transcript(video_url: str, video_id: str, timeout: int, verbose: bool) -> tuple[dict[str, Any], bool]:
    check = cache_check(video_id)
    cached = bool(check.get("cached"))
    if cached:
        permalink = str(check.get("permalink") or f"/yt/{video_id}")
        return normalize_from_cached(fetch_cached_json(permalink), video_id), True

    if verbose:
        print("cache miss: starting transcription", file=sys.stderr)
    done = transcribe(video_url, timeout=timeout, verbose=verbose)
    normalized = normalize_from_done(done, video_id, video_url)

    # After a successful job, prefer canonical cached JSON if it is immediately readable.
    permalink = normalized.get("permalink")
    if permalink:
        try:
            return normalize_from_cached(fetch_cached_json(str(permalink)), video_id), False
        except TranscribeError as exc:
            if verbose:
                print(f"warning: could not refetch cached JSON after transcribe: {exc}", file=sys.stderr)
    return normalized, False


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Save a YouTube transcript from usetranscribe.io as Markdown.")
    parser.add_argument("url", help="YouTube URL")
    parser.add_argument("--out-dir", help="Directory for the generated Markdown file. Defaults to ./transcripts")
    parser.add_argument("--output", help="Exact Markdown output path")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite the output file if it exists")
    parser.add_argument("--check-only", action="store_true", help="Only check whether the URL is already cached")
    parser.add_argument("--timeout", type=int, default=600, help="Request timeout in seconds for transcription SSE")
    parser.add_argument("--quiet", action="store_true", help="Suppress progress on stderr")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    verbose = not args.quiet

    try:
        video_id = extract_video_id(args.url)
        video_url = canonical_youtube_url(video_id)
        if args.check_only:
            check = cache_check(video_id)
            print(json.dumps({"video_id": video_id, "url": video_url, **check}, indent=2, sort_keys=True))
            return 0

        data, cached = load_transcript(video_url, video_id, timeout=args.timeout, verbose=verbose)
        path = output_path(args, data)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(render_markdown(data), encoding="utf-8")
        status = "cached" if cached else "transcribed"
        print(f"Wrote {path}")
        print(f"Status: {status}")
        print(f"Permalink: {data.get('permalink')}")
        return 0
    except TranscribeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("error: interrupted", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
