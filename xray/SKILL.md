---
name: xray
description: >
  X-ray a YC vertical: query 5,700+ companies, surface trends and failure
  patterns, rank rebuild candidates, then generate a data journalism page
  with NYT/FT-quality charts via the /data-storytelling skill.
user-invokable: true
args:
  - name: vertical
    description: The vertical to analyze (e.g., "fintech", "healthcare", "devtools")
    required: true
  - name: categories
    description: Comma-separated YC categories to match (e.g., "Fintech,Payments,Banking")
    required: false
  - name: keywords
    description: Comma-separated keywords for description search (e.g., "payment,lending,crypto")
    required: false
---

# /xray — YC Vertical Deep Dive

X-ray a vertical across the full Startups.RIP database: census, trends, failure patterns, and top rebuild candidates — then generate a reporter-style data journalism page.

## What it produces

1. `lib/{vertical}-data.ts` — All data constants (census, sub-verticals, batch trends, top 10 rebuild candidates, timing cases, trend insights)
2. `app/{vertical}/page.tsx` — SSR page with SEO metadata
3. `components/{vertical}/` — Two-tab client page (Original Report + Data Story)
4. D3 chart components in `components/charts/` — built using the **`/data-storytelling` skill** for NYT/FT-quality visualizations

## Process

### Phase 1 — Data collection (Supabase queries)

Query the `companies` table using two signals, then union and deduplicate on `slug`.

**Primary: Category overlap**
```sql
SELECT * FROM companies
WHERE categories && ARRAY[{categories}]
```

**Secondary: Keyword search**
```sql
SELECT * FROM companies
WHERE one_liner ILIKE '%{keyword}%' OR long_description ILIKE '%{keyword}%'
AND NOT (categories && ARRAY[...])
```

Use the Supabase MCP tool (`mcp__claude_ai_Supabase__execute_sql`) with project ID `emtudktizargujokhjhc`.

Then compute aggregates:
- Status breakdown (active/dead/acquired) + rates vs YC overall (5,728 total, 17.5% death, 12.8% acquired)
- Batch/year trend (aggregate by year from `yc_batch`, format: "Winter 2022", "Summer 2021", etc.)
- Sub-vertical classification
- Join with `analysis_results` for existing reports on dead/acquired companies

### Phase 2 — Agent team (3 agents, 1+2 parallel → 3 sequential)

**Agent 1: Census & Trends Analyst** — Identify 5-8 trend insights (headline, key stat, analysis, chart recommendation). Focus on counter-intuitive patterns.

**Agent 2: Rebuild Candidate Ranker** — Score dead companies on rebuild potential (1-10) across four inflection types: regulatory, technology (AI), market, distribution. Select top 10 with structured rationale. Use existing `analysis_results` reports + training knowledge, no live web search.

Agents 1 and 2 run **in parallel**.

**Agent 3: Narrative Writer** — Combine outputs from Agents 1+2 into a five-act story outline (headline, acts, chart placements, transitions) and complete TypeScript data constants matching `lib/fintech-data.ts` format.

### Phase 3 — Write data file

Create `lib/{vertical}-data.ts` with exports: `CENSUS`, `YC_OVERALL`, `STATUS_COMPARISON`, `SUB_VERTICALS`, `SUB_VERTICAL_STATS`, `BATCH_YEARS`, `TOP_10_REBUILD`, `TIMING_CASES`, `TREND_INSIGHTS`, `METHODOLOGY_TEXT`.

Follow the exact format of `lib/fintech-data.ts`.

### Phase 4 — Build page (using /data-storytelling)

**Tab 1: Original Report** — Scaffold from `components/fintech/original-report.tsx`. Tables, inline bars, census stats. Pure data reference.

**Tab 2: Data Story** — This is where the `/data-storytelling` skill takes over. When building the data story tab and its chart components:

1. **Invoke `/data-storytelling`** to guide all visualization decisions
2. Follow its design philosophy: "Don't make charts for chart people. Make stories for all people."
3. Apply its story-first chart selection table (map insight type → chart type)
4. Follow its visual design rules: fewer hues more shades, direct labels over legends, subtitle = takeaway, mute secondary data
5. Apply its responsive design rules: separate aspect ratios for desktop/mobile, charts get taller on mobile, touch targets >= 44px
6. Follow its accessibility requirements: `aria-label` states the insight (not "chart"), `prefers-reduced-motion`, hidden data tables, colorblind-safe palettes
7. Use its narrative arc structure: Setup ("here's what you'd expect") → Tension ("but look at this") → Resolution ("this matters because")

Chart components should follow the D3+React pattern: "D3 for math, React for DOM." Use `useResizeObserver` and `useChartInteraction` hooks from `components/charts/`.

Scaffold page files:
- `app/{vertical}/page.tsx` — from `app/fintech/page.tsx`
- `components/{vertical}/{vertical}-page-client.tsx` — from `components/fintech/fintech-page-client.tsx`
- `components/{vertical}/original-report.tsx` — from `components/fintech/original-report.tsx`
- `components/{vertical}/data-story.tsx` — from `components/fintech/data-story.tsx`
- Reuse `components/canada/tab-toggle.tsx` directly (generic)
- Create chart components in `components/charts/` using `/data-storytelling` principles

### Phase 5 — Verify

- `bun run build` — type-check passes
- `bun run lint` — no new lint errors
- Visual check at `localhost:3000/{vertical}`

## Template files

| File | Role |
|---|---|
| `lib/fintech-data.ts` | Data file structure + TypeScript types |
| `components/fintech/data-story.tsx` | Five-act narrative component |
| `components/fintech/original-report.tsx` | Data reference tab |
| `components/fintech/fintech-page-client.tsx` | Two-tab client wrapper |
| `components/canada/tab-toggle.tsx` | Generic tab toggle (reuse) |
| `components/charts/fintech-batch-trend-chart.tsx` | D3 bar chart pattern |
| `components/charts/subvertical-chart.tsx` | D3 horizontal bar chart |
| `components/charts/rebuild-candidates-chart.tsx` | D3 ranked bar chart |

## Key data

- Supabase project: `emtudktizargujokhjhc` (Startups.RIP)
- YC batch format: "Winter 2022", "Summer 2021", "Fall 2024", "Spring 2025"
- Company statuses: "active", "inactive" (dead), "acquired"
- Total YC companies: 5,728 | Death rate: 17.5% | Acquired rate: 12.8%
