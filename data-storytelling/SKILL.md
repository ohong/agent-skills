---
name: data-storytelling
description: >-
  Data visualizations, infographics, charts, graphs, maps, scrollytelling,
  NYT-quality graphics, FT-style editorial viz, D3.js, data dashboards,
  data stories, choropleth, scatter plots, line charts, bar charts,
  data-driven storytelling, interactive visualizations, WebGL data viz
metadata:
  filePattern:
    - "**/*chart*"
    - "**/*viz*"
    - "**/*visualization*"
    - "**/*graph*"
    - "**/*map*"
    - "**/*d3*"
    - "**/*scrolly*"
    - "**/*infographic*"
  bashPattern:
    - "d3|visx|observable|scrollama|maplibre|deck\\.gl"
  priority: 50
---

# Data Storytelling Playbook

Build NYT/FT-quality data visualizations: story-first, annotated, responsive, accessible, beautiful.

---

## 1. Design Philosophy

**FT Visual Data principle**: "Don't make charts for chart people. Make stories for all people."

**NYT Graphics principle**: "Is it Timesian?" — typography anchors the brand, not color. The chart should look like it belongs in the publication without a logo.

**Shared principles:**
- **Clarity over cleverness.** If someone has to study the chart to get it, redesign it.
- **Annotation is narrative.** Labels, callouts, and subtitles do more storytelling work than the chart geometry itself.
- **Progressive disclosure.** Start with the simplest possible view. Add complexity only when the reader needs it.
- **Completeness through removal.** A chart is done when there's nothing left to take away — not when there's nothing left to add.
- **One insight per chart.** State the single takeaway in one sentence before writing any code. If you can't, the chart is doing too much.

**Before any code:**
1. Write the insight as a single sentence (this becomes the subtitle)
2. Pick the chart type that most directly shows that insight
3. Identify what data to mute (secondary) vs. emphasize (key)
4. Decide if annotation alone can eliminate the need for a second chart

---

## 2. Story-First Chart Selection

Map the **story type** to the right chart — not the data shape.

| Story Type | Default Chart | Upgrade Option |
|---|---|---|
| **Deviation** (how far from a baseline?) | Diverging bar | Surplus/deficit fill |
| **Correlation** (do X and Y move together?) | Scatter plot | Connected scatter (adds time) |
| **Ranking** (which is biggest/smallest?) | Ordered bar | Slope chart (ranking change) |
| **Distribution** (what does the spread look like?) | Histogram | Violin / beeswarm (density) |
| **Change Over Time** (how has it evolved?) | Line chart | Small multiples (many series) |
| **Part-to-Whole** (what share does each have?) | Stacked bar | Treemap (hierarchical) |
| **Magnitude** (how big is it, absolutely?) | Bar chart | Proportional symbol (spatial) |
| **Spatial** (where is it happening?) | Choropleth | Dot density (avoids area bias) |
| **Flow** (where does it go, from/to?) | Sankey | Chord diagram (bidirectional) |

**The One-Chart Test:** Before adding a second chart, ask: "Can annotation on the first chart convey this?" Direct labels, callout boxes, and reference lines often eliminate the need for companion charts.

See [references/visual-vocabulary.md](references/visual-vocabulary.md) for the full 70+ chart taxonomy.

---

## 3. Technology Selection

### Rendering Decision Tree

```
Data points < 1,000     → SVG (crisp, accessible, inspectable)
1,000 – 50,000          → Canvas (fast 2D, custom hit detection)
50,000+                  → WebGL (GPU-accelerated, deck.gl)
```

### D3.js v7 + React: "D3 for math, React for DOM"

- **Use D3 for**: scales (`d3-scale`), shapes (`d3-shape`), arrays (`d3-array`), geo projections (`d3-geo`), color (`d3-interpolate`), time formatting (`d3-time-format`)
- **Use React/JSX for**: rendering SVG elements, managing state, handling events, responsive layout
- **Never**: let D3 touch the DOM (`d3.select(...).append(...)`) in a React app — React owns the DOM

### Alternative Libraries

| Library | When to Use |
|---|---|
| **visx** (Airbnb) | Reusable chart components, team shared library |
| **Observable Plot** | Rapid prototyping, exploratory analysis |
| **Recharts** | Simple dashboards with standard chart types |
| **Nivo** | Server-side rendering, animation-heavy |

### Maps

| Scenario | Tool |
|---|---|
| Static editorial maps | D3-geo + TopoJSON |
| Interactive pan/zoom | MapLibre GL JS |
| Large-scale point data | deck.gl (WebGL) |
| Tile-based choropleth | MapLibre + custom layers |

### Scrollytelling

- **Scrollama**: intersection-observer-based step detection
- **CSS `position: sticky`**: pins the chart while text scrolls
- **Motion** (framer-motion successor): React-native transitions between steps
- **GSAP ScrollTrigger**: scroll-scrubbed animations for complex sequences

### Animation Rule

Every motion must serve an analytical purpose. Valid: transitions between data states, re-sorting, spatial shifts revealing patterns. Invalid: decorative bounces, gratuitous hover effects, spinning entrances.

### AI Image Generation (fal.ai)

Use for editorial illustrations, backgrounds, and decorative elements — **never for the charts themselves**.
- **Nano Banana 2**: fastest, good for backgrounds/textures
- **FLUX Schnell**: best balance of quality and speed
- **Recraft V4 Pro**: highest quality, editorial illustration style

See [references/technical-patterns.md](references/technical-patterns.md) for implementation code.

---

## 4. Visual Design Rules

### Color

- **Fewer hues, more shades.** The FT approach: one or two hues with luminance variation does more work than a rainbow.
- **Bright color = key data only.** Everything else gets gray, light, or muted.
- **Sequential**: single-hue gradient (light → dark). For continuous values.
- **Diverging**: two hues meeting at a neutral midpoint. For above/below a baseline.
- **Categorical**: max 5–7 distinct hues. Beyond that, use direct labels or small multiples.
- **Cultural sensitivity**: red doesn't mean "bad" everywhere. Blue doesn't mean "cold" in every context. Consider your audience.

### Annotation

- **Direct labels > legends.** Place the label on or next to the data element. Legends force the reader's eye to ping-pong.
- **Subtitle = takeaway.** The chart title names the topic; the subtitle states the insight. Example: Title: "Startup Funding by Year" / Subtitle: "Early-stage rounds dropped 40% in 2023, the steepest decline since the dot-com bust"
- **Mute secondary data.** Lower opacity (0.2–0.4), lighter stroke, thinner lines for context data.
- **Contrast key data.** Bold weight, saturated color, thicker stroke for the data that matters.
- **Reference lines.** Averages, targets, and baselines as dashed lines with labels — they anchor the reader's interpretation.

### Responsive Design

- **Separate aspect ratios.** Desktop: 16:9 or 4:3. Mobile: 9:16 or 1:1. Don't just shrink — redesign.
- **Charts get taller on mobile.** Vertical space is abundant; horizontal space is scarce.
- **Touch targets >= 44px.** Interactive elements (tooltips, toggles, filters) must be finger-friendly.
- **Hide non-essential annotations on small screens.** Keep the title, subtitle, and key callouts. Drop secondary annotations.
- **Nine adaptation techniques** (in order of increasing effort):
  1. **Resize** — scale proportionally
  2. **Reflow** — stack horizontal elements vertically
  3. **Remove** — drop non-essential elements
  4. **Reposition** — move legend below chart
  5. **Redesign** — switch chart type (grouped bar → stacked bar)
  6. **Relayer** — split into tabs or accordion
  7. **Resequence** — change reading order
  8. **Remodel** — change data granularity (daily → monthly)
  9. **Redirect** — link to full experience ("View interactive version")

---

## 5. Storytelling Techniques

### Scrollytelling Structure

1. **Intro**: establish context (what are we looking at?)
2. **Build context**: show the baseline or expected pattern
3. **Reveal insight**: the data point or trend that breaks expectations
4. **Implications**: why this matters, what comes next

**Rule: each scroll step changes ONE thing.** One new data series, one annotation, one zoom level. Never change multiple visual elements simultaneously.

### Progressive Revelation

Start with the simplest view. Add layers as the narrative demands:
1. A single line (the protagonist)
2. A comparison line (the foil)
3. Context bands or reference lines
4. The full complexity (all series, annotations, callouts)

### Narrative Arc

- **Setup**: "Here's what you'd expect..." (show the baseline or conventional wisdom)
- **Tension**: "But look at this..." (reveal the anomaly, the trend break, the outlier)
- **Resolution**: "This matters because..." (connect to the reader's world)

### Animation: Valid vs. Invalid

**Valid analytical motion:**
- Tweening between data states (bar heights growing to new values)
- Re-sorting elements (ranking changes over time)
- Spatial shifts revealing geographic patterns
- Motion-as-data (speed = rate of change)
- Trend reveal (line drawing left-to-right to build suspense)

**Invalid decorative motion:**
- Bouncing entrance animations
- Gratuitous hover scaling
- Spinning chart transitions
- Particles or confetti on data points
- Any motion that doesn't encode information

---

## 6. Accessibility

### WCAG Compliance

- **`aria-label`**: write the actual insight, not "chart showing data." Example: `aria-label="Line chart showing startup funding dropped 40% in 2023"`
- **Contrast**: 4.5:1 minimum for text, 3:1 for graphical elements against background
- **Color is not the sole differentiator.** Every color distinction must also have a shape, pattern, or label distinction.

### Colorblind Safety

- Add texture/pattern fills alongside color for filled areas
- Test with deuteranopia simulation (most common: ~8% of males)
- Safe combinations: blue+orange, blue+red, purple+green (with pattern backup)
- Use tools: Viz Palette, Coblis, or browser DevTools color vision simulation

### Screen Readers

- Hidden data table with `sr-only` class for all chart data
- `role="img"` on the SVG container
- `<title>` and `<desc>` elements inside SVG with descriptive text
- `aria-describedby` linking to a text summary of the insight

### Motion

- Wrap all animations in `prefers-reduced-motion` media query
- Provide a visible "reduce motion" toggle
- When motion is reduced, show the final state immediately (no transition)
- `prefers-reduced-motion: reduce` → set all `transition-duration: 0.01ms`

### Keyboard Navigation

- `tabindex="0"` on interactive elements (data points, filters, toggles)
- Arrow key navigation between data points
- Visible focus indicators (outline, not just color change)
- `aria-activedescendant` for managing focus within chart groups

---

## 7. Quality Checklist

Before shipping any data visualization, verify:

### Story
- [ ] Single insight stated as subtitle?
- [ ] Anything that can be removed without losing the insight?
- [ ] Title conveys the takeaway, not just the topic?

### Design
- [ ] Annotation guides the reader to the insight?
- [ ] Direct labels used instead of legends where possible?
- [ ] Secondary data muted (low opacity, thin stroke)?
- [ ] Fewer than 5 categorical hues?
- [ ] Reference lines/baselines for context?

### Responsive
- [ ] Readable at 375px width?
- [ ] Touch targets >= 44px?
- [ ] Mobile uses taller aspect ratio?
- [ ] Non-essential annotations hidden on small screens?

### Accessibility
- [ ] Works without color alone (patterns, labels)?
- [ ] Text contrast >= 4.5:1, graphical >= 3:1?
- [ ] Text alternative states the insight (not "chart")?
- [ ] `prefers-reduced-motion` respected?
- [ ] Hidden data table for screen readers?

### Performance
- [ ] SVG element count < 1,000?
- [ ] TopoJSON (not GeoJSON) for maps?
- [ ] Charts below the fold lazy-loaded?
- [ ] Large datasets use Canvas or WebGL?
- [ ] Fonts subset to characters used?
