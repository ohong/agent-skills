# Visual Vocabulary — Chart Type Reference

Full taxonomy of chart types organized by story type. Based on the FT Visual Vocabulary with editorial extensions.

Use this as a lookup when you know the **story you want to tell** but need the right **chart type** to tell it.

---

## Quick Reference Decision Tree

```
What's the story?
├── How far from a baseline?           → Deviation
├── Do these move together?            → Correlation
├── Which is biggest/smallest?         → Ranking
├── What does the spread look like?    → Distribution
├── How has it changed?                → Change Over Time
├── What share does each part have?    → Part-to-Whole
├── How big is it?                     → Magnitude
├── Where is it happening?             → Spatial
└── Where does it flow?                → Flow
```

---

## Deviation

Show how values differ from a baseline, reference point, or target.

### Diverging Bar Chart
- Bars extend left/right (or up/down) from a central baseline
- **Use when**: comparing positive/negative deviations across categories
- **Use when**: showing surplus/deficit, profit/loss, above/below average
- **Avoid when**: categories have no natural baseline
- D3: `d3-scale` (linear, band), `d3-axis`

### Diverging Stacked Bar
- Stacked bars split at a neutral center point (e.g., Likert scale)
- **Use when**: survey responses with agree/disagree spectrum
- **Use when**: showing opinion distribution across groups
- **Avoid when**: fewer than 3 response categories
- D3: `d3-scale`, `d3-shape` (stack with offset)

### Surplus/Deficit Fill
- Area between two lines (actual vs. expected) filled with contrasting colors
- **Use when**: showing when actual exceeds or falls below a target over time
- **Use when**: budget vs. actual, forecast vs. observed
- **Avoid when**: the two lines rarely cross (just use a line chart)
- D3: `d3-shape` (area), `d3-scale`

### Spine Chart
- Back-to-back horizontal bars from a center axis, each side a different category
- **Use when**: comparing two groups (male/female, before/after)
- **Avoid when**: more than two groups
- D3: `d3-scale` (band, linear)

---

## Correlation

Show the relationship between two or more variables.

### Scatter Plot
- Points positioned by two continuous variables
- **Use when**: exploring relationship between two measures
- **Use when**: looking for clusters, outliers, or trends
- **Avoid when**: one variable is categorical (use strip plot)
- D3: `d3-scale` (linear), `d3-shape` (symbol)

### Connected Scatter Plot
- Scatter plot with points connected chronologically
- **Use when**: showing how two variables co-evolve over time
- **Use when**: revealing loops, spirals, or directional shifts
- **Avoid when**: time dimension isn't meaningful
- D3: `d3-shape` (line), `d3-scale` (linear)

### Bubble Chart
- Scatter plot where point size encodes a third variable
- **Use when**: adding a magnitude dimension to a correlation
- **Avoid when**: the size variable has small range (differences won't be visible)
- **Avoid when**: you have more than ~50 bubbles (overlap)
- D3: `d3-scale` (sqrt for area), `d3-shape` (symbol)

### Heatmap Matrix
- Grid cells colored by intensity of relationship
- **Use when**: showing correlation matrix across many variables
- **Use when**: time × category patterns (e.g., activity by hour and day)
- **Avoid when**: fewer than 5 variables (just show scatter plots)
- D3: `d3-scale` (band, sequential), `d3-color`

---

## Ranking

Show the relative position of items — which is biggest, smallest, or how ordering changes.

### Ordered Bar Chart
- Horizontal bars sorted by value
- **Use when**: comparing magnitude across 5–30 categories
- **Use when**: the ranking itself is the story
- **Avoid when**: fewer than 5 items (just state the numbers)
- D3: `d3-scale` (band, linear), `d3-axis`

### Slope Chart
- Two vertical axes connected by lines showing rank or value change
- **Use when**: showing ranking changes between two time points
- **Use when**: highlighting overtakers and decliners
- **Avoid when**: more than 2 time points (use bump chart)
- D3: `d3-scale` (point, linear)

### Bump Chart
- Lines showing rank position over multiple time periods
- **Use when**: tracking ranking changes over 3+ time periods
- **Use when**: showing competitive positioning over time
- **Avoid when**: values matter more than rank (use line chart)
- D3: `d3-scale` (point, linear), `d3-shape` (line with curve)

### Lollipop Chart
- Dot on a stick — circle at value, thin line to baseline
- **Use when**: same as bar chart, but cleaner with many categories
- **Use when**: reducing visual weight vs. thick bars
- **Avoid when**: few categories (bar chart is clearer)
- D3: `d3-scale` (band, linear)

---

## Distribution

Show how data is spread — frequency, density, range, and outliers.

### Histogram
- Bars showing frequency within binned ranges
- **Use when**: showing shape of a single continuous distribution
- **Use when**: identifying skew, modality, outliers
- **Avoid when**: comparing distributions (use density or violin)
- D3: `d3-array` (bin), `d3-scale`, `d3-axis`

### Density Plot
- Smooth curve estimating the probability distribution
- **Use when**: comparing 2–4 overlapping distributions
- **Use when**: shape matters more than exact counts
- **Avoid when**: sample size < 30 (too few points for reliable KDE)
- D3: `d3-shape` (area), kernel density estimation

### Box Plot
- Min, Q1, median, Q3, max with outlier dots
- **Use when**: comparing distributions across 5+ categories
- **Use when**: highlighting median and spread simultaneously
- **Avoid when**: audience isn't statistical (use strip or violin)
- D3: `d3-scale`, `d3-array` (quantile)

### Violin Plot
- Mirrored density curves showing distribution shape
- **Use when**: comparing distribution shapes across categories
- **Use when**: showing bimodality or skew that box plots hide
- **Avoid when**: fewer than 3 groups (density plot is clearer)
- D3: `d3-shape` (area), kernel density estimation

### Strip Plot (Jitter)
- Individual points scattered along one axis
- **Use when**: showing individual observations (< 500 points)
- **Use when**: distributions with interesting outliers
- **Avoid when**: too many points (use density or histogram)
- D3: `d3-scale`, random jitter

### Beeswarm Plot
- Points packed without overlap, forming a density shape
- **Use when**: showing individual observations AND distribution shape
- **Use when**: each point needs to be identifiable (hover, color-coded)
- **Avoid when**: more than ~300 points (gets slow)
- D3: `d3-force` (collision), `d3-scale`

### Ridgeline Plot (Joy Plot)
- Stacked, overlapping density curves
- **Use when**: comparing many distributions (10+) along a sequence
- **Use when**: showing temporal evolution of distributions
- **Avoid when**: fewer than 5 distributions
- D3: `d3-shape` (area), kernel density estimation

---

## Change Over Time

Show trends, patterns, and temporal evolution.

### Line Chart
- Connected points showing values over time
- **Use when**: showing trends for 1–5 series
- **Use when**: time is continuous and regularly spaced
- **Avoid when**: more than 5 lines (spaghetti — use small multiples)
- D3: `d3-shape` (line), `d3-scale` (time, linear)

### Area Chart
- Line chart with filled area below
- **Use when**: emphasizing volume or magnitude over time
- **Use when**: showing cumulative totals
- **Avoid when**: comparing multiple series (overlap obscures)
- D3: `d3-shape` (area), `d3-scale` (time, linear)

### Stacked Area Chart
- Multiple areas stacked showing composition over time
- **Use when**: showing both total and composition changing
- **Use when**: parts are additive and sum is meaningful
- **Avoid when**: individual series need precise comparison (use small multiples)
- D3: `d3-shape` (area, stack), `d3-scale`

### Small Multiples (Line)
- Grid of identical line charts, one per series
- **Use when**: comparing 6+ series without overlap
- **Use when**: each series has its own story worth seeing
- **Avoid when**: fewer than 4 series (just overlay them)
- D3: repeated chart pattern with shared scales

### Sparkline
- Tiny line chart embedded in text or table
- **Use when**: showing trend direction in context (table cells, prose)
- **Use when**: exact values aren't needed
- **Avoid when**: the trend itself IS the story (make it bigger)
- D3: `d3-shape` (line), minimal axes

### Step Chart
- Line chart with right-angle steps (no diagonal connections)
- **Use when**: values are discrete/categorical changes (pricing tiers, policy changes)
- **Use when**: value holds until the next change point
- **Avoid when**: continuous smooth change (use line chart)
- D3: `d3-shape` (line with curveStepAfter)

### Candlestick / OHLC
- Shows open, high, low, close for time periods
- **Use when**: financial data with intra-period range
- **Avoid when**: audience isn't familiar with financial charts
- D3: custom rect + line elements

### Calendar Heatmap
- Grid of days colored by intensity (like GitHub contribution graph)
- **Use when**: daily patterns over months/years
- **Use when**: showing seasonality, weekday effects
- **Avoid when**: data isn't daily
- D3: `d3-time`, `d3-scale` (sequential)

---

## Part-to-Whole

Show how individual parts make up a total.

### Stacked Bar Chart
- Bars divided into colored segments
- **Use when**: comparing composition across a few categories (2–7)
- **Use when**: both total and parts matter
- **Avoid when**: more than 5 segments (hard to compare middle segments)
- D3: `d3-shape` (stack), `d3-scale`

### 100% Stacked Bar
- Stacked bars normalized to 100%
- **Use when**: comparing proportions, not absolute values
- **Use when**: totals vary and proportions are the story
- **Avoid when**: absolute values matter
- D3: `d3-shape` (stack, offset expand)

### Pie Chart
- Circular chart divided into slices
- **Use when**: 2–3 segments, one dominant, proportion is the insight
- **Avoid when**: more than 4 segments, comparing across groups, precise comparison needed
- **Note**: Almost always worse than a bar chart. Use sparingly and deliberately.
- D3: `d3-shape` (pie, arc)

### Donut Chart
- Pie chart with a center hole (for label or metric)
- **Use when**: single key metric + its complement (e.g., "73% complete")
- **Avoid when**: multiple categories (same limitations as pie)
- D3: `d3-shape` (arc with innerRadius)

### Treemap
- Nested rectangles sized by value
- **Use when**: hierarchical data with 2+ levels
- **Use when**: showing both parent and child proportions
- **Avoid when**: fewer than 10 items (bar chart is clearer)
- D3: `d3-hierarchy` (treemap), `d3-scale`

### Waffle Chart
- Grid of squares, colored proportionally
- **Use when**: making percentages tangible ("23 out of 100")
- **Use when**: part-to-whole with strong visual metaphor
- **Avoid when**: precise comparison between groups
- D3: grid layout, `d3-scale` (ordinal)

### Parliament / Hemicycle
- Semi-circular arrangement of dots representing seats
- **Use when**: political seat distribution, board composition
- **Avoid when**: data isn't about discrete countable units
- D3: custom polar layout

---

## Magnitude

Show the size of things — absolute comparisons.

### Bar Chart (Horizontal)
- Simple horizontal bars for absolute comparison
- **Use when**: comparing 5–20 items by one measure
- **Use when**: category labels are long (they read naturally)
- **Avoid when**: time is the x-axis (use vertical bars or line)
- D3: `d3-scale` (band, linear)

### Grouped Bar Chart
- Side-by-side bars for multi-variable comparison
- **Use when**: comparing 2–4 measures across categories
- **Avoid when**: more than 4 groups per category (visual clutter)
- D3: `d3-scale` (band with padding), `d3-scale` (ordinal for groups)

### Proportional Symbol
- Symbols (circles) sized by value, positioned spatially
- **Use when**: magnitude varies by location
- **Use when**: showing both position and size
- **Avoid when**: precise comparison needed (area perception is poor)
- D3: `d3-scale` (sqrt for area), `d3-geo`

### Isotype / Pictogram
- Repeated icons representing counted units
- **Use when**: making numbers tangible for general audiences
- **Use when**: the icon metaphor strengthens the story
- **Avoid when**: precise values matter
- D3: repeated SVG symbols

---

## Spatial

Show geographic patterns and location-based data.

### Choropleth
- Map regions colored by data value
- **Use when**: data is tied to geographic boundaries (countries, states)
- **Avoid when**: region sizes vary wildly (large regions dominate visually)
- **Avoid when**: data is better shown per-capita (normalize first)
- D3: `d3-geo`, TopoJSON

### Dot Density Map
- Random dots within regions, each representing N units
- **Use when**: showing population distribution without area bias
- **Use when**: choropleth would mislead due to region size variation
- **Avoid when**: exact location of dots matters (they're randomized)
- D3: `d3-geo`, random point-in-polygon

### Proportional Symbol Map
- Circles or symbols on a map, sized by value
- **Use when**: comparing magnitude across locations
- **Use when**: data is tied to points (cities, facilities)
- **Avoid when**: symbols overlap heavily (use clustering)
- D3: `d3-geo`, `d3-scale` (sqrt)

### Flow Map
- Lines on a map showing movement between locations
- **Use when**: migration, trade routes, shipping, commuting
- **Use when**: origin-destination pairs with magnitude
- **Avoid when**: too many flows (>50 lines become unreadable)
- D3: `d3-geo`, curved path generator

### Cartogram
- Map with region sizes distorted to represent data
- **Use when**: population-weighted maps (each person = equal area)
- **Use when**: showing density-adjusted patterns
- **Avoid when**: geographic accuracy matters
- D3: `d3-geo`, topogram algorithms

### Tile Grid Map
- Each region as an equal-sized tile (square or hex)
- **Use when**: every region should have equal visual weight
- **Use when**: avoiding large-area bias of choropleth
- **Avoid when**: geographic shape/position is part of the story
- D3: custom grid layout

---

## Flow

Show movement, transfers, or connections between nodes.

### Sankey Diagram
- Weighted flows between nodes, showing volume of transfer
- **Use when**: showing how a total splits and recombines (budget, energy, user flow)
- **Use when**: tracking quantities through stages
- **Avoid when**: more than 4 stages (gets complex)
- D3: `d3-sankey`

### Chord Diagram
- Circular layout showing bidirectional flows between entities
- **Use when**: showing mutual relationships (trade between countries)
- **Use when**: both direction and magnitude matter
- **Avoid when**: more than 10 entities (too dense)
- D3: `d3-chord`

### Network Graph (Force-Directed)
- Nodes and edges showing connections
- **Use when**: showing relationship structure, communities, clusters
- **Use when**: topology matters more than exact position
- **Avoid when**: more than 200 nodes without clustering
- D3: `d3-force`

### Arc Diagram
- Nodes on a line with arcs showing connections
- **Use when**: showing connections with a clear ordering (timeline, sequence)
- **Use when**: alternative to network graph for linear data
- **Avoid when**: no natural ordering for nodes
- D3: `d3-shape` (arc), `d3-scale` (point)

### Waterfall Chart
- Sequential bars showing how values add/subtract to reach a total
- **Use when**: explaining how you get from A to B (revenue breakdown, budget changes)
- **Use when**: showing contribution of each factor
- **Avoid when**: more than 10 factors (hard to follow)
- D3: `d3-scale` (band, linear), custom running total
