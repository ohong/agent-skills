#!/usr/bin/env python3
"""Export and validate Field Theory bookmarks as chronological Markdown."""

from __future__ import annotations

import argparse
import html
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Sequence
from urllib.parse import urlsplit, urlunsplit

DEFAULT_FT = "/opt/homebrew/bin/ft"
DEFAULT_LIMIT = 20_000
TWITTER_DATE = "%a %b %d %H:%M:%S %z %Y"
SENSITIVE = re.compile(
    r"(?i)(authorization|cookie|token|secret)(\s*[:=]\s*)(\S+)"
)


class ExportError(ValueError):
    """Raised when Field Theory data cannot produce a trustworthy export."""


@dataclass(frozen=True)
class Bookmark:
    author_name: str
    author_handle: str
    posted_at_raw: str
    posted_at: datetime
    url: str
    text: str
    folders: tuple[str, ...]
    article_title: str | None
    article_text: str | None


def parse_date(value: str) -> datetime:
    try:
        return datetime.strptime(value, TWITTER_DATE)
    except ValueError:
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError as exc:
            raise ExportError(f"invalid postedAt timestamp: {value!r}") from exc


def required_text(record: dict[str, Any], key: str, index: int) -> str:
    value = record.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ExportError(f"record {index} has missing or empty {key}")
    return value


def optional_text(record: dict[str, Any], key: str, index: int) -> str | None:
    value = record.get(key)
    if value is None:
        return None
    if not isinstance(value, str):
        raise ExportError(f"record {index} has non-string {key}")
    return value if value.strip() else None


def canonical_url(raw: str, handle: str, index: int) -> str:
    parsed = urlsplit(raw)
    host = parsed.netloc.lower()
    parts = tuple(part for part in parsed.path.split("/") if part)
    if host in {"x.com", "www.x.com", "twitter.com", "www.twitter.com"}:
        if len(parts) >= 3 and parts[1] == "status" and parts[2].isdigit():
            return urlunsplit(("https", "x.com", f"/{handle}/status/{parts[2]}", "", ""))
    raise ExportError(f"record {index} has non-canonicalizable X URL: {raw!r}")


def parse_bookmark(record: Any, index: int, folder: str | None) -> Bookmark:
    if not isinstance(record, dict):
        raise ExportError(f"record {index} is not a JSON object")
    author_name = required_text(record, "authorName", index)
    author_handle = required_text(record, "authorHandle", index).lstrip("@")
    posted_at_raw = required_text(record, "postedAt", index)
    text = required_text(record, "text", index)
    raw_url = required_text(record, "url", index)
    raw_folders = record.get("folderNames", [])
    if not isinstance(raw_folders, list) or not all(
        isinstance(value, str) and value.strip() for value in raw_folders
    ):
        raise ExportError(f"record {index} has invalid folderNames")
    folders = tuple(raw_folders)
    if folder is not None and folder not in folders:
        raise ExportError(
            f"record {index} is missing requested folder metadata: {folder!r}"
        )
    return Bookmark(
        author_name=author_name,
        author_handle=author_handle,
        posted_at_raw=posted_at_raw,
        posted_at=parse_date(posted_at_raw),
        url=canonical_url(raw_url, author_handle, index),
        text=text,
        folders=folders,
        article_title=optional_text(record, "articleTitle", index),
        article_text=optional_text(record, "articleText", index),
    )


def load_records(
    mode: str,
    selection: str,
    ft_path: str,
    limit: int,
    input_json: Path | None,
) -> list[Any]:
    if input_json is not None:
        raw = input_json.read_text(encoding="utf-8")
    else:
        selector = "--folder" if mode == "folder" else "--query"
        command = [ft_path, "list", selector, selection, "--limit", str(limit), "--json"]
        try:
            result = subprocess.run(
                command,
                check=False,
                capture_output=True,
                text=True,
                timeout=120,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise ExportError(f"could not run Field Theory: {type(exc).__name__}") from exc
        if result.returncode != 0:
            detail = SENSITIVE.sub(r"\1\2[REDACTED]", result.stderr.strip())
            detail = detail.splitlines()[-1][:300] if detail else "no diagnostic"
            raise ExportError(
                f"Field Theory list failed with exit {result.returncode}: {detail}"
            )
        raw = result.stdout
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ExportError("Field Theory output is not valid JSON") from exc
    if not isinstance(payload, list):
        raise ExportError("Field Theory output must be a JSON array")
    return payload


def safe_heading(value: str) -> str:
    return " ".join(value.replace("#", "").split())


def preformatted(value: str) -> str:
    return f"<pre>{html.escape(value, quote=False)}</pre>"


def render(mode: str, selection: str, bookmarks: Sequence[Bookmark]) -> str:
    source = f"Field Theory {mode}"
    chronology = (
        f"{bookmarks[0].posted_at_raw} to {bookmarks[-1].posted_at_raw}"
        if bookmarks
        else "empty"
    )
    lines = [
        "# Field Theory bookmark export",
        "",
        f"- Source: {source}",
        f"- Selection: {selection}",
        f"- Bookmarks: {len(bookmarks)}",
        "- Order: postedAt ascending (oldest to newest)",
        f"- Chronology: {chronology}",
        "",
    ]
    for number, bookmark in enumerate(bookmarks, start=1):
        folders = ", ".join(bookmark.folders) if bookmark.folders else "(untagged)"
        lines.extend(
            [
                f"## {number}. {safe_heading(bookmark.author_name)} "
                f"(@{bookmark.author_handle})",
                "",
                f"- Posted: {bookmark.posted_at_raw}",
                f"- URL: {bookmark.url}",
                f"- Folders: {folders}",
                "",
                "### Post",
                "",
                preformatted(bookmark.text),
                "",
            ]
        )
        if bookmark.article_title or bookmark.article_text:
            lines.extend(
                [
                    "### X Article",
                    "",
                    f"Title: {bookmark.article_title or '(untitled)'}",
                    "",
                    preformatted(bookmark.article_text or ""),
                    "",
                ]
            )
    return "\n".join(lines).rstrip() + "\n"


def validate(
    mode: str,
    selection: str,
    bookmarks: Sequence[Bookmark],
    markdown: str,
) -> None:
    if not markdown.startswith("# Field Theory bookmark export\n"):
        raise ExportError("rendered export is missing its source heading")
    if f"- Source: Field Theory {mode}" not in markdown:
        raise ExportError("rendered export is missing source metadata")
    if f"- Selection: {selection}" not in markdown:
        raise ExportError("rendered export is missing selection metadata")
    if any(
        bookmarks[index].posted_at > bookmarks[index + 1].posted_at
        for index in range(len(bookmarks) - 1)
    ):
        raise ExportError("bookmarks are not sorted chronologically")
    urls = [bookmark.url for bookmark in bookmarks]
    if len(urls) != len(set(urls)):
        raise ExportError("source contains duplicate canonical X links")
    headings = re.findall(r"^## \d+\. ", markdown, flags=re.MULTILINE)
    links = re.findall(r"^- URL: (https://x\.com/\S+)$", markdown, flags=re.MULTILINE)
    if len(headings) != len(bookmarks):
        raise ExportError("bookmark heading count does not match source count")
    if links != urls:
        raise ExportError("rendered canonical links do not match source records")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Export full Field Theory bookmark records to verified Markdown."
    )
    parser.add_argument("mode", choices=("folder", "query"))
    parser.add_argument("selection", help="Exact folder name or FTS5 query")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT)
    parser.add_argument("--ft", default=DEFAULT_FT, help="Path to the ft executable")
    parser.add_argument(
        "--input-json",
        type=Path,
        help="Read an ft-compatible JSON fixture instead of invoking ft",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.limit < 1:
        raise ExportError("--limit must be at least 1")
    raw_records = load_records(
        args.mode, args.selection, args.ft, args.limit, args.input_json
    )
    folder = args.selection if args.mode == "folder" else None
    bookmarks = sorted(
        (parse_bookmark(record, index, folder) for index, record in enumerate(raw_records, 1)),
        key=lambda bookmark: (bookmark.posted_at, bookmark.url),
    )
    markdown = render(args.mode, args.selection, bookmarks)
    validate(args.mode, args.selection, bookmarks, markdown)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(markdown, encoding="utf-8")
    print(
        f"Wrote {len(bookmarks)} verified bookmarks to {args.output} "
        "(postedAt ascending)"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ExportError as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(2)
