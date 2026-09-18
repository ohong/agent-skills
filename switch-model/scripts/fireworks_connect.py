"""Use FireConnect's public CLI plus Fireworks' model API for Codex switching.

FireConnect owns the curated Codex catalog. This module never reimplements it.
It stages FireConnect's own `codex on` output in a disposable home, then returns
the generated catalog and metadata to the caller. Models outside that catalog
still work: Fireworks' model API lists every callable serverless model, and this
module gives those models a conservative generic catalog entry.
"""
import copy
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import tomllib
import urllib.error
import urllib.request

from fireworks_auth import credential

CATALOG_FILE = '.codex/fireworks-model-catalog.json'
FIREWORKS_BASE = 'https://api.fireworks.ai/inference/v1'
FIREWORKS_MODELS_URL = FIREWORKS_BASE + '/models'
FIREWORKS_RESPONSES_URL = FIREWORKS_BASE + '/responses'
# Any valid reference works; the generated catalog does not depend on the selection.
STAGE_REFERENCE = 'kimi-latest'
# Fireworks does not report a context length for every model. Claiming a window
# that is too large delays compaction until the server rejects the request, so
# the generic fallback stays deliberately small; compaction then happens early.
GENERIC_CONTEXT_WINDOW = 65536
GENERIC_LEVELS = [{'effort': 'low', 'description': 'Fast responses with lighter reasoning'},
                  {'effort': 'medium', 'description': 'Balances speed and reasoning depth for everyday tasks'},
                  {'effort': 'high', 'description': 'Greater reasoning depth for complex problems'}]
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


def short_id(model_id):
    """Return the Fireworks short id for a router or model id."""
    for prefix in ('accounts/fireworks/models/', 'accounts/fireworks/routers/'):
        if model_id.startswith(prefix):
            return model_id[len(prefix):]
    return model_id


def fetch_serverless_models(key):
    """Return Fireworks' callable models from the model API, keyed by short id."""
    url = os.environ.get('FIREWORKS_MODELS_URL') or FIREWORKS_MODELS_URL
    request = urllib.request.Request(url, headers={'Authorization': 'Bearer ' + key})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = json.load(response)
    except (OSError, ValueError) as exc:
        raise ValueError('Could not read the Fireworks model list: ' + str(exc)) from None
    rows = payload.get('data') or []
    return {short_id(row['id']): row for row in rows if row.get('id')}


def usable_serverless_model(slug, row):
    """Codex needs chat plus function tools; MiniMax breaks tool-message ordering."""
    return (bool(row.get('supports_chat') and row.get('supports_tools'))
            and 'minimax' not in slug.lower() and 'firerouter' not in slug.lower())


def validate_serverless_model(key, model_id):
    """Run one tiny request so unusable models fail before the config changes.

    Codex sends developer-role messages on the Responses API. Some Fireworks chat
    templates reject that role, and some listed models are not deployed. A minimal
    probe catches both failure classes without changing any files.
    """
    body = {'model': model_id, 'stream': False, 'max_output_tokens': 64,
            'input': [{'role': 'developer', 'content': [{'type': 'input_text', 'text': 'Be brief.'}]},
                      {'role': 'user', 'content': [{'type': 'input_text', 'text': 'Reply with exactly: OK'}]}]}
    url = os.environ.get('FIREWORKS_RESPONSES_URL') or FIREWORKS_RESPONSES_URL
    request = urllib.request.Request(url, data=json.dumps(body).encode(),
                                     headers={'Authorization': 'Bearer ' + key, 'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            json.load(response)
    except urllib.error.HTTPError as exc:
        try:
            detail = json.loads(exc.read().decode()).get('error', {}).get('message', '')
        except (OSError, ValueError):
            detail = ''
        raise ValueError('Fireworks rejected ' + model_id + ' in a validation probe: '
                         + (detail or str(exc)) + '. No file changed.') from None
    except (OSError, ValueError) as exc:
        raise ValueError('Could not validate ' + model_id + ': ' + str(exc)) from None


def generic_catalog_entry(template, row):
    """Build a conservative catalog entry for a model FireConnect does not curate.

    Copy a known-good curated entry so every field Codex requires stays present,
    then override only identity, limits, modalities, and the reasoning ladder.
    """
    # Codex matches catalog entries by slug, so the slug must equal the model id
    # saved in config.toml. Use Fireworks' full id because it is the canonical form.
    context = row.get('context_length') or GENERIC_CONTEXT_WINDOW
    modalities = ['text'] + (['image'] if row.get('supports_image_input') else [])
    # The deep tier is documented for the same families FireConnect curates, and a
    # 2026-09-18 probe confirmed Fireworks accepts `max` for deepseek-v4p1-flash.
    levels = list(GENERIC_LEVELS)
    if short_id(row['id']).startswith(DEEP_TIER_FAMILIES):
        levels.append(MAX_LEVEL)
    entry = copy.deepcopy(template)
    entry.update(slug=row['id'], display_name=short_id(row['id']),
                 description='Fireworks serverless model using a generic Codex catalog entry.',
                 context_window=context, max_context_window=context, input_modalities=modalities,
                 supports_image_detail_original=bool(row.get('supports_image_input')),
                 supported_reasoning_levels=levels, default_reasoning_level='high')
    return entry


def prepare(target=None, search=None, validate=False):
    """Return the catalog for one switch, or every model Codex can use on Fireworks."""
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
        # The generated catalog does not depend on the selected reference, so one
        # staging run serves curated and generic models alike.
        catalog, staged, entries = stage(home, env, STAGE_REFERENCE)
        add_deep_tier(catalog)
        info = details(env, home)
        curated = []
        for entry in entries:
            slug = entry.get('slug')
            if not slug:
                continue
            row = info.get(slug, {})
            curated.append({'id': row.get('id', slug), 'short_id': slug, 'name': entry.get('display_name', ''),
                            'context_window': entry.get('context_window'), 'vision': bool(row.get('vision')),
                            'pricing': row.get('pricing'), 'in_codex_catalog': True})
        curated.sort(key=lambda row: row['short_id'])
        curated_slugs = {row['short_id'] for row in curated}
        if target is None:
            serverless = fetch_serverless_models(key)
            rows = list(curated)
            for slug, model in serverless.items():
                if slug in curated_slugs or not usable_serverless_model(slug, model):
                    continue
                detail = info.get(slug, {})
                rows.append({'id': model['id'], 'short_id': slug, 'name': detail.get('displayName') or slug,
                             'context_window': model.get('context_length') or GENERIC_CONTEXT_WINDOW,
                             'vision': bool(model.get('supports_image_input')), 'pricing': detail.get('pricing'),
                             'in_codex_catalog': False})
            rows.sort(key=lambda row: row['short_id'])
            query = normalized(search or '')
            return {'source': 'fireworks', 'models': [row for row in rows
                    if query in normalized(row['short_id'] + ' ' + row['name'])]}
        if 'minimax' in target.lower():
            raise ValueError('MiniMax is currently incompatible with Codex tool-message ordering. Use another harness.')
        slug = short_id(target)
        selected = next((entry for entry in entries if entry.get('slug') == slug), None)
        if selected is not None:
            return {'model': slug, 'catalog': catalog, 'web_search': staged.get('web_search', 'disabled'),
                    'source': 'fireconnect',
                    'model_id': next((row['id'] for row in curated if row['short_id'] == slug), slug),
                    'efforts': [level['effort'] for level in selected.get('supported_reasoning_levels', [])]}
        model = fetch_serverless_models(key).get(slug)
        if model is None:
            raise ValueError('Fireworks does not expose a serverless model named ' + target
                             + '. Run --list to see compatible models.')
        if not usable_serverless_model(slug, model):
            raise ValueError(slug + ' does not support chat with function tools, which Codex requires.')
        if validate:
            validate_serverless_model(key, model['id'])
        # Reuse a known-good curated entry so every required catalog field exists.
        template = next((entry for entry in entries if entry.get('slug') == 'deepseek-flash-latest'), entries[0])
        entry = generic_catalog_entry(template, model)
        catalog.setdefault('models', []).append(entry)
        return {'model': model['id'], 'catalog': catalog, 'web_search': staged.get('web_search', 'disabled'),
                'source': 'fireworks-generic', 'model_id': model['id'],
                'efforts': [level['effort'] for level in entry['supported_reasoning_levels']]}
