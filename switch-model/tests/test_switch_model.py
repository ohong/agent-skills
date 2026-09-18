import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import tomllib
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/switch_model.py'
AUTH = SCRIPT.with_name('fireworks_auth.py')
ORIGINAL = '''# Personal setup
model = "gpt-6-astra" # Keep this comment
model_provider = "openai"
model_reasoning_effort = "low"
service_tier = "fast"

[features.context_management]
experimental_mode = true

[model_providers.grok]
name = "Grok"
base_url = "http://127.0.0.1:47891/v1"
wire_api = "responses"

[model_providers.grok.auth]
command = "/private/subscription-login"
refresh_interval_ms = 300000

[mcp_servers.example]
command = "tool"
args = ["--option"]
'''


class ProbeHandler(BaseHTTPRequestHandler):
    """Fake Fireworks Responses endpoint used to test generic-model validation."""

    def do_POST(self):
        failure = self.server.failure
        status = 400 if failure else 200
        body = json.dumps({'error': {'message': failure}} if failure else {}).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *_args):
        pass


class SwitchingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.config = self.root / 'config.toml'
        self.config.write_text(ORIGINAL)
        self.config.chmod(0o640)
        fixture = self.root / 'fake_fireconnect.py'
        fixture.write_text(r"""#!/usr/bin/env python3
import json, os, pathlib, sys
# Mirrors FireConnect: `model list` shows every serverless id, the Codex catalog keeps one latest per family.
LATEST = ['deepseek-flash-latest', 'deepseek-pro-latest', 'glm-5p2-fast-us', 'glm-5p3-flash-us', 'glm-fast-latest', 'glm-flash-latest', 'glm-latest', 'kimi-fast-latest', 'kimi-k3-us', 'kimi-latest', 'new-family-latest', 'minimax-latest']
PINNED = ['kimi-k3', 'glm-5p3', 'deepseek-v4p1-flash', 'minimax-m3']


def rows(names):
    return [{'id': 'accounts/fireworks/' + ('routers/' if name.endswith('-latest') else 'models/') + name,
             'shortId': name, 'displayName': name, 'kind': 'serverless', 'toolCalling': True,
             'maxInputTokens': 100000, 'pricing': {'display': '$1 / $2'}} for name in names]


if sys.argv[1] == 'model':
    print(json.dumps({'source': 'network', 'models': rows(LATEST + PINNED)}))
else:
    args = sys.argv[2:]
    def flag(name):
        return args[args.index(name) + 1] if name in args else None
    home = pathlib.Path(flag('--home'))
    config = pathlib.Path(flag('--config-path'))
    config.parent.mkdir(parents=True, exist_ok=True)
    reference = (flag('--model') or '').split('/')[-1]
    config.write_text('model = ' + json.dumps(reference) + '\nmodel_provider = "fireworks-ai"\nweb_search = "disabled"\n'
                      'model_catalog_json = "fireworks-model-catalog.json"\n[model_providers.fireworks-ai]\n'
                      'base_url = "https://api.fireworks.ai/inference/v1"\nwire_api = "responses"\n'
                      'experimental_bearer_token = ' + json.dumps(os.environ['FIREWORKS_API_KEY']) + '\n')
    slugs = [] if os.environ.get('FAKE_CATALOG_FAILURE') else [n for n in LATEST if n != 'minimax-latest']
    catalog = {'models': [{'slug': name, 'context_window': 100000, 'default_reasoning_level': 'high',
                           'supported_reasoning_levels': [{'effort': 'low'}, {'effort': 'medium'},
                                                          {'effort': 'high'}]} for name in slugs]}
    (home / '.codex').mkdir(parents=True, exist_ok=True)
    (home / '.codex/fireworks-model-catalog.json').write_text(json.dumps(catalog))
""")
        fixture.chmod(0o700)
        models = self.root / 'fireworks-models.json'
        models.write_text(json.dumps({'data': [
            {'id': 'accounts/fireworks/models/qwen3p8-max', 'supports_chat': True, 'supports_tools': True,
             'supports_image_input': True, 'context_length': 262144},
            {'id': 'accounts/fireworks/models/nemotron-lightning-3p5-30b-a3b', 'supports_chat': True,
             'supports_tools': True, 'supports_image_input': False},
            {'id': 'accounts/fireworks/models/glm-5p2', 'supports_chat': True, 'supports_tools': True,
             'context_length': 1048576},
            {'id': 'accounts/fireworks/models/plain-text-only', 'supports_chat': True, 'supports_tools': False},
        ]}))
        self.probe = ThreadingHTTPServer(('127.0.0.1', 0), ProbeHandler)
        self.probe.failure = None
        threading.Thread(target=self.probe.serve_forever, kwargs={'poll_interval': 0.01}, daemon=True).start()
        self.addCleanup(self.probe.shutdown)
        self.addCleanup(self.probe.server_close)
        self.env = os.environ | {'FIREWORKS_API_KEY': 'test-only-never-sent', 'CODEX_HOME': str(self.root),
                                 'FIRECONNECT_BIN': str(fixture), 'FIREWORKS_MODELS_URL': models.as_uri(),
                                 'FIREWORKS_RESPONSES_URL': 'http://127.0.0.1:%d/responses' % self.probe.server_address[1]}


    def run_switch(self, *args, succeeds=True):
        result = subprocess.run([sys.executable, str(SCRIPT), '--config', str(self.config), *args], env=self.env, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0 if succeeds else 1, result.stderr)
        return json.loads(result.stdout) if succeeds else result.stderr

    def data(self):
        return tomllib.loads(self.config.read_text())

    def test_fireworks_preserves_unrelated_config_and_backups(self):
        report = self.run_switch('kimi')
        data = self.data()
        self.assertEqual(data['model'], 'kimi-latest')
        self.assertEqual(data['model_reasoning_effort'], 'high')
        self.assertEqual(data['model_providers']['grok'], tomllib.loads(ORIGINAL)['model_providers']['grok'])
        self.assertIn('# Keep this comment', self.config.read_text())
        self.assertIn(ORIGINAL[ORIGINAL.index('[features.context_management]'):], self.config.read_text())
        self.assertEqual(Path(report['backup']).read_text(), ORIGINAL)
        self.assertEqual(Path(report['backup']).stat().st_mode & 0o777, 0o600)
        self.assertEqual(self.config.stat().st_mode & 0o777, 0o640)
        self.assertNotIn('test-only-never-sent', self.config.read_text())

    def test_switch_back_restores_original_gpt_settings(self):
        self.run_switch('kimi')
        self.run_switch('deepseek')
        self.run_switch('gpt')
        for key in ('model', 'model_provider', 'model_reasoning_effort'):
            self.assertEqual(self.data()[key], tomllib.loads(ORIGINAL)[key])

    def test_absent_original_settings_remain_absent_on_restore(self):
        self.config.write_text('model = "gpt-6-astra"\n[unrelated]\nkeep = true\n')
        self.run_switch('kimi')
        self.run_switch('gpt')
        self.assertNotIn('model_reasoning_effort', self.data())
        self.assertNotIn('model_provider', self.data())

    def test_existing_subscription_provider_is_unchanged(self):
        before = self.data()['model_providers']['grok']
        self.run_switch('grok')
        self.assertEqual(self.data()['model_providers']['grok'], before)
        self.assertEqual(self.data()['model_reasoning_effort'], 'high')

    def test_arbitrary_configured_provider_and_explicit_effort(self):
        self.config.write_text(ORIGINAL + '\n[model_providers.custom]\nname="Custom"\nwire_api="responses"\n')
        self.run_switch('--provider', 'custom', '--effort', 'medium', 'vendor/new-model:2026')
        self.assertEqual(self.data()['model'], 'vendor/new-model:2026')
        self.assertEqual(self.data()['model_reasoning_effort'], 'medium')

    def test_dry_run_never_writes(self):
        self.run_switch('--dry-run', 'glm')
        self.assertEqual(self.config.read_text(), ORIGINAL)
        self.assertFalse((self.root / 'switch-model').exists())

    def test_missing_provider_unknown_alias_invalid_toml_never_write(self):
        for args in [('invented',), ('--provider', 'absent', 'vendor/model')]:
            self.run_switch(*args, succeeds=False)
            self.assertEqual(self.config.read_text(), ORIGINAL)
        invalid = 'model = "a"\nmodel = "b"\n'
        self.config.write_text(invalid)
        self.run_switch('kimi', succeeds=False)
        self.assertEqual(self.config.read_text(), invalid)

    def test_conflicting_fireworks_endpoint_never_overwritten(self):
        before = ORIGINAL + '\n[model_providers.fireworks]\nbase_url="http://custom"\nwire_api="responses"\n'
        self.config.write_text(before)
        self.run_switch('kimi', succeeds=False)
        self.assertEqual(self.config.read_text(), before)

    def test_multiline_lookalike_fails_without_corrupting_config(self):
        before = '''note = """
model = "fake"
"""
model = "gpt-real"
'''
        self.config.write_text(before)
        self.run_switch('kimi', succeeds=False)
        self.assertEqual(self.config.read_text(), before)

    def test_grok_api_billing_is_not_a_subscription(self):
        before = ORIGINAL.replace('http://127.0.0.1:47891/v1', 'https://api.x.ai/v1')
        self.config.write_text(before)
        self.run_switch('grok', succeeds=False)
        self.assertEqual(self.config.read_text(), before)

    def test_crlf_backup_keeps_original_bytes(self):
        original_bytes = ORIGINAL.replace('\n', '\r\n').encode()
        self.config.write_bytes(original_bytes)
        report = self.run_switch('kimi')
        self.assertEqual(Path(report['backup']).read_bytes(), original_bytes)
        self.assertIn(b'# Keep this comment\r\n', self.config.read_bytes())

    def test_idempotent_switch(self):
        self.run_switch('kimi')
        report = self.run_switch('kimi')
        self.assertFalse(report['changed'])

    def test_any_serverless_model_switches_with_generic_catalog_entry(self):
        report = self.run_switch('qwen3p8-max')
        full = 'accounts/fireworks/models/qwen3p8-max'
        self.assertEqual(self.data()['model'], full)
        self.assertEqual(report['catalog_source'], 'fireworks-generic')
        catalog = json.loads(Path(self.data()['model_catalog_json']).read_text())
        entry = next(m for m in catalog['models'] if m['slug'] == full)
        self.assertEqual(entry['context_window'], 262144)
        self.assertEqual(entry['input_modalities'], ['text', 'image'])
        self.assertEqual([l['effort'] for l in entry['supported_reasoning_levels']], ['low', 'medium', 'high'])
        self.run_switch('accounts/fireworks/models/nemotron-lightning-3p5-30b-a3b')
        catalog = json.loads(Path(self.data()['model_catalog_json']).read_text())
        entry = next(m for m in catalog['models'] if m['slug'].endswith('nemotron-lightning-3p5-30b-a3b'))
        self.assertEqual(entry['context_window'], 65536)
        self.assertEqual(entry['input_modalities'], ['text'])

    def test_validation_probe_rejects_broken_generic_models(self):
        self.probe.failure = 'jinja template rendering failed. Unexpected message role.'
        self.run_switch('qwen3p8-max', succeeds=False)
        self.assertEqual(self.config.read_text(), ORIGINAL)
        self.probe.failure = None
        report = self.run_switch('--dry-run', 'qwen3p8-max')
        self.assertEqual(report['model'], 'accounts/fireworks/models/qwen3p8-max')

    def test_generic_models_keep_pinned_versions_selectable(self):
        self.run_switch('glm-5p2')
        self.assertEqual(self.data()['model'], 'accounts/fireworks/models/glm-5p2')

    def test_unsupported_or_unknown_models_fail_without_writes(self):
        for target in ('plain-text-only', 'not-a-fireworks-model'):
            self.run_switch(target, succeeds=False)
        self.assertEqual(self.config.read_text(), ORIGINAL)

    def test_list_marks_curated_and_generic_serverless_models(self):
        rows = self.run_switch('--list')['models']
        by_id = {row['short_id']: row for row in rows}
        self.assertTrue(by_id['kimi-latest']['in_codex_catalog'])
        self.assertFalse(by_id['qwen3p8-max']['in_codex_catalog'])
        self.assertNotIn('plain-text-only', by_id)
        found = self.run_switch('--list', '--search', 'qwen')['models']
        self.assertEqual([row['short_id'] for row in found], ['qwen3p8-max'])

    def test_kimi_switch_warns_about_desktop_only_schema_failure(self):
        report = self.run_switch('kimi')
        self.assertIn('desktop', report['warning'])
        self.assertIn('$ref', report['warning'])
        report = self.run_switch('deepseek')
        self.assertNotIn('warning', report)
        report = self.run_switch('--dry-run', 'glm')
        self.assertNotIn('warning', report)

    def test_family_aliases_use_the_latest_router_only(self):
        self.run_switch('kimi')
        self.assertEqual(self.data()['model'], 'kimi-latest')
        self.run_switch('kimi', 'fast')
        self.assertEqual(self.data()['model'], 'kimi-fast-latest')
        self.run_switch('glm', 'flash')
        self.assertEqual(self.data()['model'], 'glm-flash-latest')
        self.run_switch('deepseek', 'pro')
        self.assertEqual(self.data()['model'], 'deepseek-pro-latest')
        all_models = self.run_switch('--list')['models']
        self.assertEqual([row['short_id'] for row in all_models if 'deepseek' in row['short_id']],
                         ['deepseek-flash-latest', 'deepseek-pro-latest'])
        self.run_switch('--effort', 'max', 'kimi')
        self.assertEqual(self.data()['model_reasoning_effort'], 'max')
        self.run_switch('--effort', 'ultra', 'kimi', succeeds=False)
        self.assertEqual(self.data()['model'], 'kimi-latest')

    def test_catalog_holds_one_latest_entry_per_family(self):
        listing = self.run_switch('--list', '--search', 'new family')
        self.assertEqual([row['short_id'] for row in listing['models']], ['new-family-latest'])
        self.run_switch('new-family-latest')
        catalog = json.loads(Path(self.data()['model_catalog_json']).read_text())
        slugs = [m['slug'] for m in catalog['models']]
        self.assertIn('new-family-latest', slugs)
        self.assertNotIn('minimax-latest', slugs)
        self.assertNotIn('kimi-k3', slugs)
        self.assertNotIn('deepseek-v4p1-flash', slugs)
        self.assertEqual(self.data()['web_search'], 'disabled')

    def test_deep_tier_is_restored_when_fireconnect_omits_it(self):
        self.run_switch('kimi')
        catalog = json.loads(Path(self.data()['model_catalog_json']).read_text())
        levels = {m['slug']: [l['effort'] for l in m['supported_reasoning_levels']] for m in catalog['models']}
        self.assertEqual(levels['kimi-latest'], ['low', 'medium', 'high', 'max'])
        self.assertEqual(levels['glm-latest'], ['low', 'medium', 'high', 'max'])
        self.assertEqual(levels['deepseek-pro-latest'], ['low', 'medium', 'high', 'max'])
        self.assertEqual(levels['new-family-latest'], ['low', 'medium', 'high'])

    def test_restore_catalog_search_and_intervening_edits(self):
        self.config.write_text('model_catalog_json = "/old/catalog.json"\nweb_search = "live"\n' + ORIGINAL)
        self.run_switch('kimi')
        self.config.write_text(self.config.read_text().replace('service_tier = "fast"', 'service_tier = "default"'))
        self.run_switch('grok')
        self.assertEqual(self.data()['model_catalog_json'], '/old/catalog.json')
        self.assertEqual(self.data()['web_search'], 'live')
        self.run_switch('gpt')
        self.assertEqual(self.data()['model_catalog_json'], '/old/catalog.json')
        self.assertEqual(self.data()['service_tier'], 'default')

    def test_incompatible_or_missing_metadata_never_writes(self):
        self.run_switch('minimax-m3', succeeds=False)
        self.assertEqual(self.config.read_text(), ORIGINAL)
        # A pinned id resolves in FireConnect's list but is absent from its Codex catalog.
        self.run_switch('kimi', 'k3', succeeds=False)
        self.assertEqual(self.config.read_text(), ORIGINAL)
        self.env['FAKE_CATALOG_FAILURE'] = '1'
        self.run_switch('kimi', succeeds=False)
        self.assertEqual(self.config.read_text(), ORIGINAL)

    def test_key_reader_does_not_reveal_secret_on_check(self):
        result = subprocess.run([sys.executable, str(AUTH), '--check'], env=self.env, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertNotIn(self.env['FIREWORKS_API_KEY'], result.stdout + result.stderr)

    def test_key_reader_rejects_broad_permissions(self):
        key = self.root / 'key'
        key.write_text('fake-test-key')
        key.chmod(0o644)
        env = self.env | {'FIREWORKS_API_KEY': '', 'FIREWORKS_API_KEY_FILE': str(key)}
        result = subprocess.run([sys.executable, str(AUTH), '--check'], env=env, capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn('fake-test-key', result.stdout + result.stderr)
        key.chmod(0o600)
        result = subprocess.run([sys.executable, str(AUTH), '--check'], env=env, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)


if __name__ == '__main__':
    unittest.main()
