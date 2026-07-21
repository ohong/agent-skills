# Web Articles

Convert one article URL into a local Markdown archive. Prefer an archive.ph/archive.today snapshot as the source of truth, then extract only the main article body.

## Quick Start

Run the bundled helper with the URL:

```bash
python3 scripts/archive_article.py \
  "https://www.wired.com/story/opal-electronics-openai-investment-ai-powered-audio-gadget/" \
  --out-dir "$HOME/Documents/Saved Articles/Web/opal-electronics-ai-audio-gadget"
```

When the user does not specify a destination, create a URL-derived folder under the shared article library and pass it with `--out-dir`:

```text
~/Documents/Saved Articles/Web/<article-slug>/<article-title>.md
```

If the user already provides an archive.ph URL, pass it directly:

```bash
python3 scripts/archive_article.py \
  "https://archive.ph/pbb2L" \
  --out-dir "$HOME/Documents/Saved Articles/Web/opal-electronics-ai-audio-gadget"
```

If the original URL and archive URL are both known, preserve both:

```bash
python3 scripts/archive_article.py \
  "https://www.wired.com/story/opal-electronics-openai-investment-ai-powered-audio-gadget/" \
  --archive-url "https://archive.ph/pbb2L" \
  --out-dir "$HOME/Documents/Saved Articles/Web/opal-electronics-ai-audio-gadget"
```

## Workflow

1. Run `scripts/archive_article.py` with the user-provided URL and resolved output directory.
2. Inspect the generated title-named Markdown file before responding.
3. If the script reports an archive.ph captcha/security challenge:
   - Do not ask the user what to do.
   - Use Browser or Chrome to open the archive URL if available, complete only user-authorized visible navigation, save the page HTML if accessible, then rerun with `--html-file`.
   - If archive.ph remains inaccessible, accept the script's reader fallback only when the Markdown contains meaningful article text and clearly notes the fallback source.
4. If the Markdown is mostly consent text, nav, ads, paywall prompts, or "One more step", treat the run as failed and retry with an archive URL or browser-saved HTML.

## Output Contract

Each successful run should produce:

- `<article-title>.md`: title, source URL, archive URL when known, extraction metadata, and cleaned article content. The filename must use a filesystem-safe version of the extracted title, not `article.md`.
- `source.json`: extraction metadata, fetch path, warnings, and output paths.
- `source.html` or `reader.md`: saved diagnostics when the helper fetched useful source material or hit an access challenge.

Keep the final answer short and include the absolute path to the title-named Markdown file.

## Useful Options

```bash
python3 scripts/archive_article.py --help
```

Common flags:

- `--out-dir /path/to/folder`: choose the output folder.
- `--archive-url URL`: use a known archive.ph/archive.today snapshot while preserving the original URL.
- `--html-file /path/to/page.html`: extract from a browser-saved archive snapshot.
- `--no-reader-fallback`: fail instead of falling back to a text reader for the original URL.

## Quality Bar

- Preserve the original source URL and archive snapshot URL when available.
- Extract the article body, not page chrome.
- Include warnings for archive challenges, paywall-limited fallbacks, or suspiciously short output.
- Do not invent article text, author names, dates, or archive URLs.
