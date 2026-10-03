"""Real Streamlit editors with mocked model execution; no inference calls."""
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import unittest
from unittest.mock import patch

from streamlit.testing.v1 import AppTest
from compare import MODELS, QUESTION, default_model_keys

ROOT = Path(__file__).resolve().parents[1]


def control(app, kind, label):
    return next(widget for widget in getattr(app, kind) if widget.label == label)


def run_app(app):
    # AppTest 1.64 omits native editor and stateful-tab packets.
    states = app._tree.get_widget_states()
    for table in app.dataframe:
        if table.key and '_editor_' in table.key:
            widget = states.widgets.add()
            widget.id = table.proto.id
            widget.string_value = json.dumps(app.session_state[table.key])
    for tabs in app.get('tab_container'):
        if tabs.key:
            widget = states.widgets.add()
            widget.id = tabs.proto.id
            widget.string_value = app.session_state[tabs.key]
    return app._run(states)


def edit_table(app, key, changes=None, added=None, deleted=None):
    previous = app.session_state[key]
    edits = {'edited_rows': {int(k): dict(v) for k, v in previous['edited_rows'].items()},
             'added_rows': [dict(row) for row in previous['added_rows']],
             'deleted_rows': list(previous['deleted_rows'])}
    if key.startswith('choices_editor_'):
        base_size = len(app.session_state.choices_base[app.session_state.choices_for])
    else:
        mode = key.split('_editor_')[0]
        base_size = len(app.session_state['questions_base' if mode == 'questions' else 'suite_base'])
    for index, values in (changes or {}).items():
        if index >= base_size:
            edits['added_rows'][index - base_size].update(values)
        else:
            edits['edited_rows'].setdefault(index, {}).update(values)
    edits['added_rows'].extend(added or [])
    for index in sorted(deleted or [], reverse=True):
        if index >= base_size:
            del edits['added_rows'][index - base_size]
        else:
            edits['deleted_rows'].append(index)
    app.session_state[key] = edits
    run_app(app)
    if app.exception:
        raise AssertionError(str(app.exception))
    return app


def edit_questions(app, **kwargs):
    return edit_table(app, f'questions_editor_{app.session_state.question_revision}', **kwargs)


def edit_contexts(app, **kwargs):
    return edit_table(app, f'suite_editor_{app.session_state.suite_revision}', **kwargs)


def edit_choices(app, **kwargs):
    return edit_table(app, f'choices_editor_{app.session_state.choices_revision}_{app.session_state.choices_for}', **kwargs)


def switch_mode(app, mode):
    control(app, 'radio', 'Answer type').set_value(mode)
    run_app(app)
    if app.exception:
        raise AssertionError(str(app.exception))


def mock_worker(*args, **kwargs):
    payload = json.loads(kwargs['input'])
    answers = {}
    for index, (qid, q) in enumerate(payload['questions'].items()):
        if q['type'] == 'noul':
            answers[qid] = {'noul': .8 if index == 0 else .2}
        else:
            names = list(q['criteria'])
            answers[qid] = {'choice': names[0], 'probabilities': {k: .8 if i == 0 else .2 / (len(names)-1) for i, k in enumerate(names)}}
    results = [{'status': 'ok', 'inference_seconds': .1, 'raw_response': {'answers': deepcopy(answers)}} for _ in payload['messages']]
    return subprocess.CompletedProcess([], 0, json.dumps({'results': results, 'device': 'cpu', 'load_seconds': 1}))


class AppTests(unittest.TestCase):
    def app(self, all_models=False):
        app = AppTest.from_file(str(ROOT / 'app.py'), default_timeout=30).run()
        if not all_models:
            control(app, 'multiselect', 'Run these models').set_value(['laya'])
            run_app(app)
        self.assertFalse(app.exception)
        return app

    def run_comparison(self, app):
        control(app, 'button', 'Run comparison').click()
        run_app(app)
        self.assertFalse(app.exception)

    def test_default_suite_all_models_keep_failures_and_device(self):
        def worker(*args, **kwargs):
            return subprocess.CompletedProcess([], 1, '') if args[0][2] == 'mojev' else mock_worker(*args, **kwargs)
        hosted = {'results': [{'status': 'error', 'error': 'fixture hosted error'} for _ in range(12)]}
        with patch.dict('os.environ', {'OR_TOKEN': 'fixture-key'}), \
                patch('compare.subprocess.run', side_effect=worker) as runner, patch('compare.predict_messages', return_value=hosted):
            app = self.app(all_models=True)
            self.assertEqual(len(app.session_state.suite_latest), 12)
            self.assertEqual([r.label for r in app.radio], ['Answer type'])
            self.assertEqual(control(app, 'selectbox', 'Device').value, 'mps')
            self.run_comparison(app)
            self.assertEqual(runner.call_count, len(default_model_keys())-1)
            self.assertTrue(all(c.args[0][-1] == 'mps' for c in runner.call_args_list))
            result = app.session_state.comparison
            self.assertEqual(len(result['results']), 12*len(default_model_keys()))
            self.assertEqual(next(s for s in result['summary'] if s['model'] == 'MoJev')['errors'], 12)
            self.assertTrue(app.warning)

    def test_delete_eleven_rows_is_a_single_context_run(self):
        with patch('compare.subprocess.run', side_effect=mock_worker) as runner:
            app = self.app()
            edit_contexts(app, deleted=list(range(1, 12)))
            self.run_comparison(app)
            self.assertEqual(len(app.session_state.comparison['cases']), 1)
            self.assertEqual(len(json.loads(runner.call_args.kwargs['input'])['messages']), 1)
            self.assertTrue(app.session_state.comparison['results'][0]['correct'])

    def test_questions_add_edit_remove_repeated_runs_and_snapshot(self):
        with patch('compare.subprocess.run', side_effect=mock_worker) as runner:
            app = self.app()
            edit_contexts(app, deleted=list(range(1, 12)))
            self.run_comparison(app)
            first = deepcopy(app.session_state.comparison)
            revision = app.session_state.question_revision
            edit_questions(app, added=[{'instructions': 'I'}])
            edit_questions(app, changes={1: {'instructions': 'Is it working?'}})
            self.assertEqual(app.session_state.question_revision, revision)
            self.assertEqual(app.session_state.questions_current[1]['id'], 'question_2')
            edit_contexts(app, changes={0: {'question_2': 'No', 'message': 'Broken, refund please.'}})
            self.assertEqual(app.session_state.comparison, first)
            self.run_comparison(app)
            second = deepcopy(app.session_state.comparison)
            self.assertEqual([r['correct'] for r in second['results']], [True, True])
            edit_questions(app, changes={0: {'instructions': 'Is it damaged?'}})
            self.assertIsNone(app.session_state.suite_latest[0]['expected_answers']['refund_requested'])
            self.assertFalse(app.session_state.suite_latest[0]['expected_answers']['question_2'])
            self.assertEqual(app.session_state.comparison, second)
            edit_questions(app, deleted=[1])
            self.run_comparison(app)
            self.assertEqual(len(app.session_state.comparison['results']), 1)
            self.assertNotIn('wants_refund', app.session_state.comparison['results'][0])
            edit_questions(app, added=[{'instructions': 'Another?'}])
            self.assertEqual(app.session_state.questions_current[1]['id'], 'question_3')
            self.assertEqual(runner.call_count, 3)

    def test_mode_presets_labels_and_drafts_are_preserved(self):
        with patch('compare.subprocess.run', side_effect=mock_worker):
            app = self.app()
            edit_questions(app, changes={0: {'instructions': 'My custom binary question?'}})
            edit_contexts(app, changes={0: {'message': 'My own context', 'refund_requested': 'Yes'}}, deleted=list(range(1,12)))
            switch_mode(app, 'choice')
            self.assertEqual(len(app.session_state.suite_latest), 12)
            labels = {c['id']: c['expected_answers']['request_type'] for c in app.session_state.suite_latest}
            self.assertEqual(labels['replacement-only'], 'replacement')
            self.assertEqual(labels['repair-only'], 'repair')
            self.assertEqual(labels['refund-history'], 'order_status')
            self.assertEqual(len(app.session_state.choices_current['request_type']), 5)
            self.run_comparison(app)
            self.assertEqual(app.session_state.comparison['questions']['request_type']['type'], 'choice')
            self.assertIsNotNone(app.session_state.comparison['summary'][0]['choice_brier_score'])
            edit_contexts(app, changes={0: {'message': 'My custom choice context'}})
            switch_mode(app, 'noul')
            self.assertEqual(len(app.session_state.suite_latest), 1)
            self.assertEqual(app.session_state.suite_latest[0]['message'], 'My own context')
            self.assertTrue(app.session_state.suite_latest[0]['expected_answers']['refund_requested'])
            self.assertEqual(app.session_state.questions_current[0]['instructions'], 'My custom binary question?')
            switch_mode(app, 'choice')
            self.assertEqual(app.session_state.suite_latest[0]['message'], 'My custom choice context')

    def test_choice_changes_reset_only_affected_labels_and_persist(self):
        with patch('compare.subprocess.run', side_effect=mock_worker):
            app = self.app(); switch_mode(app, 'choice')
            edit_questions(app, added=[{'instructions': 'Which department?'}])
            control(app, 'selectbox', 'Choices for question').set_value('question_2'); run_app(app)
            edit_choices(app, added=[{'name':'a','meaning':'Department A'}, {'name':'b','meaning':'Department B'}])
            edit_contexts(app, changes={0: {'question_2':'b'}})
            control(app, 'selectbox', 'Choices for question').set_value('request_type'); run_app(app)
            edit_choices(app, changes={0: {'meaning':'Explicitly return the payment now.'}})
            labels = app.session_state.suite_latest[0]['expected_answers']
            self.assertIsNone(labels['request_type']); self.assertEqual(labels['question_2'], 'b')
            self.run_comparison(app)
            saved = deepcopy(app.session_state.comparison)
            edit_choices(app, deleted=[4], added=[{'name':'new','meaning':'New category'}])
            self.assertEqual(app.session_state.comparison, saved)
            switch_mode(app,'noul'); switch_mode(app,'choice')
            self.assertIn('new', [r['name'] for r in app.session_state.choices_current['request_type']])
            self.assertNotIn('other', [r['name'] for r in app.session_state.choices_current['request_type']])

    def test_invalid_choices_block_execution_and_preserve_last_run(self):
        with patch('compare.subprocess.run', side_effect=mock_worker) as runner:
            app = self.app(); switch_mode(app, 'choice'); self.run_comparison(app)
            saved = deepcopy(app.session_state.comparison)
            edit_choices(app, changes={1: {'name':'refund'}})
            self.run_comparison(app)
            self.assertTrue(app.error); self.assertEqual(runner.call_count, 1)
            self.assertEqual(app.session_state.comparison, saved)

    def test_inspector_stays_selected_when_question_changes(self):
        with patch('compare.subprocess.run', side_effect=mock_worker):
            app = self.app(); edit_questions(app, added=[{'instructions':'Is it damaged?'}]); self.run_comparison(app)
            app.session_state['results_tab'] = 'Inspect answers'; run_app(app)
            control(app, 'selectbox', 'Inspect question').set_value('question_2'); run_app(app)
            self.assertFalse(app.exception)
            self.assertEqual(app.session_state['results_tab'], 'Inspect answers')
            self.assertTrue(any(c.value == 'Question: Is it damaged?' for c in app.caption))

    def test_empty_questions_contexts_and_blank_input_block_runs(self):
        with patch('compare.run_model') as runner:
            app = self.app(); edit_contexts(app, changes={0: {'message':' '}}); self.run_comparison(app)
            self.assertTrue(app.error)
            edit_contexts(app, deleted=list(range(12))); self.run_comparison(app); self.assertTrue(app.error)
            edit_contexts(app, added=[{'message':'New context','refund_requested':'Yes'}])
            self.assertTrue(app.session_state.suite_latest[0]['id'].startswith('case_'))
            edit_questions(app, deleted=[0]); self.run_comparison(app); self.assertTrue(app.error)
            edit_questions(app, added=[{'instructions':' '}]); self.run_comparison(app); self.assertTrue(app.error)
            runner.assert_not_called()

    def test_context_additions_survive_question_edits_and_mode_switches(self):
        app = self.app()
        edit_contexts(app, added=[{'message':'Extra context','refund_requested':'Yes'}])
        new_id = app.session_state.suite_latest[-1]['id']
        edit_questions(app, added=[{'instructions':'Second question?'}])
        self.assertEqual(app.session_state.suite_latest[-1]['id'], new_id)
        self.assertTrue(app.session_state.suite_latest[-1]['expected_answers']['refund_requested'])
        switch_mode(app,'choice'); switch_mode(app,'noul')
        self.assertEqual(app.session_state.suite_latest[-1]['message'], 'Extra context')
        edit_contexts(app, deleted=[12])
        self.assertEqual(len(app.session_state.suite_latest), 12)

    def test_no_models_disables_run(self):
        app = self.app(); control(app,'multiselect','Run these models').set_value([]); run_app(app)
        self.assertTrue(control(app,'button','Run comparison').disabled)

    def test_choice_named_decision_has_distinct_probability_column(self):
        with patch('compare.subprocess.run', side_effect=mock_worker):
            app = self.app(); switch_mode(app, 'choice')
            edit_choices(app, changes={0: {'name':'decision'}})
            edit_contexts(app, changes={0: {'request_type':'decision'}})
            self.run_comparison(app)
            inspector = next(d.value for d in app.dataframe if 'P · decision' in d.value.columns)
            self.assertEqual(len(inspector.columns), len(set(inspector.columns)))
            self.assertAlmostEqual(inspector.iloc[0]['P · decision'], .8)
            self.assertTrue(app.session_state.comparison['results'][0]['correct'])

    def test_chart_controls_preserve_saved_run_and_editable_drafts(self):
        with patch('compare.subprocess.run', side_effect=mock_worker) as runner:
            app = self.app()
            edit_questions(app, added=[{'instructions': 'Is it damaged?'}])
            self.run_comparison(app)
            saved = deepcopy(app.session_state.comparison)
            draft = deepcopy(app.session_state.suite_latest)
            control(app, 'radio', 'Overview chart').set_value('Brier scores'); run_app(app)
            app.session_state['results_tab'] = 'Inspect answers'; run_app(app)
            control(app, 'selectbox', 'Inspect question').set_value('question_2'); run_app(app)
            control(app, 'selectbox', 'Probability to compare').set_value('No'); run_app(app)
            self.assertFalse(app.exception)
            self.assertGreaterEqual(len(app.get('vega_lite_chart')), 3)
            self.assertEqual(app.session_state.comparison, saved)
            self.assertEqual(app.session_state.suite_latest, draft)
            self.assertEqual(app.session_state['results_tab'], 'Inspect answers')
            self.assertEqual(runner.call_count, 1)

    def test_chart_failure_and_unlabelled_states_do_not_invent_scores(self):
        failed = subprocess.CompletedProcess([], 1, 'fixture failure')
        with patch('compare.subprocess.run', return_value=failed):
            app = self.app(); self.run_comparison(app)
            self.assertTrue(any('No successful probabilities' in item.value for item in app.info))
            self.assertTrue(any('No successful context timings' in item.value for item in app.info))
            control(app, 'radio', 'Overview chart').set_value('Brier scores'); run_app(app)
            self.assertFalse(app.exception)
            self.assertTrue(any('Brier scores need' in item.value for item in app.info))
        with patch('compare.subprocess.run', side_effect=mock_worker):
            app = self.app()
            edit_contexts(app, changes={i: {'refund_requested': 'Unknown'} for i in range(12)})
            self.run_comparison(app)
            self.assertIsNone(app.session_state.comparison['summary'][0]['accuracy_on_answered'])
            self.assertIsNone(app.session_state.comparison['summary'][0]['brier_score'])
            self.assertFalse(app.exception)

    def test_choice_chart_selector_uses_saved_choice_names(self):
        with patch('compare.subprocess.run', side_effect=mock_worker) as runner:
            app = self.app(); switch_mode(app, 'choice')
            edit_choices(app, changes={0: {'name': 'decision'}})
            self.run_comparison(app)
            saved = deepcopy(app.session_state.comparison)
            control(app, 'selectbox', 'Probability to compare').set_value('replacement'); run_app(app)
            self.assertFalse(app.exception)
            self.assertEqual(control(app, 'selectbox', 'Probability to compare').options,
                             list(saved['questions']['request_type']['criteria']))
            self.assertEqual(app.session_state.comparison, saved)
            self.assertEqual(runner.call_count, 1)

    def test_saved_actual_run_has_one_shared_timing_chart_and_preserves_state(self):
        saved = json.loads((ROOT / 'results/2026-10-03/comparison.json').read_text())
        with patch('compare.run_model', side_effect=AssertionError('Inference forbidden in saved-run QA')) as runner:
            app = self.app()
            draft = deepcopy(app.session_state.suite_latest)
            app.session_state['comparison'] = deepcopy(saved)
            app.session_state['results_tab'] = 'Run details'
            run_app(app)
            self.assertFalse(app.exception)
            charts = app.get('vega_lite_chart')
            timings = [json.loads(c.proto.spec) for c in charts if 'Mean observed context' in c.proto.spec]
            self.assertEqual(len(timings), 1)
            labels = timings[0]['encoding']['y']['sort']
            self.assertEqual(len(labels), 19)
            self.assertEqual(sum(label.startswith('API · ') for label in labels), 3)
            self.assertEqual(timings[0]['encoding']['color']['scale']['domain'], ['Local', 'Hosted API'])
            control(app, 'radio', 'Overview chart').set_value('Brier scores'); run_app(app)
            self.assertFalse(app.exception)
            self.assertEqual(app.session_state.comparison, saved)
            self.assertEqual(app.session_state.suite_latest, draft)
            runner.assert_not_called()

if __name__ == '__main__':
    unittest.main()
