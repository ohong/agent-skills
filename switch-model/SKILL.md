---
name: switch-model
description: Switch the Codex default model and provider in config.toml, discover Fireworks serverless models, or restore GPT and the existing Grok subscription adapter. Use for $switch-model, the typo $swtich-model, or requests to change Codex's default model.
---

# Switch model

Run the helper to change the default model. The user's switch request authorizes the config edit.
Resolve script paths relative to this skill directory. Requires Python 3.11+, Node.js, and FireConnect.
On this machine, `codex-switch-model` runs the same helper from the terminal.

1. Use a familiar alias, or discover exact IDs with `python3 scripts/switch_model.py --list --search NAME`.
2. Run the switch, for example `python3 scripts/switch_model.py kimi k3`.
3. Report the saved model, provider, effort, and session restart requirement.

```bash
codex-switch-model --list
codex-switch-model --list --search glm
codex-switch-model kimi k3
codex-switch-model glm 5.3 flash
codex-switch-model deepseek
codex-switch-model kimi-latest
codex-switch-model accounts/fireworks/models/kimi-k3
codex-switch-model --effort medium kimi k3
codex-switch-model --dry-run kimi k3
codex-switch-model --status
codex-switch-model grok
codex-switch-model gpt
```

Use `$switch-model kimi k3` inside Codex. Also recognize the user's `$swtich-model` typo.
`--list` fetches the account's serverless catalog through FireConnect and supports `--search`.
Exact IDs and unambiguous display names work without editing aliases. Unversioned `kimi`, `glm`, and `deepseek` use Fireworks latest routers; DeepSeek defaults to its Flash router.
`kimi fast`, `glm fast`, `glm flash`, and `deepseek pro` select their corresponding latest routers.
Explicit versions remain pinned. Latest routers follow Fireworks routing decisions and can lag a newer named release.
The list excludes MiniMax, non-tool models, and smart/BYOK routers. MiniMax currently conflicts with Codex tool-message ordering.
Missing or ambiguous IDs fail without changing the config. Do not invent model IDs or claim every serverless model supports Codex.

The helper uses FireConnect's generated model metadata, including context windows and reasoning options.
FireConnect 0.9.6's CLI drops pinned models when it prefers latest aliases. A small Node bridge calls its upstream catalog builder before that filter.
The bridge generates routing and metadata in a private temporary directory. The helper imports only relevant model settings and the catalog.
It retains command-backed authentication, preserves unrelated TOML and provider credentials, and writes private backups.
It never calls `fireconnect codex off`, because restoring that full snapshot could overwrite later edits.
GPT restores saved OpenAI settings. Leaving Fireworks restores the prior model catalog and web-search setting.
Fireworks temporarily sets `web_search = "disabled"`, as its Responses endpoint cannot accept Codex's server-executed search tool.
Non-GPT models default to `high`. Explicit efforts must be supported by the Fireworks model's metadata.

FireConnect must be installed at `~/.fireconnect/cli`, or set `FIRECONNECT_SOURCE` to its source checkout.
`FIRECONNECT_BIN` and `FIRECONNECT_NODE` override executable discovery. The bridge depends on FireConnect's internal exports;
if an upgrade changes them, report the integration error and repair the bridge before switching.
See the [official Codex integration](https://docs.fireworks.ai/ecosystem/fireconnect/codex).

Fireworks authentication checks `FIREWORKS_API_KEY`, then `~/.codex/credentials/fireworks-api-key` (mode 0600),
then macOS Keychain service `codex-fireworks-api-key`. `CODEX_HOME` and `FIREWORKS_API_KEY_FILE` override locations.
Check availability only with `scripts/fireworks_auth.py --check`; never print the credential helper's normal output.
Keys are passed through a subprocess environment and temporary private files, never command arguments or the permanent Codex config.
Listing, dry runs, and switches make catalog requests; they do not run inference. Dry runs leave the target config and its state unchanged.

Grok retains the configured subscription adapter. Never replace it with xAI API billing.
A switch does not prove authentication. For HTTP 401, run `grok login --oauth` and request browser sign-in.
The existing Grok credential helper does not refresh tokens itself.

Changing `config.toml` changes a default. Existing tasks can keep their selected model.
For CLI verification, start a fresh `codex` session and check its `/status` model and provider.
For desktop verification, quit and reopen Codex after switching, create a fresh task, and inspect its selected model.
Do not claim an active task switched solely because the saved config changed.
The terminal helper remains usable when the Codex subscription quota is exhausted.

For a real provider check, use a temporary workspace and request a harmless file read/edit/readback.
On this machine the CLI rejects the desktop's existing `[features.context_management]` table.
Use `codex -c features.context_management=false` for that one session; preserve the saved desktop setting.
Test results for one model do not establish compatibility for every model or tool.
