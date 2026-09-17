"""Use FireConnect's public CLI for model discovery and Codex catalog generation.

FireConnect owns the Fireworks model catalog. This module never reimplements it.
It stages FireConnect's own `codex on` output in a disposable home, then returns
the generated catalog and metadata to the caller.
"""
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import tomllib

from fireworks_auth import credential

CATALOG_FILE = '.codex/fireworks-model-catalog.json'
FIREWORKS_BASE = 'https://api.fireworks.ai/inference/v1'
# Any valid reference works; the generated catalog does not depend on the selection.
STAGE_REFERENCE = 'kimi-latest'
# FireConnect curates reasoning tiers by hand, so families that accept the deep
# tier often arrive with only a low/medium/high ladder. Fireworks documents the
# deep tier for DeepSeek V4/V4.1, Kimi K3, and GLM 5.2. A live probe confirmed
# GLM 5.3 as well: `max` produced about ten times the reasoning tokens of `high`.
DEEP_TIER_FAMILIES = ('deepseek-', 'glm-', 'kimi-')
MAX_LEVEL = {'effort': 'max', 'description': 'Extra high reasoning depth for complex problems'}


def normalized(value):
    return re.sub(r'[^a-z0-9]', '', value.lower())


def cli(env, *args):
    executable = os.environ.get('FIRECONNECT_BIN') or shutil.which('fireconnect')
    if not executable:
        fallback = Path.home() / '.local/bin/fireconnect'
        executable = str(fallback) if fallback.is_file() else None
    if not executable:
        raise ValueError('FireConnect is required for Fireworks. Install it from https://github.com/fw-ai/fireconnect.')
    try:
        result = subprocess.run([executable, *args], env=env, capture_output=True, text=True, timeout=90)
    except subprocess.TimeoutExpired:
        raise ValueError('FireConnect timed out; config was not changed.') from None
    if result.returncode:
        # Upstream output can include diagnostic credentials; only emit a sanitized tail.
        detail = (result.stderr or result.stdout).replace(env['FIREWORKS_API_KEY'], '[redacted]')
        raise ValueError('FireConnect failed: ' + detail.strip()[-1200:])
    return result.stdout


def stage(home, env, reference):
    """Run FireConnect's own Codex setup in a disposable home and read its output."""
    config = home / '.codex/config.toml'
    config.parent.mkdir(parents=True, mode=0o700, exist_ok=True)
    config.write_text('')
    cli(env, 'codex', 'on', '--model', reference, '--home', str(home),
        '--config-path', str(config), '--data-dir', str(home / 'state'))
    if not config.is_file():
        raise ValueError('FireConnect did not write a Codex config; config was not changed.')
    catalog_path = home / CATALOG_FILE
    if not catalog_path.is_file():
        raise ValueError('FireConnect did not generate model metadata; config was not changed. Retry when its catalog is available.')
    staged = tomllib.loads(config.read_text())
    catalog = json.loads(catalog_path.read_text())
    provider = staged.get('model_providers', {}).get(staged.get('model_provider'), {})
    if provider.get('base_url', '').rstrip('/') != FIREWORKS_BASE or provider.get('wire_api') != 'responses':
        raise ValueError('FireConnect generated an unexpected endpoint or protocol; config was not changed.')
    entries = catalog.get('models') or []
    if not entries:
        raise ValueError('FireConnect generated an empty Codex catalog; config was not changed.')
    return catalog, staged, entries


def add_deep_tier(catalog):
    """Restore the `max` tier that FireConnect's curated ladder omits."""
    for entry in catalog.get('models', []):
        slug = entry.get('slug') or ''
        levels = entry.get('supported_reasoning_levels') or []
        if not slug.startswith(DEEP_TIER_FAMILIES):
            continue
        if any(level.get('effort') == 'max' for level in levels):
            continue
        entry['supported_reasoning_levels'] = [*levels, MAX_LEVEL]


def details(env, home):
    """Optional pricing/context rows from FireConnect's public model list."""
    try:
        raw = json.loads(cli(env, 'model', 'list', '--json', '--home', str(home)))
    except ValueError:
        return {}
    index = {}
    for row in raw.get('models', []):
        key = row.get('shortId') or (row.get('id') or '').rsplit('/', 1)[-1]
        if key:
            index[key] = row
    return index


def prepare(target=None, search=None):
    """Return the FireConnect catalog, or the list of models it exposes to Codex."""
    key = credential()
    if any(char.isspace() for char in key) or key.startswith('fpk_'):
        raise ValueError('Codex needs a standard Fireworks API key, not a Fire Pass key.')
    env = os.environ | {'FIREWORKS_API_KEY': key, 'FIRECONNECT_NO_UPDATE_PROMPT': '1', 'FIRECONNECT_KEY_STORAGE': 'null'}
    # Do not forward unrelated BYOK credentials into a Fireworks-only setup.
    for name in ('ANTHROPIC_API_KEY', 'OPENAI_API_KEY', 'AZURE_API_KEY'):
        env.pop(name, None)
    with tempfile.TemporaryDirectory(prefix='codex-fireconnect-') as directory:
        home = Path(directory)
        env.update(XDG_CONFIG_HOME=str(home / 'config'), XDG_DATA_HOME=str(home / 'data'))
        catalog, staged, entries = stage(home, env, target or STAGE_REFERENCE)
        add_deep_tier(catalog)
        info = details(env, home)
        rows = []
        for entry in entries:
            slug = entry.get('slug')
            if not slug:
                continue
            row = info.get(slug, {})
            rows.append({'id': row.get('id', slug), 'short_id': slug, 'name': entry.get('display_name', ''),
                         'context_window': entry.get('context_window'), 'vision': bool(row.get('vision')),
                         'pricing': row.get('pricing')})
        rows.sort(key=lambda row: row['short_id'])
        if target is None:
            query = normalized(search or '')
            return {'source': 'fireconnect', 'models': [row for row in rows
                    if query in normalized(row['short_id'] + ' ' + row['name'])]}
        if 'minimax' in target.lower():
            raise ValueError('MiniMax is currently incompatible with Codex tool-message ordering. Use another harness.')
        slug = staged.get('model')
        selected = next((entry for entry in entries if entry.get('slug') == slug), None)
        known = [row['short_id'] for row in rows]
        if not slug or not selected:
            raise ValueError('FireConnect exposes only these Codex models: ' + ', '.join(known)
                             + '. Use --list to see them.')
        return {'model': slug, 'catalog': catalog, 'web_search': staged.get('web_search', 'disabled'),
                'source': 'fireconnect', 'model_id': next((row['id'] for row in rows if row['short_id'] == slug), slug),
                'efforts': [level['effort'] for level in selected.get('supported_reasoning_levels', [])]}
