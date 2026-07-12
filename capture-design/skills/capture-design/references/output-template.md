# Design System Document — Section Menu

Structure for `{kebab-case-name}-design-system.md`. **Every section below is a suggestion, not a requirement.** Let the references dictate the table of contents: a web app capture uses the interface sections; architecture photos use siting/massing/materials and skip interactive states, motion, and shadow-elevation entirely; a print or poster capture might center on typography and composition. Invent sections the input demands that this menu never anticipated.

Always include: Essence, Core Visual Identity, Ideal Uses, Influences, and Implementation Notes. Everything else is conditional on the material.

Target: a couple of pages (~1,000–2,000 words). Write in the register of a classic design manual — every guideline flows from the stated philosophy, so a reader can extrapolate to cases the doc doesn't cover.

```markdown
# {Design Name}

## Essence
2–4 sentences. The feel, personality, and philosophy. What emotional
response does it evoke? What era or worldview does it belong to?
Everything below should read as a consequence of this paragraph.

## Core Visual Identity
The 3–5 defining decisions. If someone could only apply this many moves,
which ones make the design recognizable?

## Ideal Uses
What kinds of projects this design suits (and, briefly, where it would
fight the content).

## Color Palette
Group by role, hex codes where verifiable; note overall saturation and
temperature character. Include usage guidance, not just swatches —
which color does what work, and when.

## Typography
Families (headings / body / mono), weights, scale (size, weight,
line-height, usage per level), treatments (case, tracking, numerals),
and the hierarchy logic — how the design tells you what matters.

## Spacing & Layout
Base unit or rhythm, container behavior, grid logic, density character
and why.

## Iconography & Illustration *(if present)*
Stroke vs. fill, weight, corner treatment, level of abstraction,
metaphor style, how imagery relates to type.

## UI Patterns *(interfaces)*
The recurring compositions: navigation, cards, forms, tables, empty
states, dialogs. For each pattern that defines the design: what it
looks like, when to use it, notable states (default / hover / focus /
disabled / error), and accessibility characteristics worth preserving
(contrast ratios, target sizes, focus visibility).

## Interactive States & Motion *(interfaces)*
Philosophy first (snappy? viscous? mechanical?), then patterns with
timing and easing where verifiable.

## Elevation & Depth *(if the design uses it)*
Shadows, borders, radii, layering — or the deliberate absence of depth.

## Materials & Physical Interface *(hardware, industrial, retro-computing)*
Materials, finishes, form factors, controls, wear, how light interacts
with surfaces.

## Siting, Massing & Landscape *(architecture, environments)*
Relationship to site and horizon, roof forms, volumes, openings,
exterior materials and their weathering, the boundary between built
and natural.

## Lighting & Atmosphere *(photographic/environmental)*
Light sources and quality, shadows, depth of field, grain.

## Influences & Cultural Coordinates
Adjacent aesthetics, movements, eras. What the design rejects.
What it claims.

## Implementation Notes
Concrete guidance for recreation in the target medium: CSS variable
structure and font stacks for software; materials and finishes for
hardware; rendering effects (grain %, vignette, bloom); how to extend
the palette or patterns to states the references don't show.

## References
List of files in references/ with one line each on what it shows.
```

## Bear note

An exact copy of the document above, with the title changed to `Design inspo: {Name}`, the line `#startup/design #swipefiles` inserted directly after the title, and reference images embedded at the end under `## Reference images`.
