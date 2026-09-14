import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
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
models = ['kimi-k3', 'glm-5p3', 'deepseek-v4p1-flash', 'new-model-99', 'minimax-m3', 'kimi-latest', 'kimi-fast-latest', 'glm-latest', 'glm-fast-latest', 'glm-flash-latest', 'deepseek-flash-latest', 'deepseek-pro-latest']
if sys.argv[1] == 'model':
    print(json.dumps({'source': 'network', 'models': [{'id': 'accounts/fireworks/' + ('routers/' if name.endswith('-latest') else 'models/') + name, 'shortId': name, 'displayName': name, 'kind': 'serverless', 'toolCalling': True, 'maxInputTokens': 100000} for name in models]}))
else:
    folder = pathlib.Path(sys.argv[-2]) / '.codex'
    slug = sys.argv[-1].split('/')[-1]
    config = 'model = ' + json.dumps(slug) + '\nmodel_provider = "fireworks-ai"\nweb_search = "disabled"\nmodel_catalog_json = "fireworks-model-catalog.json"\n[model_providers.fireworks-ai]\nbase_url = "https://api.fireworks.ai/inference/v1"\nwire_api = "responses"\nexperimental_bearer_token = ' + json.dumps(os.environ['FIREWORKS_API_KEY']) + '\n'
    (folder / 'config.toml').write_text(config)
    catalog = {'models': [{'slug': name, 'context_window': 100000, 'default_reasoning_level': 'high', 'supported_reasoning_levels': [{'effort': 'low'}, {'effort': 'medium'}, {'effort': 'high'}]} for name in models]}
    if os.environ.get('FAKE_CATALOG_FAILURE'):
        catalog = {'models': []}
    (folder / 'fireworks-model-catalog.json').write_text(json.dumps(catalog))
""")
        fixture.chmod(0o700)
        source = self.root / 'source/packages/setup-cli/lib/harnesses/codex'
        source.mkdir(parents=True)
        (source / 'catalog.mjs').touch()
        self.env = os.environ | {'FIREWORKS_API_KEY': 'test-only-never-sent', 'CODEX_HOME': str(self.root),
                                 'FIRECONNECT_BIN': str(fixture), 'FIRECONNECT_NODE': str(fixture),
                                 'FIRECONNECT_SOURCE': str(self.root / 'source')}


    def run_switch(self, *args, succeeds=True):
        result = subprocess.run([sys.executable, str(SCRIPT), '--config', str(self.config), *args], env=self.env, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0 if succeeds else 1, result.stderr)
        return json.loads(result.stdout) if succeeds else result.stderr

    def data(self):
        return tomllib.loads(self.config.read_text())

    def test_fireworks_preserves_unrelated_config_and_backups(self):
        report = self.run_switch('kimi', 'k3')
        data = self.data()
        self.assertEqual(data['model'], 'kimi-k3')
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

    def test_family_aliases_use_latest_and_versions_remain_pinned(self):
        self.run_switch('kimi')
        self.assertEqual(self.data()['model'], 'kimi-latest')
        self.run_switch('kimi', 'k3')
        self.assertEqual(self.data()['model'], 'kimi-k3')
        self.run_switch('glm', 'flash')
        self.assertEqual(self.data()['model'], 'glm-flash-latest')
        self.run_switch('deepseek', 'pro')
        self.assertEqual(self.data()['model'], 'deepseek-pro-latest')
        self.run_switch('--effort', 'ultra', 'kimi', succeeds=False)
        self.assertEqual(self.data()['model'], 'deepseek-pro-latest')

    def test_dynamic_model_and_catalog_are_usable(self):
        listing = self.run_switch('--list', '--search', 'new model')
        self.assertEqual([m['id'] for m in listing['models']], ['accounts/fireworks/models/new-model-99'])
        self.run_switch('new-model-99')
        catalog = json.loads(Path(self.data()['model_catalog_json']).read_text())
        self.assertIn('new-model-99', [m['slug'] for m in catalog['models']])
        self.assertNotIn('minimax-m3', [m['slug'] for m in catalog['models']])
        self.assertEqual(self.data()['web_search'], 'disabled')

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
