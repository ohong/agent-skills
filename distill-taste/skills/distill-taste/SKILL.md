---
name: distill-taste
description: Deep-research a named person's (or group of people's) public writing, interviews, and talks, then distill their taste into a standalone installable ask-person advisor skill. Use for "/distill-taste name", "make a skill from a person's taste", "I want feedback from a person's perspective", or refreshing an existing ask-* persona. Not for applying an already-installed ask-* skill, and not for private individuals with no public footprint.
---

# Distill Taste

Turn a person's public body of work into an installable **ask-<person>** skill: a full-roleplay advisor (think Delphi.ai) the user can chat with or hand work to for feedback grounded in that person's actual taste — worldview, quality bar, problem selection, pet peeves, style. Taste has no objectively correct answer; the whole value is fidelity to *this* person's particular judgment.

## Parse the request

- `<name>` — whole-person distillation.
- `<name> on <topic>` — still distill the whole person, but weight research and the profile heavily toward that domain.
- `<name> + <name> [+ ...]` — a **panel**: one skill, each person keeping a distinct voice; disagreement between them is signal, never smoothed over.
- Rerunning an existing persona refreshes it in place (re-research, rewrite profiles, bump version, re-zip).

If the name is ambiguous (multiple public figures), resolve from context; ask only if genuinely unresolvable.

## Research (deep, canonical-first)

Follow `references/research-playbook.md`. In short: identify the person, then hunt their **meta-writing first** — advice essays, "how I work/write/decide" pieces, interviews, podcast transcripts, talks, AMAs — before their general output. Read the top ~10–20 primary sources properly (fetch and read, don't skim search snippets). Capture short verbatim quotes with source URLs as you go; these become the persona's citable spine.

Run autonomously — no mid-run checkpoint. **Exception — thin data:** if you can't find enough substantive primary material for the persona to be more than guesswork, stop, present what you found, and ask whether to proceed with heavy extrapolation, narrow to their one strong domain, or abort.

## Build the persona skill

Generate a standalone plugin at the repo root named `ask-<kebab-name>` (panels: `ask-<name1>-<name2>`), following `references/persona-skill-template.md` exactly. Structure mirrors this repo's conventions:

```
ask-<person>/
  .claude-plugin/plugin.json
  skills/ask-<person>/
    SKILL.md                      # thin: behavior contract + routing to references
    agents/openai.yaml
    references/
      taste-profile.md            # the distilled taste (per person, for panels)
      voice.md                    # how they sound, argue, structure, joke
      sources.md                  # annotated bibliography with quotes + URLs
  ask-<person>.skill              # zip of skills/ask-<person>/ contents
```

Behavior contract baked into every generated skill: full first-person roleplay; extrapolates freely from the worldview onto novel topics without breaking character or hedging; feedback arrives as a prioritized critique (the few things this person would actually care about, each tied to a principle, with a concrete fix) plus the Socratic questions they'd ask; cites their real writing mid-conversation ("as I wrote in …") using the short quotes in `sources.md`.

Do **not** add generated personas to the repo's README or `.claude-plugin/marketplace.json` — those curate the public marketplace. Mention this so the user can promote a persona manually if they want.

## Deliver

Zip the skill directory as `ask-<person>.skill` (zip the contents of `skills/ask-<person>/` under a top-level `ask-<person>/` folder, matching the other `.skill` files in this repo), present it for one-click install, and summarize in a few sentences: who the persona is, the 3–4 taste pillars that define them, and the strongest sources it stands on.
