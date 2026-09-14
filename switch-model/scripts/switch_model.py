#!/usr/bin/env python3
"""Switch Codex's default provider/model without reserializing unrelated TOML."""
import argparse
import copy
from datetime import datetime, timezone
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import sys
import tempfile
import tomllib
from urllib.parse import urlparse
from fireworks_connect import prepare as prepare_fireworks

ROOT_KEYS = ('model', 'model_provider', 'model_reasoning_effort', 'model_catalog_json', 'web_search')
FIREWORKS_BASE = 'https://api.fireworks.ai/inference/v1'
ALIASES = {
    'kimi': 'accounts/fireworks/routers/kimi-latest',
    'kimi fast': 'accounts/fireworks/routers/kimi-fast-latest',
    'kimi k3': 'accounts/fireworks/models/kimi-k3',
    'kimi k3 fast': 'accounts/fireworks/routers/kimi-k3-fast',
    'glm': 'accounts/fireworks/routers/glm-latest',
    'glm fast': 'accounts/fireworks/routers/glm-fast-latest',
    'glm flash': 'accounts/fireworks/routers/glm-flash-latest',
    'glm 5.3': 'accounts/fireworks/models/glm-5p3',
    'glm 5.3 flash': 'accounts/fireworks/models/glm-5p3-flash',
    'glm 5.3 fast': 'accounts/fireworks/routers/glm-5p3-fast',
    'deepseek': 'accounts/fireworks/routers/deepseek-flash-latest',
    'deepseek flash': 'accounts/fireworks/routers/deepseek-flash-latest',
    'deepseek pro': 'accounts/fireworks/routers/deepseek-pro-latest',
    'deepseek v4.1 flash': 'accounts/fireworks/models/deepseek-v4p1-flash',
    'deepseek v4 pro': 'accounts/fireworks/models/deepseek-v4-pro-0813',
}
EFFORTS = ('none', 'minimal', 'low', 'medium', 'high', 'xhigh', 'max', 'ultra')


def atomically_write(path, value, mode=0o600):
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    fd, temp = tempfile.mkstemp(prefix='.' + path.name + '.', dir=path.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8', newline='') as handle:
            os.fchmod(handle.fileno(), mode)
            handle.write(value)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp, path)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


def read_exact(path):
    with path.open(encoding='utf-8', newline='') as handle:
        return handle.read()


def scalar(value):
    return json.dumps(value, ensure_ascii=False)


def edit_root(text, values):
    """Conservative line edits; semantic validation below rejects ambiguous TOML."""
    lines = text.splitlines(keepends=True)
    boundary = next((i for i, line in enumerate(lines) if re.match(r'^\s*\[', line)), len(lines))
    additions = []
    for key, value in values.items():
        pattern = re.compile(r'^(\s*(?:' + re.escape(key) + '|"' + re.escape(key) + '"|\'' + re.escape(key) + r'\')\s*=\s*)(.*?)(\r?\n)?$')
        matches = [(i, pattern.match(line)) for i, line in enumerate(lines[:boundary]) if pattern.match(line)]
        if len(matches) > 1:
            raise ValueError('Ambiguous root field: ' + key)
        if matches:
            index, match = matches[0]
            if value is None:
                lines[index] = ''
            else:
                # Only ordinary one-line strings are replaced. Retain trailing comments.
                old = match[2]
                tail = re.fullmatch(r'(?:"(?:[^"\\]|\\.)*"|\'[^\']*\')(\s*(?:#.*)?)', old)
                if not tail:
                    raise ValueError('Unsupported root-field formatting for ' + key + '; no file changed.')
                lines[index] = match[1] + scalar(value) + tail[1] + (match[3] or '')
        elif value is not None:
            additions.append(key + ' = ' + scalar(value) + '\n')
    if additions:
        if boundary and lines[boundary - 1] and not lines[boundary - 1].endswith('\n'):
            lines[boundary - 1] += '\n'
        lines[boundary:boundary] = additions
    return ''.join(lines)


def fireworks_definition():
    return {
        'name': 'Fireworks AI', 'base_url': FIREWORKS_BASE, 'wire_api': 'responses',
        'supports_websockets': False,
        'auth': {'command': str(Path(__file__).resolve().with_name('fireworks_auth.py')), 'timeout_ms': 10000, 'refresh_interval_ms': 300000},
    }


def append_fireworks(text, definition):
    result = text + ('' if text.endswith('\n') else '\n') + '\n[model_providers.fireworks]\n'
    for key, value in definition.items():
        if key == 'auth':
            continue
        result += key + ' = ' + ('true' if value is True else 'false' if value is False else scalar(value)) + '\n'
    result += '\n[model_providers.fireworks.auth]\n'
    for key, value in definition['auth'].items():
        result += key + ' = ' + scalar(value) + '\n'
    return result


def resolve(args, data, state):
    target = ' '.join(args.target).strip()
    alias = re.sub(r'[-_]+', ' ', target.lower())
    alias = re.sub(r'\s+', ' ', alias)
    if not target:
        raise ValueError('Specify a model, or use --status / --list.')
    if any(ord(char) < 32 for char in target):
        raise ValueError('Model names cannot contain control characters.')
    if alias in ('gpt', 'openai', 'codex') and not args.provider:
        saved = state.get('openai')
        if not saved:
            if data.get('model_provider', 'openai') == 'openai':
                saved = {k: data[k] for k in ROOT_KEYS if k in data}
            else:
                raise ValueError('No saved GPT settings. Specify an exact GPT model, e.g. --provider openai gpt-6-astra.')
        updates = {key: saved.get(key) for key in ROOT_KEYS}
        if args.effort:
            updates['model_reasoning_effort'] = args.effort
        return updates, 'openai'
    if alias in ALIASES and not args.provider:
        model, provider = ALIASES[alias], 'fireworks'
    elif alias in ('grok', 'grok 4.6') and not args.provider:
        model, provider = 'grok-4.6', 'grok'
    else:
        model = target
        provider = args.provider
        if not provider:
            if model.startswith('accounts/fireworks/'):
                provider = 'fireworks'
            elif model.startswith('gpt-') or re.fullmatch(r'o[1-9](?:-.*)?', model):
                provider = 'openai'
            elif model.startswith('grok-'):
                provider = 'grok'
            else:
                provider = 'fireworks'
    if not re.fullmatch(r'[A-Za-z0-9_-]+', provider):
        raise ValueError('Provider IDs may contain only letters, digits, underscores, and hyphens.')
    effort = args.effort or ('high' if not model.startswith('gpt-') else state.get('openai', data if data.get('model_provider', 'openai') == 'openai' else {}).get('model_reasoning_effort', 'high'))
    return {'model': model, 'model_provider': provider, 'model_reasoning_effort': effort}, provider


def run(args):
    if args.list:
        print(json.dumps(prepare_fireworks(search=args.search), indent=2))
        return
    path = args.config.expanduser().absolute()
    if path.is_symlink():
        raise ValueError('Config is a symlink; pass its resolved target explicitly.')
    before = read_exact(path)
    data = tomllib.loads(before)
    if args.status:
        print(json.dumps({key: data.get(key) for key in ROOT_KEYS}, indent=2))
        return
    state_dir = args.state_dir or path.parent / 'switch-model' / hashlib.sha256(str(path).encode()).hexdigest()[:12]
    state_file = state_dir / 'state.json'
    state = json.loads(state_file.read_text()) if state_file.exists() else {}
    updates, provider = resolve(args, data, state)
    providers = data.get('model_providers', {})
    add_provider = None
    prepared = None
    if provider == 'fireworks':
        existing = providers.get(provider)
        if existing is None:
            add_provider = fireworks_definition()
        elif existing.get('base_url', '').rstrip('/') != FIREWORKS_BASE or existing.get('wire_api') != 'responses':
            raise ValueError('Existing fireworks provider uses another endpoint or protocol. Resolve that conflict before switching.')
        prepared = prepare_fireworks(updates['model'])
        if updates['model_reasoning_effort'] not in prepared['efforts']:
            raise ValueError('Unsupported reasoning effort for this model. Available: ' + ', '.join(prepared['efforts']))
        catalog_text = json.dumps(prepared['catalog'], indent=2) + '\n'
        digest = hashlib.sha256(catalog_text.encode()).hexdigest()[:16]
        catalog_path = state_dir / ('fireworks-catalog-' + digest + '.json')
        updates.update(model=prepared['model'], model_catalog_json=str(catalog_path), web_search=prepared['web_search'])
    elif provider != 'openai' and provider not in providers:
        raise ValueError('Provider ' + provider + ' is not configured. Grok subscription access requires an existing compatible adapter; this helper never substitutes an xAI API key.')
    if provider == 'grok':
        hostname = urlparse(providers['grok'].get('base_url', '')).hostname or ''
        if hostname == 'x.ai' or hostname.endswith('.x.ai'):
            raise ValueError('The grok provider points to xAI API billing, not the requested subscription adapter; no file changed.')
    if provider != 'fireworks' and data.get('model_provider') == 'fireworks':
        prior = state.get('before_fireworks', state.get('openai', {}))
        for key in ('model_catalog_json', 'web_search'):
            if key not in updates:
                updates[key] = prior.get(key)
    expected = copy.deepcopy(data)
    for key, value in updates.items():
        if value is None:
            expected.pop(key, None)
        else:
            expected[key] = value
    after = edit_root(before, updates)
    if add_provider:
        expected.setdefault('model_providers', {})['fireworks'] = add_provider
        after = append_fireworks(after, add_provider)
    if tomllib.loads(after) != expected:
        raise ValueError('TOML preservation check failed; no file changed.')
    report = {'model': expected.get('model'), 'provider': provider, 'reasoning_effort': expected.get('model_reasoning_effort'), 'changed': after != before, 'dry_run': args.dry_run}
    if prepared:
        report.update(model_id=prepared['model_id'], catalog=str(catalog_path), catalog_source=prepared['source'])
    if args.dry_run or (after == before and (not prepared or catalog_path.exists())):
        print(json.dumps(report, indent=2))
        return
    state_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
    # Serialize writers and reject changes since this invocation read the config.
    with (state_dir / 'lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        if read_exact(path) != before:
            raise ValueError('Config changed during this operation; retry against the current file.')
        if data.get('model_provider', 'openai') == 'openai':
            state['openai'] = {key: data[key] for key in ROOT_KEYS if key in data}
        if provider == 'fireworks' and data.get('model_provider') != 'fireworks':
            state['before_fireworks'] = {key: data[key] for key in ('model_catalog_json', 'web_search') if key in data}
        if prepared:
            atomically_write(catalog_path, catalog_text)
        backup = state_dir / ('config-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ') + '.toml')
        atomically_write(backup, before)
        atomically_write(state_file, json.dumps(state, indent=2) + '\n')
        atomically_write(path, after, stat.S_IMODE(path.stat().st_mode))
    report['backup'] = str(backup)
    report['note'] = 'Default saved. Existing tasks may retain their model. Restart or resume with the selected provider and verify the effective model.'
    print(json.dumps(report, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('target', nargs='*', help='Alias words or exact provider model ID.')
    parser.add_argument('--provider', help='Existing provider ID, or fireworks/openai.')
    parser.add_argument('--effort', choices=EFFORTS)
    parser.add_argument('--config', type=Path, default=Path(os.environ.get('CODEX_HOME', str(Path.home() / '.codex'))) / 'config.toml')
    parser.add_argument('--state-dir', type=Path, help='Override private state/backup directory.')
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--status', action='store_true')
    parser.add_argument('--list', action='store_true', help='List compatible Fireworks serverless models from FireConnect.')
    parser.add_argument('--search', help='Filter --list by model name or ID.')
    args = parser.parse_args()
    try:
        run(args)
    except (ValueError, OSError, KeyError) as exc:
        print('switch-model: ' + str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
