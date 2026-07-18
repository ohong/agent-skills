---
name: skill-authoring
description: Load whenever creating or editing a SKILL.md, slash command, or agent definition. Principles for keeping skills thin, deterministic, and progressively disclosed.
---

# Skill authoring

Guiding principle: **thin prompts, thick artifacts + context, thin skills.** A skill is a router to the right context and scripts, not an essay. Most SKILL.mds are too bulky and unwieldy — bulk gets loaded on every invocation and crowds out task context.

- **Prefer deterministic scripts over prose instructions.** If a step can be a script the model runs (`scripts/check.sh`, a bun/uv one-liner), write the script and have the skill call it. Scripts don't drift, don't get misread, and cost no reasoning.
- **Progressive disclosure.** SKILL.md holds only the workflow and decision points (~50 lines is a good ceiling). Push reference material, templates, and edge-case docs into `references/*.md` files that the skill points at, loaded only when needed.
- **The description is the trigger.** Spend effort on the frontmatter `description`: when to load it, when NOT to. A skill that fires at the wrong time is worse than no skill.
- **One skill, one job.** If a SKILL.md has two unrelated workflows, split it.
- **No duplication with CLAUDE.md or the harness.** A skill restating always-on instructions wastes both budgets; link or omit.

Litmus test before shipping: could you delete half the lines and still get the same behavior? If yes, delete them.
