"""Use FireConnect discovery and catalog generation in a disposable home."""
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import tomllib

from fireworks_auth import credential


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


def prepare(target=None, search=None):
    """Fetch eligible IDs, and optionally stage official routing/catalog generation."""
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
        raw = json.loads(cli(env, 'model', 'list', '--json', '--refresh', '--home', directory))
        rows = [row for row in raw.get('models', [])
                if row.get('kind') == 'serverless' and row.get('toolCalling')
                and (row.get('maxInputTokens') or 0) > 0
                and row.get('id', '').startswith('accounts/fireworks/')
                and 'minimax' not in row['id'].lower()
                and row.get('shortId') != 'firerouter']
        if not rows:
            raise ValueError('FireConnect returned no compatible serverless models; config was not changed.')
        if target is None:
            query = normalized(search or '')
            return {'source': raw.get('source'), 'updated_at': raw.get('updatedAt'),
                    'models': [{'id': row['id'], 'name': row.get('displayName'),
                                'context_window': row['maxInputTokens'], 'pricing': row.get('pricing')}
                               for row in rows if query in normalized(row['id'] + ' ' + row.get('displayName', ''))]}
        if 'minimax' in target.lower():
            raise ValueError('MiniMax is currently incompatible with Codex tool-message ordering. Use another harness.')
        exact = [row for row in rows if target in (row['id'], row.get('shortId'))]
        matches = exact or [row for row in rows if normalized(target) in
                            (normalized(row.get('shortId', '')), normalized(row.get('displayName', '')))]
        if len(matches) != 1:
            raise ValueError('Model is unavailable or ambiguous in your Fireworks serverless catalog. Use --list --search NAME and copy an exact ID.')
        selected = matches[0]
        config = home / '.codex/config.toml'
        config.parent.mkdir(mode=0o700)
        config.write_text('')
        source = Path(os.environ.get('FIRECONNECT_SOURCE', str(Path.home() / '.fireconnect/cli')))
        node = os.environ.get('FIRECONNECT_NODE') or shutil.which('node')
        if not node or not (source / 'packages/setup-cli/lib/harnesses/codex/catalog.mjs').is_file():
            raise ValueError('FireConnect source or Node.js unavailable. Set FIRECONNECT_SOURCE for a nonstandard installation.')
        try:
            result = subprocess.run([node, str(Path(__file__).with_name('fireconnect_catalog.mjs')),
                                     str(source), directory, selected['id']],
                                    env=env, capture_output=True, text=True, timeout=90)
        except subprocess.TimeoutExpired:
            raise ValueError('FireConnect catalog generation timed out; config was not changed.') from None
        if result.returncode:
            raise ValueError(result.stderr.replace(key, '[redacted]').strip()[-1200:])
        staged = tomllib.loads(config.read_text())
        catalog_file = home / '.codex/fireworks-model-catalog.json'
        if not catalog_file.is_file() or not staged.get('model_catalog_json'):
            raise ValueError('FireConnect did not generate model metadata; config was not changed. Retry when its catalog is available.')
        catalog = json.loads(catalog_file.read_text())
        slug = staged['model']
        selected_metadata = next((entry for entry in catalog.get('models', []) if entry.get('slug') == slug), None)
        if not selected_metadata:
            raise ValueError('Selected model is absent from the generated Codex catalog; config was not changed.')
        provider = staged.get('model_providers', {}).get(staged.get('model_provider'), {})
        if provider.get('base_url', '').rstrip('/') != 'https://api.fireworks.ai/inference/v1' or provider.get('wire_api') != 'responses':
            raise ValueError('FireConnect generated an unexpected endpoint or protocol; config was not changed.')
        # Store only serverless entries. FireConnect can synthesize auto/BYOK routers.
        eligible = {row.get('shortId', row['id'].rsplit('/', 1)[-1]) for row in rows}
        catalog['models'] = [entry for entry in catalog['models'] if entry.get('slug') in eligible]
        return {'model': slug, 'catalog': catalog, 'web_search': staged.get('web_search', 'disabled'),
                'source': raw.get('source'), 'model_id': selected['id'],
                'efforts': [level['effort'] for level in selected_metadata.get('supported_reasoning_levels', [])]}
