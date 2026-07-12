# Query Ladders

Relax one assumption at a time. Mine near-matches for unusual vocabulary, then search those clue phrases exactly on X and the web.

## Exact phrase

- Quoted remembered phrases
- Distinctive two-term combinations
- Partial clauses

## Anchors

- `brand + concept`
- `example + category`
- `article or product + take`

Example: search `Waymo physical`, then relax it to `robotaxi real world` or `self-driving embodied`.

## Semantic substitutions

- Replace brands with categories: `Instacart` → `grocery delivery`.
- Replace adjectives: `physical` → `real world`, `IRL`, `atoms`, `embodied`, `hardware`.
- Replace verbs: `people like` → `people love`, `actually use`, `improves life`.

## Surfaces

1. Target quote search
2. Plain X search
3. Likely-author profile search
4. Web search with exact snippets
5. Article/news search when the post may link rather than quote

## Useful X queries

```text
"exact phrase"
brand category
"rare phrase" OR "alternate phrase"
from:handle phrase
to:handle phrase
filter:links phrase
min_faves:10 phrase
since:YYYY-MM-DD until:YYYY-MM-DD phrase
url:domain.com/article-slug
```

Operators are inconsistent. Switch surfaces when an operator returns implausibly empty results.

## Common memory distortions

- A “quote tweet” may be a reply or a link post about the same news.
- A remembered brand may appear only as its category.
- The author may have posted in a thread or reply.
- X may omit older, low-ranked, deleted, protected, or login-only posts.
- The remembered wording may come from an attached screenshot or article rather than the post text.
