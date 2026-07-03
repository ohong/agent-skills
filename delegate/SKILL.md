---
name: delegate
description: Run the Planner→Generator→Evaluator loop — Claude (Fable) specs the work, Codex GPT-5.5 implements it, an Opus 4.8 subagent grades the result against the spec. Use for implementation tasks big enough to spec — new features, refactors, migrations, bulk mechanical changes. Not for small edits (<~30 lines) or pure judgment tasks; do those directly.
---

# Delegate: Planner → Generator → Evaluator

You (Claude, the main loop) are the **Planner** — a product-minded tech lead. You decide architecture and scope, write the spec, answer questions, and hold final judgment. Codex (GPT-5.5 @ xhigh, the user's Codex default) is the **Generator**. An Opus 4.8 subagent is the **Evaluator**. You never hand-write the bulk implementation yourself in this flow.

## Step 0 — Triage

- If the task is trivial (roughly under 30 lines of change, or faster to do than to spec): skip delegation, do it directly, and tell the user why.
- If scope is genuinely ambiguous (the user's decision, not yours), ask 1–3 extremely concise questions before speccing.
- Note whether the working tree is dirty (`git status`) so Codex's changes stay distinguishable. Do not commit anything unless the user asked.

## Step 1 — Write the spec (Planner)

Write the spec to a file in the scratchpad directory (e.g. `<scratchpad>/spec.md`). Prompt Codex like an operator, not a collaborator — compact XML blocks:

```xml
<task>
One concrete job. Goal, relevant repo context, key files.
</task>

<scope>
In scope: ...
Out of scope: ... (be explicit — this is where scope creep dies)
</scope>

<implementation_notes>
Architecture decisions already made, interfaces to conform to,
patterns to follow from the existing codebase.
</implementation_notes>

<acceptance_criteria>
Numbered, testable criteria. These are what the Evaluator grades against.
</acceptance_criteria>

<verification_loop>
Exact commands to run before declaring done (tests, typecheck, lint, build).
Do not report success without running them.
</verification_loop>

<action_safety>
Stay narrow. No unrelated refactors, no dependency additions unless specified,
no commits. Leave the working tree uncommitted.
</action_safety>

<escalation_contract>
If you are blocked, or face a decision that changes architecture, scope, or
public interfaces — do NOT guess. Stop and print a block starting with
"QUESTIONS:" listing each question and the options you considered, then end
your turn.
</escalation_contract>

<output_contract>
End with: files touched, what was verified (commands + results), and any
residual risks. If you printed QUESTIONS, output nothing else after it.
</output_contract>
```

## Step 2 — Run Codex (Generator)

Resolve the companion runtime: list `~/.claude/plugins/cache/openai-codex/codex/` and use the highest version's `scripts/codex-companion.mjs`. Then:

```bash
node "<companion>" task --write --prompt-file "<scratchpad>/spec.md"
```

- Bounded task → run foreground with a generous Bash timeout (600000).
- Long/open-ended task → add `--background`, then use the `status <jobId> --wait` and `result <jobId>` subcommands.
- If the companion runtime is missing, fall back to `codex exec --sandbox workspace-write "$(cat <spec-file>)"`.
- Model and effort are already gpt-5.5 @ xhigh via the user's `~/.codex/config.toml` — don't pass `--model`/`--effort` unless overriding deliberately.

## Step 3 — Answer questions (advisor protocol)

If the output contains a `QUESTIONS:` block:
1. Answer each question yourself using your judgment as tech lead. Only surface to the user questions that are genuinely theirs (product direction, irreversible choices).
2. Resume the same thread with just the answers:
   ```bash
   node "<companion>" task --resume-last "Answers: ..."
   ```
Repeat as needed. Keep answers as deltas — don't restate the spec.

## Step 4 — Evaluate (Opus 4.8)

Spawn the Evaluator with the Agent tool, `model: "opus"`. Its prompt must include the full spec text and instructions to:
- Inspect the actual diff (`git diff` / `git status`) — grade what exists, not what Codex claims.
- Run the spec's verification commands.
- Grade each acceptance criterion individually: pass/fail + evidence (file:line).
- Return a final verdict: `PASS` or `FAIL`, with findings ordered by severity. No fixes — evaluation only.

## Step 5 — Loop or close

- **FAIL** → feed the Evaluator's findings verbatim into the same Codex thread (`task --resume-last`), then re-evaluate with a fresh Opus agent. Maximum 3 cycles; after that, fix the remainder yourself or surface the impasse to the user.
- **PASS** → spot-check the diff yourself (you are accountable for what ships). Then report.

## Step 6 — Report

Tell the user: what was built, files changed, evaluator verdict and cycle count, questions that were escalated and how you answered them, and the Codex thread resume command (`codex resume <threadId>`, printed in the companion output) in case they want to continue in Codex directly.
