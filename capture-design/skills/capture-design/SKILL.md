---
name: capture-design
description: Save reference visuals as a reusable design-system swipefile. Use when the user explicitly asks to capture or preserve an aesthetic for reuse.
---

# Capture Design

Turn reference assets containing a "target design" into a permanent, importable swipefile entry: a named design system, a full description document, and the saved references. The output must be complete enough that a design engineer or coding agent who has never seen the references can convincingly recreate or apply the aesthetic to a new website, app, or piece of hardware.

## Inputs

The user provides one or more of:

- **Images / screenshots** — analyze qualitatively. Only state precise values (hex codes, px) you can actually sample or confidently infer; otherwise describe qualitatively ("warm gray plastic, roughly #9B968C–#A8A298").
- **Live URLs** — you have browser and computer-use tools; use them fully. Open the link, traverse the landing page plus 3–5 primary pages/flows, click around the site or app, hover elements, open modals and forms, and take screenshots as you go (these become references). Where DevTools/computed styles are accessible, extract exact colors, font stacks, sizes, spacing, shadows, and transition timings. Interactive states define much of a system's character — do whatever it takes to deeply study the reference, not just read the first page.
- **Other media** (video stills, PDFs, physical product photos, architecture) — extract what's visible; note the medium.

Use available image-analysis tools to sample colors when practical. Do not add a dependency solely for this workflow without the user's approval.

## Workflow

1. **Save the references.** Copy every provided asset into `references/` at the project root, naming files descriptively (`landing-hero.png`, `detail-typography.png`). Do this first, and verify the files actually exist on disk before moving on — this step fails silently in some environments:
   - Images pasted into chat are often visible to you but never materialized as files (the uploads folder is empty). Check the uploads folder; if the assets aren't there, tell the user immediately and ask them to re-attach as files or connect a folder, then continue with the available material rather than blocking.
   - Browser screenshots may not be persistable to disk in your session. Try the save option once; if unavailable, fall back to downloading the page's own image assets, or note the gap.
   - If some assets truly cannot be saved, write a `references/{name}-sources.md` manifest listing each missing asset with a description and source URL, so the user (or a future agent) can complete the folder manually. Never skip the references step without leaving this manifest and telling the user.

2. **Study the material.** Identify what makes this design *this design* — the three or four decisions that, if removed, would collapse the aesthetic. Look past surface styling to the worldview: what does this design believe about its user, its era, its purpose?

3. **Name the design.** Give it a memorable, evocative name that captures the essence without referencing any trademarked product or company (e.g. "Digital Atheneum", "Tempelhof Air Traffic Control", "Arctic Dawn"). Non-commercial proper nouns — places, movements, historical references — are encouraged.

4. **Write the design system document** to `{kebab-case-name}-design-system.md` at the project root. `references/output-template.md` (read it before writing) lists candidate sections — treat them as suggestions, not must-haves. What belongs in the doc is dictated entirely by what the references contain. A web app needs interactive states, UI patterns, and motion; architecture photos need siting, massing, and materials instead — and would skip elevation-as-shadows, interactive states, and motion entirely. Invent sections the input demands that the template never anticipated.

5. **Create the Bear note** (if a Bear connector is available — otherwise skip silently and mention the skip in your summary). The note is simply a copy of the design system .md, titled `Design inspo: {Name}`, with `#startup/design #swipefiles` on the line after the title for retrieval. The Bear API cannot attach images; end the note with a `## Reference images` section describing each reference and where it lives, so the user can drag images in manually.

6. **Summarize** for the user: the name, the one-paragraph essence, and where everything was saved.

## The trademark rule

Reference assets often come from real products. The *output* (doc, Bear note, design name) must never mention trademarked product or company names. Write "the workstation", "the application", "the site" instead. This keeps the swipefile clean for reuse in commercial projects. The saved reference files themselves are exempt — they are what they are.

## Quality bar

The exemplar for the *writing* is the Sea Ranch Lodge Design Manual: prose where every guideline flows from a stated philosophy of place, so a reader absorbs the worldview and can extrapolate correctly to situations the manual never covers. Aim for that register, compressed to a couple of pages — the key pillars of the design, sufficient for later recreation and application.

Good design system documentation (per current practice) covers typography, color, spacing, iconography, and UI patterns with clear usage guidance — not just what the elements are, but when and how to use them, including states and accessibility characteristics where the medium has them. Apply this expectation proportionally to what the references actually show.

The difference between a useful capture and a mood-board caption is specificity plus interpretation:

- **Specific**: real hex codes, font weights, border radii, timing curves, material finishes — when verifiable. Qualitative but vivid language when not ("blacks aren't true black; they're dark gray with phosphor warmth").
- **Interpretive**: name the influences and cultural coordinates. State what the design *rejects* as well as what it claims. A design system is a worldview with hex codes.
- **Actionable**: usage guidance and implementation notes a coding agent can follow directly — when to reach for each element, CSS variable structure, rendering effects (grain, vignette, bloom), animation timing, what to do at the edges the references don't show.

Write for the audience: an agent or design engineer importing this into a project six months from now with zero other context. Plain, precise language; every value and guideline earns its place by helping them recreate the design.
