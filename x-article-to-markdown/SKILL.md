---
name: x-article-to-markdown
description: Convert an X/Twitter article, post, status, or thread URL into a clean local Markdown archive with a companion media asset folder. Use when the user provides an x.com or twitter.com URL and wants a Markdown file preserving article text, tweet embeds, quoted posts, photos, video thumbnails, screenshots, and other local media assets.
---

# X Article to Markdown

## Overview

Create a self-contained Markdown archive from an X URL. Preserve readable text as Markdown, keep X posts as live tweet embeds where possible, and store photos/screenshots/media in a sibling folder with relative links.

## Output Contract

Given a single X URL, produce:

- `article.md`: clean Markdown with source metadata, article/post content, tweet embed blocks, local image links, and notes about any fallback screenshots.
- `media/`: downloaded images, copied local screenshots, video thumbnails, and other media assets referenced by relative paths.
- `source.json`: optional extraction manifest used to build the archive.

Use `outputs/` for user-facing deliverables when working in a Codex projectless workspace.

## Workflow

1. Normalize and inspect the URL.
   - Accept `https://x.com/{handle}/status/{id}` and `https://twitter.com/{handle}/status/{id}`.
   - Keep the canonical source URL in the Markdown.
   - Derive a stable output slug from `{handle}-{id}` when no output name is requested.

2. Load the page.
   - Prefer the Browser or Chrome plugin when the page requires a logged-in session, expanded long-form article text, or interactive media.
   - Prefer structured DOM/accessibility text over OCR. Use screenshots only for media fallback, visual verification, or content that cannot be extracted as text.
   - Expand "Show more", article body, replies/thread continuations, quoted posts, alt text dialogs, and media viewers when needed.

3. Extract the article/post content.
   - Preserve author name, handle, publish date/time, source URL, body text, headings, lists, links, and meaningful line breaks.
   - Remove UI chrome: counts, buttons, nav labels, ads, "For you", sign-in prompts, and unrelated replies unless the user asked to include replies.
   - For a thread, include posts in order with each post's source URL.

4. Preserve embeds and media.
   - For each quoted/embedded tweet, include a live embed block when a tweet URL is available:

```html
<blockquote class="twitter-tweet"><a href="https://x.com/handle/status/id"></a></blockquote>
```

   - Also include a short fallback quote or local screenshot when the embedded tweet's text/media is important.
   - Download original image URLs when possible. For X images, prefer the largest accessible variant.
   - For videos, download a thumbnail or take a screenshot unless a direct media file is plainly available and appropriate to save.
   - Capture screenshots of media, quoted posts, or article sections when downloads are blocked or when the visual layout matters.

5. Build the archive.
   - Create an extraction manifest and run `scripts/package_x_article.py` from this skill directory.
   - Keep paths relative in the generated Markdown so the archive can be moved as a folder.
   - Open or inspect the final Markdown and media folder before responding.

## Extraction Manifest

Use this JSON shape with the packaging script. Omit fields that are unknown.

```json
{
  "url": "https://x.com/RLanceMartin/status/2064397389189071163",
  "title": "Optional title",
  "author": {"name": "Author Name", "handle": "handle"},
  "published_at": "2026-06-09T12:34:56Z",
  "body_markdown": "Clean article/post text in Markdown.",
  "media": [
    {
      "url": "https://pbs.twimg.com/media/example.jpg?format=jpg&name=large",
      "alt": "Meaningful alt text if available",
      "caption": "Optional caption",
      "kind": "image"
    }
  ],
  "embeds": [
    {
      "url": "https://x.com/other/status/123",
      "text_markdown": "Fallback quoted tweet text.",
      "author": {"name": "Other Author", "handle": "other"},
      "media": []
    }
  ],
  "screenshots": [
    {
      "path": "/absolute/path/to/screenshot.png",
      "caption": "Screenshot fallback for blocked media"
    }
  ]
}
```

Run:

```bash
python scripts/package_x_article.py \
  --manifest /path/to/source.json \
  --out-dir /path/to/output-folder
```

To create a starter manifest:

```bash
python scripts/package_x_article.py \
  --init-url "https://x.com/handle/status/id" \
  --out-dir /path/to/output-folder
```

## Quality Bar

- The Markdown should read like an article archive, not a dump of X UI text.
- Every local media reference in `article.md` must point to an existing file.
- Every embedded tweet should include a source URL and either a live embed block or a local screenshot/fallback text.
- Preserve source attribution and avoid inventing unavailable text, dates, authors, or alt text.
- Mention any inaccessible media or screenshot fallbacks in a short note at the end of the Markdown.

## Resource

- `scripts/package_x_article.py`: packages an extraction manifest into `article.md`, downloads/copies media into `media/`, and creates a starter manifest when needed.
