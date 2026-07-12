# Public Skill Portfolio Audit

> Snapshot note: this report records the original pruning analysis. The final portfolio decision retained `mission`, `audit-and-improve`, and public `post-walk`, while moving project-specific skills out and packaging every shareable skill in the Claude Code marketplace. See `README.md` for the current set.

**Date:** 2026-07-11  
**Target:** GPT-5.6 Sol at any reasoning effort, running in current Codex surfaces  
**Scope:** The public/shared skills in `/Users/ohong/dev/agent-skills`

## Executive Summary

**Grade: C.** The repository contains useful deterministic tooling, but the public portfolio is now substantially larger and more eager than GPT-5.6 Sol needs. Eight capabilities are safe deprecation candidates because they are prompt-only scaffolds for planning, auditing, reviewing, explaining, specification writing, or security reasoning that Codex now performs natively. Two more capabilities are useful but should not be public: `post-walk` contains personal paths and behavior, while `xray` is a Startups.RIP project command with a hard-coded Supabase project and repository templates. Keep the workflows that add external retrieval, scripts, platform-specific measurements, durable artifact contracts, or substantial reference material. Merge the three URL-to-Markdown skills into one routed skill, leaving a target public portfolio of six skills instead of eighteen capabilities. Make `data-storytelling` and `name-it` explicit-invocation only; if a small A/B evaluation cannot show material lift over unskilled Sol, remove them too. The current descriptions are the main context and routing problem: several use “whenever,” “proactively,” keyword soup, or broad file patterns that make routine work look skill-worthy. No existing eval records compare skilled output against an unskilled GPT-5.6 Sol baseline, so the deprecation recommendations are high-confidence architectural judgments, not measured quality guarantees.

## Repo Map

This is a Claude Code marketplace plus a set of unbundled cross-agent skills. The root marketplace exposes two plugins, `audit-and-improve` and `mission` (`.claude-plugin/marketplace.json:9-34`); the README lists those plus thirteen standalone skills (`README.md:16-39`). Three newer top-level skills, `capture-design`, `post-walk`, and `press-release-faq`, are not indexed in the README.

The repository currently contains:

- 18 top-level capability folders.
- 23 `SKILL.md` files, because `mission` contributes six commands.
- 3,082 lines of injected skill instructions.
- Five bundled helper scripts: article archival, Wi-Fi measurement, voice transcription, YouTube transcription, and X packaging.
- Six Codex `agents/openai.yaml` interface files.
- Eleven packaged `.skill` archives. All archives passed `unzip -t` during this audit.
- Two assertion files called evals, but neither contains recorded runs or an unskilled baseline (`data-storytelling/evals.json:1-71`, `vibe-security-audit/evals.json:1-47`).

The capability split matters more than the folder count:

1. **Deterministic/tool-backed workflows:** archival, transcription, Wi-Fi diagnostics.
2. **Durable artifact workflows:** design capture and fuzzy X retrieval.
3. **Reference-backed judgment workflows:** editorial visualization and naming.
4. **Generic reasoning/orchestration prompts:** audit, delegation, explanation, mission planning, PR/FAQ, spec writing, security review, and cleanup advice.
5. **Private/project commands:** post-walk and xray.

## Audit Report

### Native capability baseline

The current Codex manual describes GPT-5.6 as the starting point for demanding agents and Sol as the choice for complex, open-ended work requiring analysis, judgment, or polish. It also documents native Plan mode, persistent goals with automatic continuation, review mode, stable multi-agent tools, and agent-driven testing and review. Most importantly for this audit, the manual says most tasks do not need Max or Ultra, and that skill or project instructions can themselves trigger subagents, which consume more tokens than single-agent runs. See the current [Codex manual](https://developers.openai.com/codex/codex-manual.md) and [Codex use cases](https://developers.openai.com/codex/use-cases).

This creates a simple retention test:

> Keep a skill only if it supplies a tool, external access path, deterministic script, durable cross-session artifact contract, project-specific protocol, or reference corpus that materially changes the result. Generic advice to inspect, reason, plan, verify, explain, or write a familiar document is no longer enough.

### Recommended disposition

| Current capability | Disposition | Confidence | Evidence and rationale |
|---|---|---:|---|
| `audit-and-improve` | **Deprecate** | High | It is a 248-line prompt-only repo-audit template. Its 884-character description claims every audit, review, assessment, improvement, refactor plan, and modernization plan (`audit-and-improve/skills/audit-and-improve/SKILL.md:3-14`). Sol natively performs codebase analysis, planning, validation, and review. The fixed report contract can be requested in one prompt when needed. |
| `delegate` | **Deprecate immediately** | Very high | It always routes substantial work through Claude → GPT-5.5 → Opus 4.8 (`delegate/SKILL.md:3-8`) and explicitly spawns a fresh evaluator up to three times (`delegate/SKILL.md:85-96`). The model pins are stale, the companion path is surface-specific, and the whole loop duplicates native planning, implementation, review, and optional subagents. |
| `explain` | **Deprecate** | High | No script, external system, or reference corpus. It expands a normal “explain this diff” request into 133 lines and even requires 3–5 quiz questions (`explain/SKILL.md:79-82`). Sol can inspect and explain a change directly; the user can ask for a teaching-oriented walkthrough when desired. |
| `mission` | **Deprecate for Codex 5.6** | High | Native `/plan`, `/goal`, `/review`, persisted goals, and automatic continuation overlap its core function. It also forces subagents for exploration (`mission/skills/plan/SKILL.md:42-50`; `mission/skills/start/SKILL.md:70-74`) and writes commits without per-task authorization (`mission/skills/start/SKILL.md:45-48`, `mission/references/execution-protocol.md:38-45`). Keep only if supporting older/non-Codex clients is an explicit product goal. |
| `press-release-faq` | **Deprecate** | High | This is a familiar document format plus word limits and a file path. It has no unique tool or reference asset. The 554-character description and autonomous “ask nothing” behavior (`press-release-faq/SKILL.md:3-17`) add routing and judgment risk without adding capability. |
| `spec-writer` | **Deprecate immediately** | Very high | A 306-line prompt-only template that assumes one-pass implementation, prohibits questions and alternatives, and hard-codes stale stack defaults (`spec-writer/SKILL.md:8-32`, `spec-writer/SKILL.md:36-50`, `spec-writer/SKILL.md:295-306`). Sol can write a grounded spec natively and should not invent certainty merely to satisfy the template. |
| `spring-cleaning` | **Deprecate immediately** | Very high | No helper script, only a 314-line recipe book containing broad destructive commands such as clearing Trash, Messages attachments, Docker data, and all Codex worktrees (`spring-cleaning/SKILL.md:143-175`, `spring-cleaning/SKILL.md:184-240`). Native state-aware diagnosis is safer than injecting stale deletion recipes. |
| `vibe-security-audit` | **Deprecate as a standalone skill** | High | Codex already supports deep security scans and remediation. This skill auto-activates during nearly any BaaS/database/auth/env/deployment work and tells the agent to fix issues even when no audit was requested (`vibe-security-audit/SKILL.md:26-39`). Its narrow Supabase checks can live in project guidance or an explicit security prompt; they should not hijack ordinary implementation. |
| `post-walk` | **Move to private skills; remove agent launching by default** | Very high | The workflow is useful and script-backed, but it names Oscar, searches a personal Voice Memos path, reads a personal env-file path, files Things todos, and launches background agents (`post-walk/SKILL.md:3-18`, `post-walk/SKILL.md:20-28`, `post-walk/SKILL.md:66-86`). That is personal automation, not a public skill. |
| `xray` | **Move into `startups-rip`; remove forced team** | Very high | It hard-codes a Supabase project, database totals, repo template paths, and a three-agent workflow (`xray/SKILL.md:24-29`, `xray/SKILL.md:33-66`, `xray/SKILL.md:104-122`). It is a project command. Keep the capability beside the project data and let a single agent run it unless the user explicitly requests parallelism. |
| `archive-article-to-markdown` | **Merge and keep** | Very high | Adds a real archive.ph retrieval/extraction script, saved diagnostics, and a concrete output contract (`archive-article-to-markdown/SKILL.md:10-58`). |
| `transcribe-yt` | **Merge and keep** | Very high | Adds a real usetranscribe.io integration and local Markdown output, capability the model does not have from reasoning alone (`transcribe-yt/SKILL.md:10-47`). |
| `x-article-to-markdown` | **Merge and keep** | Very high | Adds deterministic packaging of X text and local media with a helper script and source manifest (`x-article-to-markdown/SKILL.md:36-82`). |
| `capture-design` | **Keep, slim, explicit trigger** | Medium-high | The model can analyze visuals natively, but the saved-reference + reusable swipefile artifact is a distinct durable workflow (`capture-design/SKILL.md:28-43`). Remove the broad “whenever visual material is shared” trigger and the inline `pip install --break-system-packages` instruction (`capture-design/SKILL.md:3`, `capture-design/SKILL.md:18-26`). |
| `fast-wifi` | **Keep** | Very high | The bundled snapshot script and macOS-specific first-hop measurements add real capability and reproducibility. This is not merely “reason harder.” |
| `search-x` | **Keep, slim** | High | Logged-in X surfaces, query ladders, and live-post verification address a real retrieval failure mode (`search-x/SKILL.md:23-31`, `search-x/SKILL.md:63-111`). Keep the verification contract; move examples into references. |
| `data-storytelling` | **Probationary keep; explicit invocation only** | Medium | Its editorial chart vocabulary and technical references may add quality, but the 281-line main file includes stale library/model advice and its keyword/file-pattern metadata can trigger on routine charts (`data-storytelling/SKILL.md:3-20`, `data-storytelling/SKILL.md:72-124`). Retain only the editorial principles and accessibility/verification checklist, then A/B test against unskilled Sol. |
| `name-it` | **Probationary keep; explicit invocation only** | Medium | The reference corpus and staged validation method may improve high-stakes brand naming, but Sol natively generates and evaluates names. The current “whenever the user needs to name anything,” including libraries and features, is far too broad (`name-it/SKILL.md:1-4`). Keep only for explicit structured naming engagements and A/B test it. |

### Target public portfolio

The recommended public surface is six skills:

1. `archive-to-markdown` (merge article archival, X archival, and YouTube transcription behind URL routing)
2. `capture-design`
3. `data-storytelling` (probationary, explicit only)
4. `fast-wifi`
5. `name-it` (probationary, explicit only)
6. `search-x`

`post-walk` remains a private personal skill. `xray` becomes a project-local Startups.RIP skill. If the two probationary skills fail A/B evaluation, the stable public portfolio becomes four.

The archive merge should use progressive disclosure: a short `SKILL.md` routes by URL type, while source-specific procedures live in references and the existing helper scripts remain separate. That reduces discovery metadata without injecting X and YouTube details into an ordinary article run.

### Description audit

The trigger descriptions are currently too long. The median is roughly 400 characters; `audit-and-improve` reaches 884 characters. Descriptions should answer only two questions: what unique capability is added, and when it should load. Procedures, examples, quality bars, exclusions, model names, and marketing language belong in the body or references.

Use these descriptions for the retained public set:

| Skill | Proposed description |
|---|---|
| `archive-to-markdown` | `Save a web article, X post/thread, or YouTube transcript as local Markdown using the bundled source-specific tools. Use when the user explicitly asks to archive one of those URLs.` |
| `capture-design` | `Save reference visuals as a reusable design-system swipefile. Use when the user explicitly asks to capture or preserve an aesthetic for reuse.` |
| `data-storytelling` | `Create editorial data stories and custom narrative visualizations. Use only for explicitly requested publication-quality charts or scrollytelling, not routine charts or dashboards.` |
| `fast-wifi` | `Diagnose a slow macOS network with the bundled measurement script. Use when the user asks to troubleshoot current Wi-Fi or internet performance.` |
| `name-it` | `Run a structured brand or product naming and validation process. Use for explicit naming strategy or candidate evaluation, not ordinary code identifiers.` |
| `search-x` | `Find a specific remembered X post from fuzzy clues and verify it on the live post. Use when exact wording or the author is unknown.` |

Use these descriptions for retained non-public workflows:

| Skill | Proposed description |
|---|---|
| private `post-walk` | `Process a local Apple Voice Memo into an archived transcript, project notes, tasks, todos, and drafts. Launch agents only when the user explicitly asks.` |
| project-local `xray` | `Build a Startups.RIP YC-vertical report from the project database and existing templates. Use only inside startups-rip when explicitly invoked.` |

Description rules for this repository:

- Prefer one or two sentences, usually under 220 characters.
- Say **“use when the user explicitly asks”** for expensive or niche workflows.
- Do not say “whenever,” “always,” “proactively,” or “even if the user did not ask” in discovery metadata.
- Do not list every synonym or file type. Two representative terms are enough for semantic routing.
- Do not mention model names, agent roles, implementation steps, output sections, or marketing quality claims in descriptions.
- Do not use `filePattern` or `bashPattern` auto-routing for a large niche skill unless false-trigger evals prove it is safe.
- A skill must never trigger subagents implicitly. Require explicit user intent for parallel work.

### Other high-confidence findings

#### High: Public/private boundary is broken

`post-walk` exposes a personal name, filesystem layout, API-key lookup path, and task-launching conventions. `xray` exposes a project identifier and Startups.RIP implementation details. This contradicts the repository’s public/shared purpose and makes both workflows brittle elsewhere.

#### High: Several skills override user authority

`vibe-security-audit` authorizes fixes without an explicit request (`vibe-security-audit/SKILL.md:26-39`). `mission` authorizes commits per milestone (`mission/skills/start/SKILL.md:45-48`). `spring-cleaning` supplies irreversible deletion commands after one warning. Skills should constrain an agent, not silently broaden its permission to mutate code, history, accounts, or user data.

#### Medium: Main skill files contain volatile facts

`delegate` pins GPT-5.5 and Opus 4.8. `spec-writer` pins Next.js 15 and other stack defaults. `data-storytelling` recommends specific image models and libraries. `xray` embeds company counts and rates. Volatile facts create maintenance debt and degrade output once stale. Where live facts are necessary, direct the agent to verify official sources or project state; do not cache the answer in the skill.

#### Medium: There is no evidence that prompt-only skills beat unskilled Sol

The two eval files contain prompts and expected assertions, not executed results, scores, cost, false-trigger rate, or a no-skill control. None of the eight prompt-only deprecation candidates has an eval at all. Without comparative evidence, keeping thousands of tokens of generic instructions is portfolio inertia.

#### Low: Public index and packaging are inconsistent

The README omits three top-level skills, only six skills have Codex interface metadata, and only eleven have packaged archives. This is manageable after pruning, but it makes the current definition of “public” ambiguous.

### Strengths

- The best skills wrap real scripts and produce inspectable local artifacts.
- Archive `.skill` files are structurally valid.
- The X retrieval and archival workflows explicitly require verification instead of trusting a plausible match.
- `fast-wifi` encodes a measured before/after diagnostic flow rather than generic networking advice.
- The repository is cleanly licensed and has a readable marketplace structure.

Security, performance, and dependency health are otherwise low-risk because this repository contains little runtime code. The more important risks are unsafe instructions, stale facts, false activation, and unnecessary agent orchestration.

## Improvement Strategy

### Theme 1: Skills add capabilities, not generic competence

**Target state:** Every public skill passes the retention test: unique tool/script, external access, durable artifact protocol, project protocol, or demonstrably valuable reference corpus.

**Do not preserve:** Generic “be thorough,” “plan first,” “verify,” “explain clearly,” and familiar document templates. Those are native model behavior or short task constraints.

### Theme 2: Explicit routing for expensive workflows

**Target state:** Niche, high-context, destructive, or multi-agent workflows load only after an explicit user request. No public skill implicitly spawns agents.

**Done when:** Searching all descriptions and bodies for `subagent`, `spawn`, `parallel`, and `background agent` finds no automatic delegation instruction in the public set.

### Theme 3: Progressive disclosure and stable facts

**Target state:** Main `SKILL.md` files are short routers and invariant operating rules. Long examples, taxonomies, and source-specific instructions move to references. Volatile versions, counts, model names, and service recommendations are verified live or removed.

**Done when:** Every retained description is under 220 characters and every retained main skill is under roughly 100 lines unless its additional length is empirically justified.

### Theme 4: Separate public, private, and project-local workflows

**Target state:** Public skills contain no personal paths, names, account IDs, project IDs, or repo-specific template paths. Personal automation lives in private skills; project commands live in their repository.

**Done when:** A repository scan for `/Users/`, `Oscar`, project IDs, private env paths, and project-specific source paths is clean in the public set.

### Trade-offs

- Deprecating prompt-only skills may reduce output-format consistency for users who relied on exact templates. That is not loss of underlying functionality; users can request the format directly, or a short prompt template can live in documentation rather than auto-injected skill metadata.
- Merging the three archive skills reduces discovery noise but requires careful routing. Keep source-specific instructions in separate references so one source does not pollute another.
- `data-storytelling` and `name-it` contain actual domain material. Do not delete their references until a small A/B test shows Sol reaches the same quality without them.
- If Claude Code compatibility remains a product requirement, `mission` may still have a non-Codex audience. It should then be marketed and installed as a Claude-only plugin, not treated as necessary for Codex 5.6.

## Task Plan

### Quick wins

1. Disable or remove `delegate` first. It is the clearest stale, usage-multiplying workflow.
2. Remove automatic subagent language from `post-walk`, `xray`, and `mission` before any further public release.
3. Move `post-walk` private and `xray` into `startups-rip`.
4. Replace retained descriptions with the six short versions above.
5. Remove `filePattern` and `bashPattern` routing from `data-storytelling`.

### Milestones

| Milestone | Task | Areas | Acceptance criteria | Effort | Change risk | Depends on |
|---|---|---|---|---:|---:|---|
| 0 | Snapshot and evaluation harness | retained skill prompts, eval runner | Three representative positive prompts and three false-trigger prompts per probationary skill; run with and without skill on Sol; record quality, tool correctness, tokens, and latency | M | Low | None |
| 1 | Remove native-overlap skills | audit, delegate, explain, mission, PR/FAQ, spec, spring-cleaning, vibe-security | Folders, marketplace entries, README rows, and installed symlinks removed or disabled; no broken package references | M | Medium | 0 for audit/name/data evidence; immediate for delegate/spec/spring |
| 1 | Rehome non-public workflows | post-walk, xray | No personal/project identifiers remain in the public repo; destination installs still work | S | Medium | None |
| 2 | Merge archive workflows | three archive/transcript folders | One router selects article/X/YouTube correctly; all existing helper smoke tests and archive integrity checks pass | M | Medium | 1 |
| 2 | Slim retained skills | capture, data, fast-wifi, name-it, search-x | Descriptions under 220 characters; main files near 100 lines; volatile guidance moved/removed; no implicit delegation | M | Medium | 0 |
| 3 | Normalize packaging and docs | README, marketplace, archives, OpenAI metadata | README matches folders; every public skill has one packaging strategy and interface metadata; all archives pass integrity checks | S | Low | 1, 2 |

### Top implementation sketches

#### 1. Deprecation pass

Create a manifest of current folders, README rows, marketplace entries, installed symlinks, and packaged archives. Remove one capability at a time and validate that no retained skill links to it. Do not leave redirect comments or tombstone skills in the discovery path; use release notes if deprecation history matters.

#### 2. Archive merge

Create `archive-to-markdown/SKILL.md` as a short URL classifier. Route `x.com`/`twitter.com` to the existing X packager, YouTube URLs to the transcript helper, and other article URLs to archive.ph extraction. Put each existing workflow in a separate reference file and keep each script independently testable. Preserve all current output contracts and metadata.

#### 3. Probationary-skill A/B test

For `data-storytelling` and `name-it`, run the same prompts with Sol and no skill, then with the skill. Score concrete criteria, not vibes: chart choice, accessibility, responsive behavior, naming diversity, fit to brief, validation discipline, false activations, token usage, and latency. Keep only rules that produce repeatable lift; delete prose that merely restates good reasoning.

## Open Questions

1. Is the repository still intended to support Claude Code as a first-class public target, or should GPT-5.6 Codex be the sole retention baseline? This mainly affects whether `mission` is removed or separated as a Claude-only plugin.
2. Do you want exact output formats such as PR/FAQ and audit reports discoverable as documentation templates after their skills are removed, or is a clean deletion preferable?
3. Should the three archive workflows merge now, or remain separate because source-specific installation and permissions are useful to users?

The audit phase ends here. No skill implementation, deletion, description rewrite, packaging change, or git write was performed beyond this report.
