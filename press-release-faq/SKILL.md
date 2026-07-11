---
name: press-release-faq
description: >
  Write an Amazon-style Working Backwards PR/FAQ for a product that hasn't been built
  yet, grounded in the codebase the skill is invoked in. Produces a press release
  (max 500 words) and FAQ (max 500 words) written as if the product already launched.
  Use for: (1) Pressure-testing a product or feature idea before building it,
  (2) Turning specs/PRDs/READMEs into a customer-focused launch narrative,
  (3) Forcing clarity on customer, problem, and differentiation. Scope defaults to
  the whole product in the repo; the user may narrow it to a specific feature.
---

# Press Release / FAQ (Working Backwards)

Write the press release and FAQ *before* the product exists — Amazon's Working Backwards method (Bryar & Carr). The PR/FAQ is a truth-seeking document, not a sales pitch. Its job is to force clarity on who the customer is, what problem is being solved, and why this solution is meaningfully better than what exists today. Most PR/FAQs should reveal weaknesses; that is the point.

Run fully autonomously. Make every judgment call yourself (customer segment, launch date, pricing, differentiation). Do not ask the user questions.

## Scope

- **Default:** the entire product/project described by the repo.
- **If the user names a feature or change:** write the PR/FAQ for that feature only, treating the existing product as the status quo customers use today.

## Step 1 — Gather context from the codebase

Read the written documentation first; it carries the intent. Priority order:

1. `README.md` (root, then subdirectories)
2. Specs, PRDs, design docs, RFCs — search for `*.md` in `docs/`, `specs/`, `design/`, `rfcs/`, and the repo root (e.g. `SPEC.md`, `PRD.md`, `VISION.md`, `ROADMAP.md`, `CLAUDE.md`)
3. `package.json` / `pyproject.toml` / `Cargo.toml` etc. — name, description, dependencies (reveals capabilities)
4. Top-level code structure — routes, commands, models, UI pages — to infer what the product actually does and doesn't do

Extract: what the product is, who it seems to be for, what problem it addresses, what exists today vs. what is planned, and any stated positioning or pricing. Where docs are silent, infer from code; where code is silent, make a reasonable decision and commit to it.

## Step 2 — Work backwards from the customer

Before writing, answer these for yourself (they shape every sentence):

- **Who exactly is the customer?** A specific segment, never "everyone." If the docs say "developers," decide *which* developers.
- **What is their most important problem?** From the customer's point of view, not the builder's. Not all problems are equal — pick the one with the largest willingness to pay.
- **What do they use today?** There is always a current solution. Name it.
- **On which dimension is this better, cheaper, or faster?** If the answer is "none," the PR/FAQ should say so honestly in the FAQ — do not paper over a copycat.
- **What behavior change are we asking for?** Customers must switch from something.

Customer backwards, not skills forward: describe the product customers need, even where it exceeds what the current codebase can do. The gap between the PR and today's code is the roadmap, not a reason to shrink the vision.

## Step 3 — Write the press release (≤ 500 words)

Written as if launch day has arrived. Plain language a customer would use — no corporate jargon, no internal terminology from the codebase. Structure:

1. **Heading** — product name plus one sentence any target customer instantly understands.
2. **Subheading** — one sentence: who the customer is and the benefit they get. Be precise about the segment.
3. **Summary paragraph** — city, outlet, plausible launch date (pick a real future date, roughly sized to the remaining build effort), then a crisp summary of the product and its benefits.
4. **Problem paragraph** — the customer's problem, in their words and from their point of view.
5. **Solution paragraph(s)** — how the product simply and directly solves that problem. Must include the competitive sentence pattern: "Today, customers with this problem use X or Y. Those fall short because Z. [Product] addresses this by…" Specific and brief; no laundry lists of features.
6. **Quotes** — one from a company spokesperson (invent a plausible name/title), one from a hypothetical customer describing the benefit in concrete terms.
7. **Getting started** — how easy it is to begin, with a call to action.

Quality bar: a reader should finish the PR excited to use the product. If the PR describes something no better/faster/cheaper than existing options, that's a "Phoenix 400" — rework the positioning or surface the problem loudly in the FAQ rather than shipping a bland PR.

## Step 4 — Write the FAQ (≤ 500 words)

The PR names the destination; the FAQ is the map and the dragons. Two sections, ruthlessly prioritized to fit the word budget:

**External FAQs** (customer/press voice, pick 2–4):
- What does it cost? How does it work? How do I get started? What platforms/integrations are supported?

**Internal FAQs** (truth-seeking, pick 4–6 — these matter most):
- What do target customers use today, and why would they switch?
- How is this better, cheaper, or faster than the alternatives?
- How large is the TAM / how many customers have this problem badly enough to pay?
- What are the hardest problems (technical, legal, operational, business-model) we must solve to build this?
- What must be true for this product to succeed?
- What are the top three reasons this will fail?

Answers must be optimistic but realistic — grounded in what the codebase and docs actually support, honest about risks and unknowns. Never sell. If the TAM looks small or the differentiation thin, say so plainly; a PR/FAQ that kills a bad idea has done its job.

## Step 5 — Output

- Write a single file `PRFAQ.md` at the repo root (use `docs/PRFAQ.md` if a `docs/` directory exists). If scoped to a feature, name it `PRFAQ-<feature-slug>.md`.
- File structure: `# Press Release` section, then `# FAQ` section (with `## External` and `## Internal` subsections).
- Verify both word counts before finishing (PR ≤ 500, FAQ ≤ 500, excluding headings). Trim until compliant.
- End your response with a 2–3 sentence honest assessment: the strongest claim in the PR, and the biggest risk the FAQ surfaced.

## Rules

- **Customer's point of view, always.** Every problem and benefit is framed as the customer experiences it.
- **One specific customer segment.** "Everyone" is a failure.
- **Name the competition.** There is always a current solution; state why customers would switch.
- **Truth-seeking, not selling.** Include the uncomfortable questions and answer them honestly.
- **No jargon.** If a customer wouldn't say it, don't write it.
- **Grounded but not constrained.** Root claims in the repo's docs and code; let the vision exceed current implementation, never contradict it.
- **Hard word limits.** 500 words each for PR and FAQ. Count, then trim.
- **Autonomous.** Decide everything; ask nothing.
