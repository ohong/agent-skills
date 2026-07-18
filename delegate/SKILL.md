---
name: delegate
description: Hand implementation work to Codex workers once planning is done. Invoke when Claude (Fable) has a plan/spec ready and is about to start coding — Fable specs and reviews, Codex implements. Skip for small edits (<~30 lines) or pure judgment tasks.
---

# Delegate

Three roles:

| Role | Model | Job |
|---|---|---|
| **General** (you, main loop) | Fable 5 | Plan, spec, orchestrate, advise — answer workers' questions when they're stuck or need a product/technical direction call; final judgment on what ships |
| **Workhorse** | Codex gpt-5.6 Sol, **medium** effort | Bulk of code generation: features, refactors, migrations, token-hungry work |
| **Fast worker** | Codex gpt-5.6 Luna, **high** effort | Tightly scoped grunt work: quick edits, surveys, file ops, running checks, repo chores |

Never gpt-5.5. Delegate for scale and context isolation, not "smarter" thinking. Treat the Workhorse as a peer engineer: specs state the goal and the why, not step-by-step instructions.

## 1 — Spec

Triage first: trivial (<~30 lines, or faster to do than spec) → do it yourself and say why. Ambiguous scope that's the user's call → ask 1–3 concise questions first. Note `git status` so worker changes stay distinguishable; commit nothing unless asked.

Write the spec to `<scratchpad>/spec.md` as compact XML blocks:

```xml
<task>One concrete job: goal, repo context, key files.</task>
<scope>In: ... Out: ... (explicit — this is where scope creep dies)</scope>
<implementation_notes>Decisions already made; interfaces and patterns to conform to.</implementation_notes>
<acceptance_criteria>Numbered, testable.</acceptance_criteria>
<verification_loop>Exact commands to run before declaring done.</verification_loop>
<action_safety>Stay narrow. No unrelated refactors, no new deps unless specified, no commits.</action_safety>
<escalation_contract>If blocked, or facing a decision that changes architecture, scope, or
public interfaces — do NOT guess. Print a "QUESTIONS:" block with options considered, then stop.</escalation_contract>
<output_contract>End with: files touched, what was verified (commands + results), residual risks.</output_contract>
```

## 2 — Run Codex

Resolve the companion runtime (highest version under `~/.claude/plugins/cache/openai-codex/codex/`, `scripts/codex-companion.mjs`), then:

```bash
node "<companion>" task --write --prompt-file "<scratchpad>/spec.md" \
  -c model="gpt-5.6-sol" -c model_reasoning_effort="medium"   # Workhorse; omit -c flags for Fast worker (config.toml default is luna/high)
```

- Bounded task → foreground with a generous Bash timeout (600000).
- Long/open-ended → the companion's own `--background` flag from a **foreground** Bash call — never a foreground companion inside a harness `run_in_background` shell (process tree gets SIGKILLed; bugs #432/#222). Wait with one `status <jobId> --wait --timeout-ms N` background call, never `while/sleep` loops; treat long-elapsed `running` as possibly stale; `result <jobId>` fetches output.
- Companion missing → fall back to `codex exec --sandbox workspace-write "$(cat <spec-file>)"`.
- Avoid the `codex:codex-rescue` agent (stub/orphan bugs #324/#395/#486). Prompt per the plugin's `gpt-5-4-prompting` skill.

## 3 — Advise

On a `QUESTIONS:` block: answer with your judgment as tech lead; surface only genuinely user-level questions (product direction, irreversible choices) to Oscar. Resume the **same** thread with deltas only: `task --resume-last "Answers: ..."`.

## 4 — Review & close

Review the actual diff against the acceptance criteria yourself — grade what exists, not what Codex claims; run the verification commands if the worker's evidence is thin. For substantial or high-stakes diffs, invoke the `/code-review` skill for an adversarial fresh-context review. On failure, feed findings verbatim into the same Codex thread (`--resume-last`); after 3 cycles, take over or surface the impasse. You are accountable for everything that ships.

Report: what was built, files changed, review outcome and cycle count, escalated questions and your answers, and the `codex resume <threadId>` command for continuing in Codex directly.
