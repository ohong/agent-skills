#!/usr/bin/env python3
"""Archive an article URL and extract the main content as Markdown."""

from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from typing import Any


USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)
ARCHIVE_HOSTS = {
    "archive.ph",
    "archive.today",
    "archive.is",
    "archive.li",
    "archive.vn",
    "archive.md",
}
READER_PREFIX = "https://r.jina.ai/"
MIN_ARTICLE_CHARS = 600


@dataclass
class FetchResult:
    url: str
    final_url: str
    status: int
    content_type: str
    text: str


class FetchError(Exception):
    pass


class MainContentParser(HTMLParser):
    """Small dependency-free HTML to Markdown-ish block extractor."""

    block_tags = {
        "article",
        "blockquote",
        "figcaption",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "li",
        "p",
    }
    skip_tags = {"script", "style", "noscript", "svg", "canvas", "iframe", "form", "button"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.blocks: list[tuple[str, str]] = []
        self.title = ""
        self.metadata: dict[str, str] = {}
        self._current_tag: str | None = None
        self._current: list[str] = []
        self._skip_stack: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = {name.lower(): value or "" for name, value in attrs}
        if self._skip_stack:
            if tag not in {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}:
                self._skip_stack.append(tag)
            return
        if tag in self.skip_tags or tag in {"header", "nav", "footer", "aside"}:
            self._skip_stack.append(tag)
            return
        if tag == "meta":
            self._handle_meta(attrs_dict)
            return
        if tag == "title":
            self._start_block("title")
            return
        if tag == "br" and self._current_tag:
            self._current.append("\n")
            return
        if tag == "img" and self._current_tag:
            alt = clean_inline(attrs_dict.get("alt", ""))
            src = attrs_dict.get("src") or attrs_dict.get("data-src") or ""
            if alt and src and not looks_like_tracking_image(src):
                self._current.append(f" ![{alt}]({src}) ")
            return
        if tag in self.block_tags:
            self._start_block(tag)

    def handle_endtag(self, tag: str) -> None:
        if self._skip_stack:
            if tag in self._skip_stack:
                while self._skip_stack:
                    skipped = self._skip_stack.pop()
                    if skipped == tag:
                        break
            return
        if tag == self._current_tag:
            self._finish_block()

    def handle_data(self, data: str) -> None:
        if self._skip_stack or not self._current_tag:
            return
        self._current.append(data)

    def _handle_meta(self, attrs: dict[str, str]) -> None:
        key = (attrs.get("property") or attrs.get("name") or "").lower()
        value = attrs.get("content", "").strip()
        if not key or not value:
            return
        if key in {"og:title", "twitter:title"} and not self.metadata.get("title"):
            self.metadata["title"] = html.unescape(value)
        elif key in {"article:published_time", "date", "datepublished", "publishdate"}:
            self.metadata["published"] = html.unescape(value)
        elif key in {"author", "article:author"}:
            self.metadata["author"] = html.unescape(value)

    def _is_chrome(self, attrs: dict[str, str]) -> bool:
        blob = " ".join(
            attrs.get(name, "") for name in ("id", "class", "role", "aria-label", "data-testid")
        ).lower()
        return any(
            token in blob
            for token in (
                "advert",
                "banner",
                "breadcrumb",
                "cookie",
                "footer",
                "header",
                "modal",
                "nav",
                "newsletter",
                "paywall",
                "privacy",
                "promo",
                "related",
                "share",
                "sidebar",
                "subscribe",
            )
        )

    def _start_block(self, tag: str) -> None:
        if self._current_tag:
            self._finish_block()
        self._current_tag = tag
        self._current = []

    def _finish_block(self) -> None:
        tag = self._current_tag
        text = clean_inline(" ".join(self._current))
        self._current_tag = None
        self._current = []
        if not tag or not text:
            return
        if tag == "title":
            self.title = text
            return
        self.blocks.append((tag, text))


def slugify(value: str, fallback: str = "article") -> str:
    value = urllib.parse.urlparse(value).path.rsplit("/", 1)[-1] or value
    value = re.sub(r"https?://", "", value.lower())
    value = re.sub(r"[^a-z0-9]+", "-", value).strip("-")
    return value[:96] or fallback


def normalize_url(url: str) -> str:
    url = url.strip()
    if not url:
        raise ValueError("empty URL")
    parsed = urllib.parse.urlparse(url)
    if not parsed.scheme:
        url = "https://" + url
        parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError(f"unsupported URL: {url}")
    return urllib.parse.urlunparse((parsed.scheme, parsed.netloc, parsed.path or "/", "", parsed.query, ""))


def is_archive_url(url: str) -> bool:
    host = urllib.parse.urlparse(url).netloc.lower().removeprefix("www.")
    return host in ARCHIVE_HOSTS


def archive_candidates(url: str) -> list[str]:
    if is_archive_url(url):
        return [url]
    encoded = urllib.parse.quote(url, safe=":/?&=%#")
    return [
        f"https://archive.ph/newest/{encoded}",
        f"https://archive.ph/{encoded}",
        f"https://archive.today/newest/{encoded}",
        f"https://archive.today/{encoded}",
    ]


def fetch_url(url: str, timeout: int = 40) -> FetchResult:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,text/plain;q=0.8,*/*;q=0.7",
            "Accept-Language": "en-US,en;q=0.9",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read()
            charset = response.headers.get_content_charset() or "utf-8"
            text = raw.decode(charset, errors="replace")
            return FetchResult(
                url=url,
                final_url=response.geturl(),
                status=response.status,
                content_type=response.headers.get("Content-Type", ""),
                text=text,
            )
    except urllib.error.HTTPError as exc:
        raw = exc.read()
        charset = exc.headers.get_content_charset() or "utf-8"
        text = raw.decode(charset, errors="replace")
        return FetchResult(
            url=url,
            final_url=exc.geturl(),
            status=exc.code,
            content_type=exc.headers.get("Content-Type", ""),
            text=text,
        )
    except urllib.error.URLError as exc:
        raise FetchError(str(exc)) from exc


def is_archive_challenge(text: str) -> bool:
    lowered = text.lower()
    return (
        "one more step" in lowered
        and "security check" in lowered
        and ("captcha" in lowered or "grecaptcha" in lowered)
    )


def is_bad_article_text(markdown: str) -> bool:
    lowered = markdown.lower()
    if is_archive_challenge(markdown):
        return True
    noisy = sum(
        token in lowered
        for token in (
            "manage your consent preferences",
            "confirm my choices",
            "accept all",
            "reject all",
            "start free trial",
            "subscribe",
            "sign in",
            "privacy policy",
        )
    )
    return len(re.sub(r"\W+", "", markdown)) < MIN_ARTICLE_CHARS or noisy >= 5


def clean_inline(text: str) -> str:
    text = html.unescape(text)
    text = re.sub(r"[ \t\r\f\v]+", " ", text)
    text = re.sub(r"\s*\n\s*", "\n", text)
    return text.strip()


def normalize_for_match(text: str) -> str:
    text = re.sub(r"\|.*$", "", text)
    text = re.sub(r"[^a-z0-9]+", " ", text.lower())
    return re.sub(r"\s+", " ", text).strip()


def remove_markdown_link_noise(line: str) -> str:
    line = re.sub(r"\[\]\([^)]+\)", "", line)
    line = re.sub(r"!\[Image \d+:[^\]]*\]\([^)]+\)", "", line)
    line = re.sub(r"!\[Image \d+\]\([^)]+\)", "", line)
    return line.strip()


def noisy_line(line: str) -> bool:
    stripped = line.strip()
    lowered = stripped.lower()
    if not stripped:
        return False
    if len(stripped) <= 2:
        return True
    if re.fullmatch(r"[-*_ ]{3,}", stripped):
        return True
    if re.fullmatch(r"\d+\s+save this story", lowered):
        return True
    if lowered in {
        "essential",
        "performance",
        "functional",
        "social media",
        "save this story",
        "confirm my choices",
        "reject all",
        "accept all",
        "subscribe",
        "sign in",
        "back to top",
        "skip to main content",
    }:
        return True
    return any(
        token in lowered
        for token in (
            "manage your consent preferences",
            "these cookies",
            "privacy policy",
            "powered by",
            "start free trial",
            "already a subscriber",
            "newsletter",
            "more great",
            "related stories",
            "advertisement",
            "all rights reserved",
            "cookie",
            "targeted advertising",
            "sale/targeted",
            "to revisit this article",
        )
    )


def clean_markdown(markdown: str, title: str, warnings: list[str]) -> str:
    lines = [remove_markdown_link_noise(line.rstrip()) for line in markdown.splitlines()]
    title_norm = normalize_for_match(title)
    start = 0
    if title_norm:
        matches = []
        for index, line in enumerate(lines):
            if not line.lstrip().startswith("#"):
                continue
            line_norm = normalize_for_match(line.lstrip("# "))
            if title_norm and (title_norm in line_norm or line_norm in title_norm):
                matches.append(index)
        if matches:
            start = matches[-1]

    cleaned: list[str] = []
    content_chars = 0
    for raw in lines[start:]:
        line = raw.strip()
        if not line:
            if cleaned and cleaned[-1] != "":
                cleaned.append("")
            continue
        lowered = line.lower()
        if content_chars > 300 and (
            any(
                lowered.startswith(prefix)
                for prefix in (
                    "topics[",
                    "comments",
                    "join the discussion",
                    "more from wired",
                    "read more",
                    "you might also like",
                    "recommended",
                    "related articles",
                    "sign in or create account",
                )
            )
            or "you've read your last free article" in lowered
            or "you’ve read your last free article" in lowered
        ):
            if "you've read your last free article" in lowered or "you’ve read your last free article" in lowered:
                warnings.append("The source appears paywall-limited near the extracted article body.")
            break
        if noisy_line(line):
            if "start free trial" in lowered or "already a subscriber" in lowered:
                warnings.append("The source appears paywall-limited near the extracted article body.")
            continue
        cleaned.append(line)
        content_chars += len(re.sub(r"\W+", "", line))

    while cleaned and cleaned[-1] == "":
        cleaned.pop()
    return "\n".join(cleaned).strip()


def html_to_markdown(text: str, source_url: str, warnings: list[str]) -> tuple[str, dict[str, str]]:
    parser = MainContentParser()
    parser.feed(text)
    title = parser.metadata.get("title") or parser.title or title_from_url(source_url)
    title_norm = normalize_for_match(title)
    blocks = parser.blocks
    start = 0
    if title_norm:
        matches = [
            index
            for index, (tag, block) in enumerate(blocks)
            if tag.startswith("h") and (title_norm in normalize_for_match(block) or normalize_for_match(block) in title_norm)
        ]
        if matches:
            start = matches[-1]

    lines: list[str] = []
    chars = 0
    for tag, block in blocks[start:]:
        lowered = block.lower()
        if chars > 300 and (
            any(
                lowered.startswith(prefix)
                for prefix in (
                    "topics",
                    "comments",
                    "join the discussion",
                    "related",
                    "recommended",
                    "more from",
                    "read more",
                    "sign in or create account",
                )
            )
            or "you've read your last free article" in lowered
            or "you’ve read your last free article" in lowered
        ):
            if "you've read your last free article" in lowered or "you’ve read your last free article" in lowered:
                warnings.append("The source appears paywall-limited near the extracted article body.")
            break
        if noisy_line(block):
            continue
        if tag == "h1":
            lines.extend([f"# {block}", ""])
        elif tag == "h2":
            lines.extend([f"## {block}", ""])
        elif tag in {"h3", "h4", "h5", "h6"}:
            lines.extend([f"### {block}", ""])
        elif tag == "li":
            lines.append(f"- {block}")
        elif tag == "blockquote":
            lines.extend(["> " + block.replace("\n", "\n> "), ""])
        else:
            lines.extend([block, ""])
        chars += len(re.sub(r"\W+", "", block))

    markdown = "\n".join(lines).strip()
    markdown = clean_markdown(markdown, title, warnings)
    metadata = dict(parser.metadata)
    metadata["title"] = title
    return markdown, metadata


def parse_reader_output(text: str, warnings: list[str]) -> tuple[str, dict[str, str]]:
    metadata: dict[str, str] = {}
    body = text
    if "Markdown Content:" in text:
        header, body = text.split("Markdown Content:", 1)
        for line in header.splitlines():
            if ":" not in line:
                continue
            key, value = line.split(":", 1)
            key = key.strip().lower()
            value = value.strip()
            if key == "title":
                metadata["title"] = value
            elif key == "url source":
                metadata["source"] = value
            elif key == "published time":
                metadata["published"] = value
            elif key == "warning":
                warnings.append(value)
    title = metadata.get("title", "")
    markdown = clean_markdown(body, title, warnings)
    return markdown, metadata


def title_from_url(url: str) -> str:
    path = urllib.parse.urlparse(url).path.strip("/")
    if not path:
        return "Article Archive"
    slug = path.rsplit("/", 1)[-1]
    return re.sub(r"[-_]+", " ", slug).strip().title() or "Article Archive"


def unique_output_dir(base: Path, slug: str) -> Path:
    candidate = base / slug
    index = 2
    while candidate.exists() and any(candidate.iterdir()):
        candidate = base / f"{slug}-{index}"
        index += 1
    return candidate


def reader_url(url: str) -> str:
    return READER_PREFIX + url


def render_article(
    *,
    title: str,
    source_url: str,
    archive_url: str,
    extraction_path: str,
    markdown: str,
    metadata: dict[str, str],
    warnings: list[str],
) -> str:
    title = title.strip() or metadata.get("title") or title_from_url(source_url)
    body = markdown.strip()
    title_norm = normalize_for_match(title)
    body_lines = body.splitlines()
    if body_lines and body_lines[0].startswith("#") and title_norm in normalize_for_match(body_lines[0]):
        body = "\n".join(body_lines[1:]).strip()

    lines = [f"# {title}", ""]
    facts = [
        ("Source", source_url),
        ("Archive", archive_url),
        ("Author", metadata.get("author", "")),
        ("Published", metadata.get("published", "")),
        ("Extracted", dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()),
        ("Extraction", extraction_path),
    ]
    for label, value in facts:
        if value:
            lines.append(f"- **{label}:** {value}")
    lines.append("")
    if body:
        lines.extend([body, ""])
    if warnings:
        lines.extend(["## Notes", ""])
        for warning in dict.fromkeys(warnings):
            lines.append(f"- {warning}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def extract_from_html_file(path: Path, source_url: str, warnings: list[str]) -> tuple[str, dict[str, str]]:
    text = path.read_text(encoding="utf-8", errors="replace")
    if is_archive_challenge(text):
        raise FetchError("HTML file is an archive.ph security challenge, not an article snapshot")
    return html_to_markdown(text, source_url, warnings)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url", help="Original article URL or archive.ph/archive.today snapshot URL")
    parser.add_argument("--archive-url", help="Known archive.ph/archive.today snapshot URL for the article")
    parser.add_argument("--html-file", help="Browser-saved HTML to extract instead of fetching")
    parser.add_argument("--out-dir", help="Output directory; defaults to outputs/archive-article/<slug>")
    parser.add_argument("--no-reader-fallback", action="store_true", help="Do not fall back to the text reader")
    parser.add_argument("--timeout", type=int, default=40, help="Fetch timeout in seconds")
    args = parser.parse_args()

    input_url = normalize_url(args.url)
    provided_archive_url = normalize_url(args.archive_url) if args.archive_url else (input_url if is_archive_url(input_url) else "")
    archive_url = provided_archive_url
    archive_verified = False
    archive_attempts: list[str] = []
    source_url = input_url if not is_archive_url(input_url) else ""
    warnings: list[str] = []
    extraction_path = ""
    markdown = ""
    metadata: dict[str, str] = {}
    fetched: FetchResult | None = None

    base = Path(args.out_dir).expanduser().resolve() if args.out_dir else Path.cwd() / "outputs" / "archive-article"
    slug_source = source_url or archive_url or input_url
    out_dir = base if args.out_dir else unique_output_dir(base, slugify(slug_source))
    out_dir.mkdir(parents=True, exist_ok=True)

    try:
        if args.html_file:
            html_path = Path(args.html_file).expanduser().resolve()
            markdown, metadata = extract_from_html_file(html_path, source_url or archive_url or input_url, warnings)
            extraction_path = f"browser-saved HTML: {html_path}"
            (out_dir / "source.html").write_text(html_path.read_text(encoding="utf-8", errors="replace"), encoding="utf-8")
        else:
            for candidate in ([archive_url] if archive_url else archive_candidates(input_url)):
                if not candidate:
                    continue
                archive_attempts.append(candidate)
                fetched = fetch_url(candidate, timeout=args.timeout)
                candidate_archive_url = fetched.final_url if is_archive_url(fetched.final_url) else candidate
                (out_dir / "source.html").write_text(fetched.text, encoding="utf-8")
                if is_archive_challenge(fetched.text):
                    warnings.append(f"Archive source returned a security challenge: {candidate_archive_url}")
                    continue
                if fetched.status >= 400:
                    warnings.append(f"Archive fetch returned HTTP {fetched.status}: {candidate_archive_url}")
                    continue
                markdown, metadata = html_to_markdown(fetched.text, candidate_archive_url, warnings)
                if not is_bad_article_text(markdown):
                    archive_url = candidate_archive_url
                    archive_verified = True
                    extraction_path = "archive.ph snapshot"
                    break
                warnings.append(f"Archive extraction did not produce enough article text: {candidate_archive_url}")
                markdown = ""

            if not markdown and not args.no_reader_fallback:
                fallback_target = source_url or input_url
                fetched = fetch_url(reader_url(fallback_target), timeout=args.timeout)
                (out_dir / "reader.md").write_text(fetched.text, encoding="utf-8")
                reader_markdown, reader_meta = parse_reader_output(fetched.text, warnings)
                if reader_markdown and not is_archive_challenge(reader_markdown):
                    markdown = reader_markdown
                    metadata = reader_meta
                    extraction_path = "reader fallback for original URL"
                    warnings.append("Used reader fallback because archive.ph was unavailable or challenged.")

        if not markdown:
            raise FetchError("no article content extracted")
        if is_bad_article_text(markdown):
            warnings.append("Extracted content may be short, noisy, or paywall-limited; inspect article.md.")

        title = metadata.get("title") or title_from_url(source_url or archive_url or input_url)
        article = render_article(
            title=title,
            source_url=source_url or metadata.get("source") or input_url,
            archive_url=archive_url if archive_verified or provided_archive_url else "",
            extraction_path=extraction_path,
            markdown=markdown,
            metadata=metadata,
            warnings=warnings,
        )
        article_path = out_dir / "article.md"
        article_path.write_text(article, encoding="utf-8")
        write_json(
            out_dir / "source.json",
            {
                "input_url": input_url,
                "source_url": source_url or metadata.get("source") or input_url,
                "archive_url": archive_url if archive_verified or provided_archive_url else "",
                "attempted_archive_urls": archive_attempts,
                "archive_verified": archive_verified,
                "title": title,
                "metadata": metadata,
                "extraction_path": extraction_path,
                "warnings": list(dict.fromkeys(warnings)),
                "article_path": str(article_path),
            },
        )
        print(article_path)
        return 0
    except Exception as exc:  # noqa: BLE001
        write_json(
            out_dir / "source.json",
            {
                "input_url": input_url,
                "source_url": source_url or input_url,
                "archive_url": archive_url if archive_verified or provided_archive_url else "",
                "attempted_archive_urls": archive_attempts,
                "archive_verified": archive_verified,
                "error": str(exc),
                "warnings": list(dict.fromkeys(warnings)),
            },
        )
        print(f"error: {exc}", file=sys.stderr)
        print(f"diagnostics: {out_dir / 'source.json'}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
