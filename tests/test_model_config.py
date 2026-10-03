"""Credential eligibility, no-network boundaries, startup output, and real UI."""

from copy import deepcopy
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

from streamlit.testing.v1 import AppTest

import compare
import model_config
from openrouter_backend import predict_messages
from refund_demo import QUESTIONS
from test_app import control, edit_contexts, edit_questions, mock_worker, run_app

ROOT = Path(__file__).resolve().parents[1]
ENV = {'OR_TOKEN': 'fixture-openrouter', 'CLOUDFLARE_AUTH_TOKEN': 'fixture-cloudflare',
       'CLOUDFLARE_ACCOUNT_ID': 'a' * 32}
CASES = [{'id': 'private-label', 'message': 'Please refund', 'expected': True}]


class ConfigurationTests(unittest.TestCase):
    def test_every_registered_hosted_backend_has_explicit_requirements(self):
        backends = {s['backend'] for s in compare.MODELS.values() if model_config.is_hosted(s)}
        self.assertEqual(backends, {'openrouter', 'cloudflare'})
        self.assertTrue(all(model_config.PROVIDERS[b].api_keys for b in backends))

    def test_missing_whitespace_and_provider_independence(self):
        local = [k for k, s in compare.MODELS.items() if not model_config.is_hosted(s)]
        for blank in ('', ' ', '\t\r\n'):
            with self.subTest(blank=repr(blank)):
                env = dict.fromkeys(ENV, blank)
                self.assertEqual(model_config.available_model_keys(compare.MODELS, env), local)
                self.assertEqual(model_config.default_model_keys(compare.MODELS, env), local)
        self.assertIn('jev', model_config.default_model_keys(compare.MODELS, {'OR_TOKEN': 'fixture'}))
        cloud = {k: v for k, v in ENV.items() if k.startswith('CLOUDFLARE_')}
        self.assertEqual(model_config.available_model_keys(compare.MODELS, cloud), local + ['clef_flash', 'clef'])
        self.assertEqual(model_config.default_model_keys(compare.MODELS, cloud), local)
        self.assertEqual(model_config.default_model_keys(compare.MODELS, ENV), local + ['jev'])

    def test_unrelated_tokens_unknown_backend_and_local_hf_access(self):
        env = {'CLOUDFLARE_API_TOKEN': 'unrelated', 'BLOG_CF_API_TOKEN': 'blog', 'HF_TOKEN': 'download'}
        self.assertFalse(model_config.provider_eligibility('cloudflare', env).enabled)
        self.assertFalse(model_config.provider_eligibility('openrouter', env).enabled)
        self.assertTrue(model_config.model_eligibility(compare.MODELS['mojev'], {}).enabled)
        self.assertFalse(model_config.model_eligibility({'backend': 'unregistered'}, ENV).enabled)

    def test_account_config_is_distinct_and_invalid_formats_never_leak(self):
        status = model_config.provider_eligibility('cloudflare', {'CLOUDFLARE_AUTH_TOKEN': 'fixture'})
        self.assertEqual(status.missing_api_keys, ())
        self.assertEqual(status.missing_settings, ('CLOUDFLARE_ACCOUNT_ID',))
        env = {**ENV, 'CLOUDFLARE_ACCOUNT_ID': 'private-bad-account', 'OR_TOKEN': 'private\nheader'}
        diagnostic = model_config.startup_diagnostics(compare.MODELS, env)
        self.assertIn('invalid API key format: OR_TOKEN', diagnostic)
        self.assertIn('invalid nonsecret configuration format: CLOUDFLARE_ACCOUNT_ID', diagnostic)
        for value in env.values():
            self.assertNotIn(value, diagnostic)
        self.assertNotIn('private', diagnostic)

    def test_startup_lists_only_registered_providers_and_names(self):
        text = model_config.startup_diagnostics(compare.MODELS, {})
        for name in ('Jev', 'CLEF Flash', 'CLEF', 'OR_TOKEN', 'CLOUDFLARE_AUTH_TOKEN', 'CLOUDFLARE_ACCOUNT_ID'):
            self.assertIn(name, text)
        self.assertIn('missing API keys', text)
        self.assertIn('missing nonsecret configuration', text)
        self.assertIn('optional for local inference', text)
        self.assertIn('opt-in', text)
        local = {k: s for k, s in compare.MODELS.items() if not model_config.is_hosted(s)}
        self.assertNotIn('OR_TOKEN', model_config.startup_diagnostics(local, {}))
        present = model_config.startup_diagnostics(compare.MODELS, ENV)
        self.assertNotIn('missing API keys', present)
        self.assertIn('key validity unverified', present)
        for value in ENV.values():
            self.assertNotIn(value, present)

    def test_print_once_per_process_even_repeated_sessions(self):
        output = io.StringIO()
        with patch.object(model_config, '_startup_pid', None):
            for _ in range(3):
                model_config.print_startup_diagnostics(compare.MODELS, {}, output)
        self.assertEqual(output.getvalue().count('Hosted model configuration'), 1)

    def test_direct_api_and_compare_block_every_unconfigured_hosted_model(self):
        with patch.dict(os.environ, {}, clear=True), patch('compare.predict_messages') as hosted, \
                patch('compare.predict_cloudflare') as cloud, patch('compare.subprocess.run') as worker, \
                patch('openrouter_backend.requests.Session') as network:
            for key, spec in compare.MODELS.items():
                if model_config.is_hosted(spec):
                    rows = compare.run_model(key, CASES)
                    self.assertEqual(rows[0]['status'], 'error')
                    self.assertEqual(rows[0]['execution'], 'hosted')
                    self.assertNotIn('decision', rows[0])
            for value in ('', ' \n\t', 'private\nheader'):
                with patch.dict(os.environ, {'OR_TOKEN': value}):
                    self.assertEqual(predict_messages(['context'], QUESTIONS, 'typesafe/jev-1.13')['results'][0]['status'], 'error')
        hosted.assert_not_called(); cloud.assert_not_called(); worker.assert_not_called(); network.assert_not_called()

    def test_cli_rejects_mixed_selection_before_any_execution_and_stdout_stays_empty(self):
        for key in ('jev', 'clef_flash', 'clef'):
            with self.subTest(key=key), patch.dict(os.environ, {}, clear=True), \
                    patch.object(sys, 'argv', ['compare.py', '--models', 'laya', key]), \
                    patch('compare.run_model') as runner, patch('sys.stdout', new_callable=io.StringIO) as output, \
                    patch('sys.stderr', new_callable=io.StringIO) as error:
                with self.assertRaises(SystemExit) as exit:
                    compare.main()
                self.assertEqual(exit.exception.code, 2)
                self.assertEqual(output.getvalue(), '')
                self.assertIn('Unavailable models', error.getvalue())
                runner.assert_not_called()

    def test_cli_default_is_local_without_keys_and_reports_json(self):
        with patch.dict(os.environ, {}, clear=True), patch.object(sys, 'argv', ['compare.py']), \
                patch('compare.run_model', return_value=[]) as runner, \
                patch('sys.stdout', new_callable=io.StringIO) as output, patch('sys.stderr', new_callable=io.StringIO):
            compare.main()
        data = json.loads(output.getvalue())
        local = [k for k, s in compare.MODELS.items() if not model_config.is_hosted(s)]
        self.assertEqual([c.args[0] for c in runner.call_args_list], local)
        self.assertEqual(list(data['models']), local)

    def test_worker_cannot_treat_hosted_models_as_local_checkpoints(self):
        from model_worker import main
        with patch.dict(os.environ, {}, clear=True), patch.object(sys, 'argv', ['model_worker.py', 'jev']), \
                patch('model_worker.load_model') as loader, patch('sys.stderr', new_callable=io.StringIO) as error:
            with self.assertRaises(SystemExit) as exit:
                main()
        self.assertEqual(exit.exception.code, 2)
        self.assertIn('OR_TOKEN', error.getvalue())
        loader.assert_not_called()

    def test_launcher_prints_before_streamlit_and_forwards_flags(self):
        import serve
        output = io.StringIO()
        def started():
            self.assertIn('OR_TOKEN', output.getvalue())
            self.assertEqual(sys.argv, ['streamlit', 'run', str(ROOT / 'app.py'), '--server.port', '8502'])
        with patch.dict(os.environ, {}, clear=True), patch.object(model_config, '_startup_pid', None), \
                patch('sys.stdout', output), patch.object(sys, 'argv', ['serve.py']), \
                patch('streamlit.web.cli.main', side_effect=started):
            serve.main(['--server.port', '8502'])


class CredentialUITests(unittest.TestCase):
    def app(self):
        app = AppTest.from_file(str(ROOT / 'app.py'), default_timeout=30).run()
        self.assertFalse(app.exception)
        return app

    def test_missing_keys_show_disabled_entries_and_keep_local_models_available(self):
        with patch.dict(os.environ, {}, clear=True), patch('requests.Session') as network, \
                patch('compare.subprocess.run') as worker:
            app = self.app()
            picker = control(app, 'multiselect', 'Run these models')
            self.assertEqual(len(picker.options), 16)
            self.assertEqual(len(picker.value), 16)
            optional = control(app, 'multiselect', 'Optional Cloudflare models')
            self.assertTrue(optional.disabled); self.assertEqual(optional.options, [])
            self.assertEqual(len(app.checkbox), 3)
            self.assertTrue(all(item.disabled and not item.value for item in app.checkbox))
            captions = '\n'.join(item.value for item in app.caption)
            self.assertIn('missing API keys: OR_TOKEN', captions)
            self.assertIn('missing nonsecret configuration: CLOUDFLARE_ACCOUNT_ID', captions)
            self.assertFalse(control(app, 'button', 'Run comparison').disabled)
            picker.set_value([]); run_app(app)
            self.assertTrue(control(app, 'button', 'Run comparison').disabled)
        network.assert_not_called(); worker.assert_not_called()

    def test_present_keys_enable_selection_without_proving_access_and_clef_is_opt_in(self):
        with patch.dict(os.environ, ENV, clear=True), patch('requests.Session') as network:
            app = self.app()
            picker = control(app, 'multiselect', 'Run these models')
            optional = control(app, 'multiselect', 'Optional Cloudflare models')
            self.assertEqual(len(picker.value), 17)
            self.assertEqual(optional.value, [])
            self.assertFalse(optional.disabled); self.assertEqual(len(optional.options), 2)
            self.assertFalse(app.checkbox)
            optional.set_value(['clef_flash']); run_app(app)
            self.assertIn('unverified', '\n'.join(c.value for c in app.caption))
        network.assert_not_called()

    def test_diagnostic_is_not_repeated_by_reruns_or_new_sessions(self):
        output = io.StringIO()
        with patch.dict(os.environ, {}, clear=True), patch.object(model_config, '_startup_pid', None), \
                patch('sys.stdout', output), patch('requests.Session') as network:
            app = self.app()
            run_app(app)
            self.assertFalse(app.exception)
            self.app()
        self.assertEqual(output.getvalue().count('Hosted model configuration'), 1)
        network.assert_not_called()

    def test_removed_credentials_clear_stale_selections_preserve_draft_and_saved_charts(self):
        with patch.dict(os.environ, ENV, clear=True), patch('requests.Session') as network, \
                patch('compare.subprocess.run', side_effect=mock_worker) as runner:
            app = self.app()
            control(app, 'multiselect', 'Run these models').set_value(['laya']); run_app(app)
            edit_questions(app, changes={0: {'instructions': 'My custom question?'}})
            edit_contexts(app, changes={0: {'message': 'My own refund context'}}, deleted=list(range(1, 12)))
            control(app, 'button', 'Run comparison').click(); run_app(app)
            saved = deepcopy(app.session_state.comparison)
            questions = deepcopy(app.session_state.questions_current)
            cases = deepcopy(app.session_state.suite_latest)
            control(app, 'multiselect', 'Run these models').set_value(['laya', 'jev'])
            control(app, 'multiselect', 'Optional Cloudflare models').set_value(['clef_flash']); run_app(app)
            with patch.dict(os.environ, dict.fromkeys(ENV, ' ')):
                run_app(app)
                self.assertFalse(app.exception)
                self.assertEqual(control(app, 'multiselect', 'Run these models').value, ['laya'])
                self.assertEqual(control(app, 'multiselect', 'Optional Cloudflare models').value, [])
                self.assertTrue(control(app, 'multiselect', 'Optional Cloudflare models').disabled)
                self.assertEqual(app.session_state.comparison, saved)
                self.assertEqual(app.session_state.questions_current, questions)
                self.assertEqual(app.session_state.suite_latest, cases)
                self.assertTrue(app.get('vega_lite_chart'))
        self.assertEqual(runner.call_count, 1)
        network.assert_not_called()


if __name__ == '__main__':
    unittest.main()
