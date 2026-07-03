---
name: search-x
description: Find X/Twitter posts when the user remembers only the high-level message, mood, examples, author vibe, adjacent article, or partial/inexact wording. Use for semantic search over X posts, quote posts, replies, threads, bookmarks, or profiles, especially when exact keywords may be wrong, the post may not be indexed by normal web search, or logged-in X/browser state may reveal more than anonymous search.
---

# Search X

## Goal

Find the actual X post the user is thinking of, even when their remembered details are fuzzy or wrong. Optimize for semantic triangulation and direct verification, not for matching the first literal query.

## Core Principle

Treat the user's prompt as a noisy memory. Preserve its semantic fingerprint while actively testing which specifics may be wrong:

- **Message**: the claim, take, thesis, joke, critique, or emotional point.
- **Anchors**: remembered examples, names, links, dates, author handles, screenshots, quote-tweet targets.
- **Surface**: original post, quote post, reply, thread, article link post, bookmark, or profile post.
- **Wording risk**: examples may be categories, brands may be implied, and "quote tweet" may actually be a link post or reply.

Do not stop at a plausible result unless it matches the semantic fingerprint and is verified on the live post page.

## Source Order

Use the strongest available surfaces in this order, adjusting for the task:

1. **Live/logged-in X**: use browser/Chrome when quote tabs, search, bookmarks, hidden posts, profile timelines, or logged-in visibility matter.
2. **X search URLs**: use `x.com/search?q=...&f=live` for exact phrase, concept, and operator searches.
3. **The target post/profile itself**: inspect quote tabs, replies, repost/quote activity, and profile timelines.
4. **Web search**: use Google/Bing-style web results for indexed snippets, mirrored tweet text, newsletters, or articles.
5. **Clue engines**: Grok or another search assistant can suggest phrases/handles, but never accept its answer without live-post verification.

## Workflow

### 1. Build the semantic fingerprint

Write down a compact fingerprint before searching:

- One sentence for the remembered thesis.
- Exact anchors the user supplied.
- Likely synonyms and category substitutions.
- Things that might be wrong.

Example:

```text
Thesis: Popular tech people consciously like is embodied/physical.
Anchors: Midjourney Medical, ultrasound AI, Instacart, Waymo/robotaxi.
Risk: Instacart may be "same-day grocery"; Waymo may be "robotaxis"; quote-tweet may be a Bloomberg link post.
```

### 2. Verify the literal path first

If the user gives a URL, author, or quote-tweet target:

- Open the target post.
- Inspect the post page and activity surface: quotes, replies, thread context, reposts when relevant.
- Search within visible results for exact anchors and synonyms.
- Open long candidates because previews often hide the important line behind "Show more."

If the literal path fails, record why: no results, unrelated results, quote tab only shows top-ranked posts, search operators unsupported, login wall, or candidate mismatch.

### 3. Generate query ladders

Run searches in ladders, not random rewrites. Start narrow, then relax one assumption at a time.

**Exact phrase ladder**

- Quoted phrases from the user.
- Distinctive two-term combinations.
- Partial remembered clauses.

**Anchor ladder**

- `brand + concept`: `Midjourney ultrasound`, `Waymo physical`
- `example + category`: `Instacart robotaxi`, `same-day grocery robotaxis`
- `article/product + take`: `Midjourney scanner physical`, `ultrasound AI real world`

**Semantic ladder**

- Replace brands with categories: `Instacart` -> `same-day grocery`, `grocery delivery`; `Waymo` -> `robotaxis`, `self-driving rides`.
- Replace adjectives: `physical` -> `real world`, `IRL`, `atoms`, `embodied`, `hardware`.
- Replace verbs: `people like` -> `people love`, `consciously like`, `improves life`, `favorite`, `actually use`.

**Surface ladder**

- Target quote search.
- Plain X search.
- Profile search for likely authors.
- Web search with exact snippets.
- Article/news search if the post links an article rather than quoting the original post.

### 4. Search for clue phrases, not just facts

When a query nearly works, mine it for unexpected vocabulary. A single odd phrase can unlock the match.

Examples of clue phrases:

- "people consciously like"
- "same-day grocery"
- "bits to atoms"
- "real-world data"
- "unbreakable screens"

Search these phrases exactly on X and the web. If a clue engine suggests handles or phrases, verify each directly.

### 5. Inspect candidates rigorously

For each candidate, check:

- Does the author/handle match any remembered vibe or network?
- Does the post contain the thesis, not just one keyword?
- Are examples exact, categorical, or adjacent?
- Does it reference the same object through a quote, reply, article link, screenshot, or thread?
- Is the date plausible relative to the original event?

Open the direct status URL. Do not rely on search result snippets alone.

### 6. Deliberately relax wrong assumptions

If no exact result appears after strong searches, test likely memory distortions:

- "Quote tweet" may be a link post about the same news.
- Named examples may be generic categories.
- The remembered brand may be absent but implied.
- The author may have replied or threaded instead of posting standalone.
- X search may omit older/lower-ranked/low-engagement posts.
- A post may be deleted, protected, translated, or only visible while logged in.

Make each relaxation explicit in your reasoning and keep searching until either a match is verified or the remaining uncertainty is concrete.

## Useful X Queries

Use URL encoding as needed.

```text
"exact phrase"
brand category
brand1 brand2 concept
"rare phrase" OR "alternate phrase"
from:handle phrase
to:handle phrase
filter:links phrase
min_faves:10 phrase
since:YYYY-MM-DD until:YYYY-MM-DD phrase
url:domain.com/article-slug
```

Do not assume every advanced operator works consistently on X. If an operator returns nothing where results should exist, switch surfaces instead of repeating it.

## Verification Standard

Before answering, provide:

- Author display name and handle.
- Direct post URL.
- The matching text or a short paraphrase of the decisive line.
- Any caveat about mismatch against the user's remembered parameters.

If the best match is not exact, say why it is still likely: same thesis, same examples/categories, same linked object, same timing, or same author context.

## Failure Handling

If no match is found:

- Report the highest-signal searches and surfaces checked.
- List the closest candidates and why each failed.
- Name the most likely failure mode: deleted/protected post, non-indexed quote, wrong examples, wrong source post, or login-limited visibility.
- Suggest the single next best input from the user: screenshot, approximate date, likely author, remembered reply/quote target, or whether they liked/bookmarked it.
