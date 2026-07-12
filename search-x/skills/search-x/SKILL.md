---
name: search-x
description: Find a specific remembered X post from fuzzy clues and verify it on the live post. Use when exact wording or the author is unknown.
---

# Search X

Find the actual post behind a noisy memory. Optimize for semantic triangulation and direct verification, not the first plausible keyword match.

## Workflow

1. Build a compact semantic fingerprint:
   - remembered thesis or emotional point;
   - concrete anchors such as examples, names, links, dates, or screenshots;
   - likely synonyms and category substitutions;
   - details that may be wrong, including author, wording, or post type.

2. Search the strongest available surfaces:
   - logged-in X for bookmarks, quote tabs, replies, profiles, and hidden posts;
   - X live search for phrases, concepts, and operators;
   - direct post or profile pages for surrounding context;
   - web search for indexed snippets, mirrors, newsletters, or linked articles.

3. If a URL, author, or quoted post is known, inspect that literal path first. Open long candidates because previews may hide the decisive line. Record why a path fails before relaxing it.

4. Run query ladders instead of random rewrites. Read [references/query-ladders.md](references/query-ladders.md) for the ladder patterns, X operators, and common memory distortions.

5. Inspect each candidate against the whole fingerprint:
   - Does it express the thesis, not merely share one keyword?
   - Are the remembered examples exact, categorical, or adjacent?
   - Is the claim carried by a quote, reply, thread, screenshot, or linked article?
   - Does the author context and date fit?

6. Open the direct status URL and verify it on the live page. Search assistants may suggest clues, but never treat their answer as verification.

## Result

Return:

- author display name and handle;
- direct post URL;
- a short paraphrase of the decisive match;
- any mismatch against the user's remembered details.

If no post is verified, report the highest-signal surfaces searched, the closest candidates and why they failed, the likely failure mode, and the single most useful missing clue.
