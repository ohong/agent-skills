#!/usr/bin/env python3
"""Package an extracted X article/post manifest as Markdown plus media assets."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import mimetypes
import re
import shutil
import sys
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)

DEFAULT_LIBRARY_ROOT = Path.home() / "Documents" / "Saved Articles" / "X"


def slugify(value: str, fallback: str = "x-article") -> str:
    value = value.strip().lower()
    value = re.sub(r"https?://", "", value)
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = value.strip("-")
    return value[:96] or fallback


def canonical_x_url(url: str) -> str:
    parsed = urllib.parse.urlparse(url.strip())
    host = parsed.netloc.lower().replace("www.", "")
    if not host:
        return ""
    if host == "twitter.com":
        host = "x.com"
    path = re.sub(r"/+$", "", parsed.path)
    if not path:
        return ""
    return urllib.parse.urlunparse(("https", host, path, "", "", ""))


def source_slug_from_url(url: str) -> str:
    canonical = canonical_x_url(url)
    parsed = urllib.parse.urlparse(canonical)
    parts = [part for part in parsed.path.split("/") if part]
    if len(parts) >= 3 and parts[1] == "status":
        return slugify(f"{parts[0]}-{parts[2]}")
    if len(parts) >= 3 and parts[1] == "article":
        return slugify(f"{parts[0]}-{parts[2]}")
    return slugify(canonical or url, "x-article")


def title_filename(data: dict[str, Any]) -> str:
    title = str(data.get("title") or "").strip()
    if title:
        return f"{slugify(title)}.md"
    return f"{source_slug_from_url(str(data.get('url') or ''))}.md"


def resolve_out_dir(out_dir_arg: str | None, library_root_arg: str | None, data: dict[str, Any]) -> Path:
    if out_dir_arg:
        return Path(out_dir_arg).expanduser().resolve()
    library_root = Path(library_root_arg or DEFAULT_LIBRARY_ROOT).expanduser()
    return (library_root / source_slug_from_url(str(data.get("url") or ""))).resolve()


def guess_extension(url: str, content_type: str | None = None, default: str = ".bin") -> str:
    parsed = urllib.parse.urlparse(url)
    query = urllib.parse.parse_qs(parsed.query)
    if "format" in query and query["format"]:
        ext = "." + re.sub(r"[^a-zA-Z0-9]", "", query["format"][0]).lower()
        if ext != ".":
            return ext
    suffix = Path(parsed.path).suffix
    if suffix:
        return suffix.split("?")[0]
    if content_type:
        ext = mimetypes.guess_extension(content_type.split(";")[0].strip())
        if ext:
            return ext
    return default


def unique_path(directory: Path, stem: str, ext: str) -> Path:
    stem = slugify(stem, "media")
    candidate = directory / f"{stem}{ext}"
    index = 2
    while candidate.exists():
        candidate = directory / f"{stem}-{index}{ext}"
        index += 1
    return candidate


def download_file(url: str, dest_dir: Path, stem: str) -> Path:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=30) as response:
        content_type = response.headers.get("Content-Type")
        ext = guess_extension(url, content_type)
        dest = unique_path(dest_dir, stem, ext)
        with dest.open("wb") as handle:
            shutil.copyfileobj(response, handle)
    return dest


def copy_file(path: str, dest_dir: Path, stem: str) -> Path:
    src = Path(path).expanduser()
    if not src.exists():
        raise FileNotFoundError(path)
    dest = unique_path(dest_dir, stem or src.stem, src.suffix or ".png")
    shutil.copy2(src, dest)
    return dest


def store_asset(item: dict[str, Any], dest_dir: Path, stem: str) -> str | None:
    source = item.get("path") or item.get("file") or item.get("url")
    if not source:
        return None
    if re.match(r"https?://", source):
        dest = download_file(source, dest_dir, stem)
    else:
        dest = copy_file(source, dest_dir, stem)
    return str(Path("media") / dest.name)


def author_line(author: Any) -> str:
    if not isinstance(author, dict):
        return ""
    name = str(author.get("name") or "").strip()
    handle = str(author.get("handle") or "").strip().lstrip("@")
    if name and handle:
        return f"{name} (@{handle})"
    if handle:
        return f"@{handle}"
    return name


def media_markdown(item: dict[str, Any], link_path: str) -> str:
    alt = str(item.get("alt") or item.get("caption") or "X media").strip()
    caption = str(item.get("caption") or "").strip()
    kind = str(item.get("kind") or "").lower()
    if kind == "video":
        line = f"[Video asset]({link_path})"
    else:
        line = f"![{alt}]({link_path})"
    if caption:
        line += f"\n\n_{caption}_"
    return line


def markdown_asset_path(rel_path: str, out_dir: Path, absolute: bool) -> str:
    if not absolute:
        return rel_path
    return str((out_dir / rel_path).resolve())


def tweet_embed_html(url: str) -> str:
    return f'<blockquote class="twitter-tweet"><a href="{url}"></a></blockquote>'


def render_markdown(
    data: dict[str, Any],
    media_dir: Path,
    notes: list[str],
    absolute_media_links: bool = False,
) -> str:
    url = canonical_x_url(str(data.get("url") or ""))
    title = str(data.get("title") or "").strip() or "X Article Archive"
    out_dir = media_dir.parent
    lines: list[str] = [f"# {title}", ""]
    meta = [
        ("Source", url),
        ("Author", author_line(data.get("author"))),
        ("Published", str(data.get("published_at") or "").strip()),
        ("Archived", dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()),
    ]
    for label, value in meta:
        if value:
            lines.append(f"- **{label}:** {value}")
    lines.append("")

    body = str(data.get("body_markdown") or "").strip()
    if body:
        lines.extend([body, ""])

    media_items = data.get("media") or []
    if media_items:
        lines.extend(["## Media", ""])
        for index, item in enumerate(media_items, start=1):
            if not isinstance(item, dict):
                continue
            try:
                rel = store_asset(item, media_dir, f"media-{index}")
                if rel:
                    link_path = markdown_asset_path(rel, out_dir, absolute_media_links)
                    lines.extend([media_markdown(item, link_path), ""])
            except Exception as exc:  # noqa: BLE001
                notes.append(f"Could not save media {index}: {exc}")

    embeds = data.get("embeds") or data.get("tweets") or []
    if embeds:
        lines.extend(["## Tweet Embeds", ""])
        for index, embed in enumerate(embeds, start=1):
            if not isinstance(embed, dict):
                continue
            embed_url = canonical_x_url(str(embed.get("url") or ""))
            embed_author = author_line(embed.get("author"))
            if embed_author:
                lines.append(f"### {embed_author}")
                lines.append("")
            if embed_url:
                lines.extend([tweet_embed_html(embed_url), ""])
            fallback = str(embed.get("text_markdown") or "").strip()
            if fallback:
                lines.extend(["> " + fallback.replace("\n", "\n> "), ""])
            for media_index, item in enumerate(embed.get("media") or [], start=1):
                if not isinstance(item, dict):
                    continue
                try:
                    rel = store_asset(item, media_dir, f"embed-{index}-media-{media_index}")
                    if rel:
                        link_path = markdown_asset_path(rel, out_dir, absolute_media_links)
                        lines.extend([media_markdown(item, link_path), ""])
                except Exception as exc:  # noqa: BLE001
                    notes.append(f"Could not save embed {index} media {media_index}: {exc}")

    screenshots = data.get("screenshots") or []
    if screenshots:
        lines.extend(["## Screenshots", ""])
        for index, item in enumerate(screenshots, start=1):
            if not isinstance(item, dict):
                continue
            try:
                rel = store_asset(item, media_dir, f"screenshot-{index}")
                if rel:
                    link_path = markdown_asset_path(rel, out_dir, absolute_media_links)
                    lines.extend([media_markdown({"alt": item.get("caption") or "Screenshot"}, link_path), ""])
                    caption = str(item.get("caption") or "").strip()
                    if caption:
                        lines.extend([f"_{caption}_", ""])
            except Exception as exc:  # noqa: BLE001
                notes.append(f"Could not save screenshot {index}: {exc}")

    if notes:
        lines.extend(["## Notes", ""])
        lines.extend(f"- {note}" for note in notes)
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def starter_manifest(url: str) -> dict[str, Any]:
    canonical = canonical_x_url(url)
    return {
        "url": canonical,
        "title": "",
        "author": {"name": "", "handle": ""},
        "published_at": "",
        "body_markdown": "",
        "media": [],
        "embeds": [],
        "screenshots": [],
    }


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", help="Extraction manifest JSON to package")
    parser.add_argument("--init-url", help="Create a starter source.json for this X URL")
    parser.add_argument("--out-dir", help="Output folder; defaults to ~/Documents/Saved Articles/X/<handle>-<status-id>")
    parser.add_argument("--library-root", help="Saved article library root when --out-dir is omitted")
    parser.add_argument(
        "--title-filename",
        action="store_true",
        help="Write <title-slug>.md instead of article.md",
    )
    parser.add_argument(
        "--absolute-media-links",
        action="store_true",
        help="Write absolute local image paths in Markdown for renderers that do not resolve relative links",
    )
    args = parser.parse_args()

    if args.init_url:
        data = starter_manifest(args.init_url)
        out_dir = resolve_out_dir(args.out_dir, args.library_root, data)
        out_dir.mkdir(parents=True, exist_ok=True)
        source_path = out_dir / "source.json"
        write_json(source_path, data)
        print(source_path)
        return 0

    if not args.manifest:
        parser.error("--manifest or --init-url is required")

    manifest_path = Path(args.manifest).expanduser().resolve()
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    out_dir = resolve_out_dir(args.out_dir, args.library_root, data)
    out_dir.mkdir(parents=True, exist_ok=True)
    media_dir = out_dir / "media"
    media_dir.mkdir(exist_ok=True)
    source_path = out_dir / "source.json"
    notes: list[str] = []
    markdown = render_markdown(data, media_dir, notes, args.absolute_media_links)
    markdown_path = out_dir / (title_filename(data) if args.title_filename else "article.md")
    markdown_path.write_text(markdown, encoding="utf-8")
    if manifest_path != source_path:
        write_json(source_path, data)
    print(markdown_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
