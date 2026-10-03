import copy
import json
import os
from pathlib import Path
import unittest
from unittest.mock import Mock, patch

import requests

from cloudflare_backend import API_ROOT, MODEL_SELECTORS, configuration_error, predict_messages
from compare import MODELS, default_model_keys, run_model
from refund_demo import QUESTIONS
from scripts import download_models

ACCOUNT = 'a' * 32
TOKEN = 'fake-clef-token'
CONFIG = {'CLOUDFLARE_ACCOUNT_ID': ACCOUNT, 'CLOUDFLARE_AUTH_TOKEN': TOKEN}
MIXED = {**QUESTIONS, 'route': {'type': 'choice', 'instructions': 'Which team?',
                              'criteria': {'billing': 'Refunds', 'support': 'Product support'}}}


def native(selector='clef-flash', questions=MIXED):
    answers = {}
    for qid, question in questions.items():
        if question['type'] == 'noul':
            answers[qid] = {'type': 'noul', 'noul': .95}
        else:
            answers[qid] = {'type': 'choice', 'choice': 'billing',
                            'probabilities': {'billing': .9, 'support': .1}, 'confidence': .8}
    return {'model': selector, 'answers': answers, 'usage': {'input_tokens': 120, 'output_tokens': 0}}


def response(raw, status=200, success=True, errors=None):
    return Mock(status_code=status, text=json.dumps(
        {'success': success, 'errors': errors or [], 'messages': [], 'result': raw}))


class CloudflareTests(unittest.TestCase):
    def test_missing_configuration_never_uses_other_tokens_or_network(self):
        with patch.dict(os.environ, {'CLOUDFLARE_API_TOKEN': 'unrelated', 'BLOG_CF_API_TOKEN': 'blog'}, clear=True), \
                patch('cloudflare_backend.requests.Session') as factory:
            packet = predict_messages(['one', 'two'], QUESTIONS, '@cf/cloudflare/clef')
        factory.assert_not_called()
        self.assertEqual(len(packet['results']), 2)
        self.assertTrue(all(r['status'] == 'error' for r in packet['results']))
        self.assertIn('CLOUDFLARE_ACCOUNT_ID', packet['results'][0]['error'])
        self.assertIn('CLOUDFLARE_AUTH_TOKEN', packet['results'][0]['error'])

    def test_partial_and_malformed_account_configuration_stays_local(self):
        for env in ({'CLOUDFLARE_AUTH_TOKEN': TOKEN}, {'CLOUDFLARE_ACCOUNT_ID': ACCOUNT},
                    {**CONFIG, 'CLOUDFLARE_ACCOUNT_ID': 'x/ai/run/other'},
                    {**CONFIG, 'CLOUDFLARE_AUTH_TOKEN': 'secret\ninjection'}):
            with self.subTest(env=list(env)), patch.dict(os.environ, env, clear=True), \
                    patch('cloudflare_backend.requests.Session') as factory:
                self.assertTrue(configuration_error())
                packet = predict_messages(['one'], QUESTIONS, '@cf/cloudflare/clef')
            factory.assert_not_called()
            self.assertEqual(packet['results'][0]['status'], 'error')
            self.assertNotIn(TOKEN, json.dumps(packet))

    def test_both_exact_native_model_routes_and_request_contract(self):
        for model, selector in MODEL_SELECTORS.items():
            with self.subTest(model=model), patch.dict(os.environ, CONFIG, clear=True), \
                    patch('cloudflare_backend.requests.Session') as factory:
                session = factory.return_value.__enter__.return_value
                raw = native(selector)
                session.post.return_value = response(raw)
                packet = predict_messages(['Refund my shoes'], MIXED, model)
            call = session.post.call_args
            self.assertEqual(call.args[0], f'{API_ROOT}/accounts/{ACCOUNT}/ai/run/{model}')
            self.assertEqual(call.kwargs['json'], {'model': selector, 'state': 'Refund my shoes', 'questions': MIXED})
            self.assertFalse(call.kwargs['allow_redirects'])
            self.assertEqual(call.kwargs['timeout'], (10, 60))
            self.assertEqual(packet['results'][0]['raw_response'], raw)
            self.assertEqual(packet['results'][0]['api_response']['result'], raw)
            self.assertIsNone(packet['results'][0]['cost_usd'])
            self.assertNotIn(TOKEN, json.dumps(packet))

    def test_compare_rows_preserve_decisions_usage_and_local_labels(self):
        cases = [{'id': 'private-id', 'message': 'Refund my shoes',
                  'expected_answers': {'refund_requested': True, 'route': 'billing'}}]
        with patch.dict(os.environ, CONFIG, clear=True), patch('cloudflare_backend.requests.Session') as factory, \
                patch('compare.subprocess.run') as worker:
            session = factory.return_value.__enter__.return_value
            session.post.return_value = response(native())
            rows = run_model('clef_flash', cases, questions=MIXED)
        worker.assert_not_called()
        self.assertEqual(len(rows), 2)
        self.assertTrue(all(r['status'] == 'ok' and r['correct'] and r['execution'] == 'hosted' for r in rows))
        self.assertEqual(rows[0]['probability_yes'], .95)
        self.assertEqual(rows[1]['probabilities'], {'billing': .9, 'support': .1})
        self.assertEqual(rows[1]['returned_confidence'], .8)
        self.assertEqual(rows[0]['raw_response']['usage']['input_tokens'], 120)
        self.assertNotIn('private-id', json.dumps(session.post.call_args.kwargs['json']))
        self.assertNotIn('expected_answers', json.dumps(session.post.call_args.kwargs['json']))
        self.assertEqual(session.post.call_count, 1)

    def test_invalid_schemas_and_unknown_model_never_call_network(self):
        oversized = {f'q{i}': {'type': 'noul', 'instructions': 'Yes?'} for i in range(65)}
        invalids = [({}, '@cf/cloudflare/clef'), (oversized, '@cf/cloudflare/clef'),
                    ({'bad id': {'type': 'noul', 'instructions': 'Yes?'}}, '@cf/cloudflare/clef'),
                    ({'x' * 101: {'type': 'noul', 'instructions': 'Yes?'}}, '@cf/cloudflare/clef'),
                    ({'q': {'type': 'score', 'instructions': 'Severity?', 'criteria': ['low', 'high']}}, '@cf/cloudflare/clef'),
                    ({'q': {'type': 'choice', 'instructions': 'Pick', 'criteria': {'one': 'only'}}}, '@cf/cloudflare/clef'),
                    (QUESTIONS, '@cf/cloudflare/wrong')]
        for questions, model in invalids:
            with self.subTest(model=model, ids=list(questions)[:1]), patch.dict(os.environ, CONFIG, clear=True), \
                    patch('cloudflare_backend.requests.Session') as factory:
                packet = predict_messages(['one'], questions, model)
            factory.assert_not_called()
            self.assertEqual(packet['results'][0]['status'], 'error')

    def test_invalid_answers_are_errors_not_votes(self):
        valid = native()
        corruptions = []
        for field, value in [('model', 'clef'), ('answers', {}), ('usage', {'input_tokens': True, 'output_tokens': 0})]:
            raw = copy.deepcopy(valid); raw[field] = value; corruptions.append(raw)
        for field, value in [('type', 'choice'), ('noul', True), ('noul', '0.95'), ('noul', float('nan')), ('noul', 1.01)]:
            raw = copy.deepcopy(valid); raw['answers']['refund_requested'][field] = value; corruptions.append(raw)
        for field, value in [('choice', 'unknown'), ('choice', 'support'), ('confidence', None),
                             ('probabilities', {'billing': .3, 'support': .1}),
                             ('probabilities', {'billing': .9, 'other': .1})]:
            raw = copy.deepcopy(valid); raw['answers']['route'][field] = value; corruptions.append(raw)
        for raw in corruptions:
            with self.subTest(raw=raw), patch.dict(os.environ, CONFIG, clear=True), \
                    patch('cloudflare_backend.requests.Session') as factory:
                factory.return_value.__enter__.return_value.post.return_value = response(raw)
                packet = predict_messages(['one'], MIXED, '@cf/cloudflare/clef-flash')
            self.assertEqual(packet['results'][0]['status'], 'error')
            self.assertNotIn('raw_response', packet['results'][0])

    def test_upstream_errors_timeouts_redirects_and_redaction_no_retries(self):
        denied = response(None, 403, False, [{'code': 10000, 'message': f'Unauthorized {TOKEN}'}])
        success_echo = native(); success_echo['extra'] = TOKEN
        with patch.dict(os.environ, CONFIG, clear=True), patch('cloudflare_backend.requests.Session') as factory:
            session = factory.return_value.__enter__.return_value
            session.post.side_effect = [denied, requests.Timeout(), requests.ConnectionError(),
                                        Mock(status_code=302, text='redirect'),
                                        Mock(status_code=200, text='[]'), response(success_echo)]
            packet = predict_messages(['one'] * 6, MIXED, '@cf/cloudflare/clef-flash')
        self.assertEqual(session.post.call_count, 6)
        self.assertEqual([r['status'] for r in packet['results']], ['error'] * 5 + ['ok'])
        self.assertNotIn(TOKEN, json.dumps(packet))
        self.assertIn('[REDACTED]', packet['results'][0]['error'])
        self.assertIn('No automatic retry', packet['results'][1]['error'])

    def test_new_models_are_opt_in_and_existing_defaults_are_preserved(self):
        with patch.dict(os.environ, {'OR_TOKEN': 'fixture-key'}, clear=True):
            self.assertEqual(default_model_keys(), [key for key in MODELS if key not in {'clef', 'clef_flash'}])
        self.assertEqual(MODELS['clef']['repo'], '@cf/cloudflare/clef')
        self.assertEqual(MODELS['clef_flash']['repo'], '@cf/cloudflare/clef-flash')

    def test_hosted_model_selection_is_skipped_by_downloader(self):
        with patch('sys.argv', ['download_models.py', 'clef', 'clef_flash', 'jev']), \
                patch('scripts.download_models.download') as download:
            download_models.main()
        download.assert_not_called()



if __name__ == '__main__':
    unittest.main()
