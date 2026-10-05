"""Focused log-loss scoring/export checks and one saved-run UI smoke; no inference."""

from copy import deepcopy
import json
import math
from pathlib import Path
import unittest
from unittest.mock import patch

from compare import MODELS, add_log_loss, log_loss_fields, report, summarize
from results_charts import log_loss_data, log_loss_spec, runtime_color

ROOT = Path(__file__).resolve().parents[1]


def binary(probability=.8, expected=True, key='laya', case='one', **extra):
    decision = probability >= .5
    return {'model_key': key, 'name': MODELS[key]['name'], 'case_id': case,
            'question_id': 'refund_requested', 'question_type': 'noul', 'status': 'ok',
            'expected': expected, 'probability_yes': probability, 'decision': decision,
            'correct': None if expected is None else decision == expected, **extra}


def choice(probability=.8, expected='refund', **extra):
    row = binary(**extra)
    row.update(question_type='choice', expected=expected, decision='refund',
               probabilities={'refund': probability, 'other': 1 - probability},
               correct=None if expected is None else expected == 'refund')
    return row


class LogLossTests(unittest.TestCase):
    def test_correct_and_wrong_binary_and_choice_use_truth_probability(self):
        for row, truth_probability in [(binary(.8, True), .8), (binary(.8, False), .2),
                                       (choice(.8, 'refund'), .8), (choice(.8, 'other'), .2)]:
            with self.subTest(row=row):
                loss = log_loss_fields([row])
                self.assertAlmostEqual(loss['log_loss'], -math.log(truth_probability))
                self.assertEqual(loss['log_loss_status'], 'finite')
                self.assertEqual(loss['log_loss_scored'], 1)

    def test_zero_and_one_are_exact_without_clipping(self):
        for row in [binary(1, True), binary(0, False), choice(1, 'refund'), choice(0, 'other')]:
            self.assertEqual(log_loss_fields([row])['log_loss'], 0)
        for row in [binary(0, True), binary(1, False), choice(0, 'refund'), choice(1, 'other')]:
            loss = log_loss_fields([row])
            self.assertIsNone(loss['log_loss'])
            self.assertEqual(loss['log_loss_status'], 'infinite')
            self.assertEqual(loss['log_loss_zero_probability_count'], 1)
            self.assertEqual(loss['log_loss_scored'], 1)
            json.dumps(loss, allow_nan=False)

    def test_failures_unlabelled_missing_and_invalid_are_unavailable(self):
        missing = binary(); missing.pop('probability_yes')
        missing_choice = choice(); missing_choice['probabilities'] = {}
        rows = [binary(status='error'), binary(expected=None), missing,
                binary(probability_yes=True), binary(probability_yes=float('nan')),
                binary(question_type='unsupported'), missing_choice]
        for row in rows:
            with self.subTest(row=row):
                loss = log_loss_fields([row])
                self.assertIsNone(loss['log_loss'])
                self.assertEqual(loss['log_loss_status'], 'unavailable')
                self.assertEqual(loss['log_loss_scored'], 0)
        self.assertEqual(log_loss_fields([])['log_loss_status'], 'unavailable')

    def test_mean_denominators_and_existing_scores_stay_separate(self):
        rows = [binary(.8, True), binary(.8, False, case='two'),
                binary(status='error', case='failed'), binary(expected=None, case='unlabelled')]
        summary = summarize(rows)[0]
        self.assertAlmostEqual(summary['log_loss'], (-math.log(.8) - math.log(.2)) / 2)
        self.assertEqual(summary['log_loss_scored'], 2)
        self.assertAlmostEqual(summary['brier_score'], (.04 + .64) / 2)
        self.assertEqual(summary['accuracy_on_answered'], .5)
        self.assertEqual(summary['correct_over_labelled'], 1/3)
        self.assertEqual(summary['coverage'], 3/4)
        mixed = log_loss_fields([rows[0], binary(0, True)])
        self.assertEqual((mixed['log_loss_status'], mixed['log_loss_scored']), ('infinite', 2))

    def test_new_and_legacy_exports_round_trip_and_preserve_inputs(self):
        legacy = binary(0, True); legacy.pop('question_type'); legacy.pop('question_id')
        source = {'created_at': 'original timestamp', 'cases': [], 'results': [legacy]}
        before = deepcopy(source)
        exported = add_log_loss(source)
        self.assertEqual(source, before)
        reloaded = json.loads(json.dumps(exported, allow_nan=False))
        self.assertEqual(reloaded['created_at'], 'original timestamp')
        self.assertEqual(reloaded['results'][0]['log_loss_status'], 'infinite')
        self.assertIsNone(reloaded['summary'][0]['log_loss'])
        self.assertEqual(reloaded['question_summaries']['refund_requested'][0]['log_loss_zero_probability_count'], 1)
        self.assertEqual(add_log_loss(reloaded), reloaded)
        questions = {'q': {'type': 'choice', 'instructions': 'Request?',
                           'criteria': {'refund': 'Money back', 'other': 'Another request'}}}
        new = report([{'id': 'one', 'message': 'Refund', 'expected_answers': {'q': 'other'}}],
                     ['laya'], [choice(1, 'other', question_id='q')], questions)
        self.assertEqual(new['question_summaries']['q'][0]['log_loss_status'], 'infinite')
        json.dumps(new, allow_nan=False)

    def test_saved_scores_chart_sort_colors_and_one_hot_outputs(self):
        saved = json.loads((ROOT / 'results/2026-10-03/comparison.json').read_text())
        before = deepcopy(saved)
        data = add_log_loss(saved)
        rows = {row['model_key']: row for row in data['results']}
        self.assertEqual([r['probabilities'] for r in data['results']],
                         [r['probabilities'] for r in saved['results']])
        self.assertEqual(rows['jev']['log_loss'], 0)
        scores = log_loss_data(data['results'])
        self.assertEqual(len(scores), 19)
        self.assertEqual(scores[0]['Model'], MODELS['jev']['name'])
        self.assertEqual(scores[-1]['Model'], MODELS['fragment2']['name'])
        self.assertEqual(scores[-1]['Status'], 'infinite')
        self.assertEqual(scores[-1]['Zero-probability truths'], 1)
        finite = [v['Value'] for v in scores if v['Status'] == 'finite']
        self.assertEqual(finite, sorted(finite))
        spec = log_loss_spec(scores)
        self.assertEqual(spec['encoding']['color'], runtime_color())
        json.dumps(spec, allow_nan=False)
        self.assertEqual(saved, before)
        self.assertEqual(log_loss_data([binary(expected=None)]), [])

    def test_saved_run_ui_smoke_without_execution_or_draft_changes(self):
        from streamlit.testing.v1 import AppTest
        from test_app import control, run_app
        saved = json.loads((ROOT / 'results/2026-10-03/comparison.json').read_text())
        with patch('compare.run_model', side_effect=AssertionError('Inference forbidden')) as runner, \
                patch('requests.sessions.Session.request', side_effect=AssertionError('API forbidden')) as api:
            app = AppTest.from_file(str(ROOT / 'app.py'), default_timeout=30).run()
            draft = deepcopy(app.session_state.suite_latest)
            app.session_state['comparison'] = deepcopy(saved)
            run_app(app)
            control(app, 'radio', 'Overview chart').set_value('Log loss'); run_app(app)
            self.assertFalse(app.exception)
            overview = next(d.value for d in app.dataframe if 'Zero-probability truths' in d.value.columns)
            self.assertEqual(overview.loc[overview['Model'] == MODELS['fragment2']['name'], 'Log loss (nats)'].iloc[0], '∞')
            self.assertEqual(overview.loc[overview['Model'] == MODELS['jev']['name'], 'Log loss (nats)'].iloc[0], '0')
            chart = next(json.loads(c.proto.spec) for c in app.get('vega_lite_chart') if 'Mean log loss in nats' in c.proto.spec)
            self.assertEqual(len(chart['encoding']['y']['sort']), 19)
            self.assertEqual(sum(n.startswith('API · ') for n in chart['encoding']['y']['sort']), 3)
            self.assertEqual(app.session_state.comparison, saved)
            self.assertEqual(app.session_state.suite_latest, draft)
            runner.assert_not_called(); api.assert_not_called()


if __name__ == '__main__':
    unittest.main()
