# X Posts, Threads, and Articles

## Overview

Create a self-contained Markdown archive from an X URL. Preserve readable text as Markdown, keep X posts as live tweet embeds where possible, and store photos/screenshots/media in a sibling folder.

Final user-facing archives belong in the saved article library, not a repo scratch directory:

- Default library root: `~/Documents/Saved Articles/X/`
- Default archive folder: title slug, for example `getting-started-with-loops/`
- Markdown filename: matching title slug, for example `getting-started-with-loops.md`
- Companion files: `source.json` and `media/`

## Output Contract

Given a single X URL, produce:

- `<title-slug>.md`: clean Markdown with source metadata, article/post content, tweet embed blocks, local image links, and notes about any fallback screenshots.
- `media/`: downloaded images, copied local screenshots, video thumbnails, and other media assets referenced by relative paths.
- `source.json`: optional extraction manifest used to build the archive.

Use `~/Documents/Saved Articles/X/` for user-facing deliverables. Use `outputs/` only for temporary scratch work when explicitly requested or when the user asks to keep the archive inside the current repo.

## Workflow

1. Normalize and inspect the URL.
   - Accept `https://x.com/{handle}/status/{id}` and `https://twitter.com/{handle}/status/{id}`.
   - Keep the canonical source URL in the Markdown.
   - Derive the final archive folder and Markdown filename from the article title. Use `{handle}-{id}` only as a fallback when no title is available yet, such as a starter manifest.

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
   - Use title-slug folders and title-slug Markdown filenames for saved-article library entries; do not leave final deliverables named `article.md` or store them in opaque status-id folders.
   - For Codex app/local previews, write absolute media links so images render instead of placeholders.
   - Open or inspect the final Markdown and media folder before responding.
   - Validate media by checking the image files are non-empty and recognized as real image files, not just that Markdown links point somewhere.

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

Run this for the normal saved-articles library flow:

```bash
python3 scripts/package_x_article.py \
  --manifest /path/to/source.json \
  --title-filename \
  --absolute-media-links
```

When `--out-dir` is omitted, the packager writes to `~/Documents/Saved Articles/X/<title-slug>/`. If the manifest title is blank, the fallback folder is `<handle>-<status-id>/` until the title is known.

Use `--out-dir /path/to/output-folder` only when the user asks for a specific destination. Use `--library-root /path/to/library` to change the saved-articles library root.

To create a starter manifest:

```bash
python3 scripts/package_x_article.py \
  --init-url "https://x.com/handle/status/id" \
  --library-root "~/Documents/Saved Articles/X"
```

## Quality Bar

- The Markdown should read like an article archive, not a dump of X UI text.
- Every local media reference in the Markdown file must point to an existing file.
- In Codex app/local Markdown previews, use absolute local media paths; relative `media/...` links can render as gray placeholders even when the files exist.
- Verify media with `file path/to/media/*` or equivalent image inspection so failed downloads/placeholders are caught.
- Every embedded tweet should include a source URL and either a live embed block or a local screenshot/fallback text.
- Preserve source attribution and avoid inventing unavailable text, dates, authors, or alt text.
- Mention any inaccessible media or screenshot fallbacks in a short note at the end of the Markdown.

## Resource

- `scripts/package_x_article.py`: packages an extraction manifest into a title-slug Markdown archive, downloads/copies media into `media/`, and creates a starter manifest when needed.
