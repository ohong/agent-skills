---
name: switch-model
description: Switch the Codex default model and provider in config.toml, list the Fireworks models FireConnect exposes, or restore GPT and the existing Grok subscription adapter. Use for $switch-model, the typo $swtich-model, or requests to change Codex's default model.
---

# Switch model

Run the helper to change the default model. The user's switch request authorizes the config edit.
Resolve script paths relative to this skill directory. Requires Python 3.11+ and FireConnect.
On this machine, `codex-switch-model` runs the same helper from the terminal.

1. Use a familiar alias, or list exact IDs with `python3 scripts/switch_model.py --list --search NAME`.
   `--list` reports each model's id, display name, context window, vision support, and price.
2. Run the switch, for example `python3 scripts/switch_model.py kimi`.
3. Report the saved model, provider, effort, and session restart requirement.

```bash
codex-switch-model --list
codex-switch-model --list --search glm
codex-switch-model kimi
codex-switch-model kimi fast
codex-switch-model glm flash
codex-switch-model deepseek pro
codex-switch-model deepseek-flash-latest
codex-switch-model --effort medium kimi
codex-switch-model --dry-run kimi
codex-switch-model --status
codex-switch-model grok
codex-switch-model gpt
```

Use `$switch-model kimi` inside Codex. Also recognize the user's `$swtich-model` typo.

FireConnect owns the Fireworks model catalog. This helper ships no catalog of its own.
It stages FireConnect's own `fireconnect codex on` output in a private temporary home, then reads the
generated Codex catalog and model list from that directory. Aliases point at Fireworks latest routers.
The helper edits that catalog in exactly one way: it restores the `max` reasoning tier described below.
Only models present in FireConnect's catalog are accepted; anything else fails without changing the config.

FireConnect's Codex catalog keeps one latest entry per model family, so pinned versions such as
`kimi-k3` or `deepseek-v4-pro-0813` are not selectable. Use the family router instead.
The catalog can include region-only deployments such as `kimi-k3-us` and `glm-5p3-flash-us`.

FireConnect curates reasoning tiers by hand and grants `max` to only a few base refs, so DeepSeek,
GLM, and Kimi families arrive with a three-tier ladder. The helper restores `max` on those families.
Fireworks documents the deep tier for DeepSeek V4/V4.1, Kimi K3, and GLM 5.2; a live probe confirmed
it for GLM 5.3. Measured cost: `max` uses two to twelve times the output tokens of `low` and rarely
improves accuracy on small coding tasks. Prefer `low` or `high`, and reach for `max` only when a task
needs deep deliberation.
The list excludes MiniMax, non-tool models, and the FireRouter BYOK router. MiniMax currently conflicts
with Codex tool-message ordering. Missing or ambiguous IDs fail without changing the config.
Do not invent model IDs or claim every serverless model supports Codex.

Kimi K3 works in CLI sessions but currently fails in Codex desktop sessions. Fireworks rejects any tool schema
that sets `type` beside `$ref`, and a desktop app tool sends that shape. The turn ends with
`stream disconnected before completion: JSON Schema not supported: when using $ref, type should be defined in the
referenced schema instead of the parent schema.` DeepSeek and GLM accept that shape. Verified on 2026-09-17:
`kimi-fast-latest` failed in this desktop thread, passed in two CLI sessions, and a direct Fireworks probe reproduced
the exact rejection. Use Kimi in the CLI, or DeepSeek/GLM in the desktop, until the app or Fireworks fixes it.

The helper keeps its own TOML writer. It preserves unrelated TOML and provider credentials, retains
command-backed authentication, and writes private backups. It never writes the API key into `config.toml`.
It never calls `fireconnect codex off`, because restoring that full snapshot could overwrite later edits.
GPT restores saved OpenAI settings. Leaving Fireworks restores the prior model catalog and web-search setting.
Fireworks temporarily sets `web_search = "disabled"`, as its Responses endpoint cannot accept Codex's
server-executed search tool. See the WebSearch MCP note below for the supported replacement.
Non-GPT models default to `high`. Explicit efforts must be supported by the Fireworks model's metadata.
Fireworks promotes `xhigh` into `max`, so `max` is the only way to select the deepest tier; `--effort xhigh`
fails with the supported list.

`fireconnect codex on` cannot patch this machine's real `config.toml` directly: FireConnect's TOML parser
rejects root integers above 2^53, and `[agents] max_concurrent_threads_per_session` exceeds that.
Route through this helper, or lower that value first.

FireConnect must be installed at `~/.fireconnect/cli` or on `PATH`.
`FIRECONNECT_BIN` overrides executable discovery. The helper uses only FireConnect's public CLI commands,
so a FireConnect upgrade is unlikely to break it; report any integration error before switching.
See the [official Codex integration](https://docs.fireworks.ai/ecosystem/fireconnect/codex).

Fireworks authentication checks `FIREWORKS_API_KEY`, then `$CODEX_HOME/credentials/fireworks-api-key`
(mode 0600), then macOS Keychain service `codex-fireworks-api-key`. `FIREWORKS_API_KEY_FILE` overrides the path.
Check availability only with `scripts/fireworks_auth.py --check`; never print the credential helper's normal output.
Keys are passed through a subprocess environment, never command arguments or the permanent Codex config.
Listing, dry runs, and switches make catalog requests; they do not run inference.

Grok retains the configured subscription adapter. Never replace it with xAI API billing.
A switch does not prove authentication. For HTTP 401, run `grok login --oauth` and request browser sign-in.
The existing Grok credential helper does not refresh tokens itself.

## Web search on Fireworks models

Codex's built-in `web_search` is an OpenAI server-side tool. Fireworks' Responses endpoint rejects it,
so Fireworks models run with `web_search = "disabled"`.

The supported replacement is the Fireworks WebSearch MCP server:

- URL `https://mcp.fireworks.ai/work/mcp`, auth `Authorization: Bearer <fireworks-api-key>`.
- Access is not enabled on every account. Request it from the Fireworks team.
- FireConnect auto-installs it for Claude Code only; add it to `~/.codex/config.toml` by hand for Codex.
- Billing is not published. Searches are attributed to the calling API key, so a billable price is likely.

Changing `config.toml` changes a default. Existing tasks can keep their selected model.
For CLI verification, start a fresh `codex` session and check its `/status` model and provider.
For desktop verification, quit and reopen Codex after switching, create a fresh task, and inspect its selected model.
Do not claim an active task switched solely because the saved config changed.
The terminal helper remains usable when the Codex subscription quota is exhausted.

For a real provider check, use a temporary workspace and request a harmless file read/edit/readback.
On this machine the CLI rejects the desktop's existing `[features.context_management]` table.
Use `codex -c features.context_management=false` for that one session; preserve the saved desktop setting.
Test results for one model do not establish compatibility for every model or tool.
