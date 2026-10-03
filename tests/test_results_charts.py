"""Chart semantics: saved data, failure denominators, legacy rows, and shared calls."""

from copy import deepcopy
import unittest

from compare import MODELS, ordered_results, ordered_model_keys, summarize
from results_charts import (score_data, probability_data, timing_data, brier_data,
                            score_spec, probability_spec, timing_spec, brier_spec)


def row(key='laya', case='one', **fields):
    return {'model_key': key, 'name': MODELS[key]['name'], 'case_id': case,
            'status': 'ok', 'question_id': 'question_1', 'question_type': 'noul',
            'expected': True, 'decision': True, 'correct': True,
            'probability_yes': .8, 'probability_no': .2, 'inference_seconds': 2,
            'execution': 'local', **fields}


class ChartDataTests(unittest.TestCase):
    def test_failure_and_unknown_labels_keep_different_denominators(self):
        rows = [row(), row(case='two', expected=None, correct=None),
                row(case='three', status='error', correct=None, probability_yes=None)]
        before = deepcopy(rows)
        points = score_data(rows)
        self.assertEqual(next(v for v in points if v['Metric'] == 'Accuracy')['Value'], 1)
        coverage = next(v for v in points if v['Metric'] == 'Coverage')
        self.assertEqual(coverage['Value'], 2/3)
        self.assertEqual(coverage['Count'], '2 / 3')
        self.assertEqual(rows, before)

    def test_unlabelled_and_all_errors_do_not_invent_accuracy(self):
        self.assertEqual([v['Metric'] for v in score_data([row(expected=None, correct=None)])], ['Coverage'])
        values = score_data([row(status='error', correct=None)])
        self.assertEqual([(v['Model'], v['Metric'], v['Value'], v['Count']) for v in values],
                         [('Laya', 'Coverage', 0, '0 / 1')])
        self.assertEqual(brier_data([row(status='error')], 'noul'), [])

    def test_registry_family_order_and_zero_probability_in_legacy_reports(self):
        legacy = row('kev9b', probability_yes=0, probability_no=None, wants_refund=False)
        legacy.pop('decision')
        rows = [legacy, row('kev'), row(status='error')]
        values = probability_data(rows, {'type': 'noul'}, 'Yes')
        self.assertEqual([v['Model'] for v in values], [MODELS['kev']['name'], MODELS['kev9b']['name']])
        self.assertEqual(values[1]['Value'], 0)
        self.assertEqual(values[1]['Decision'], 'No')
        self.assertEqual(probability_data([legacy], {'type': 'noul'}, 'No')[0]['Value'], 1)

    def test_choice_names_and_unavailable_probabilities(self):
        question = {'type': 'choice', 'criteria': {'decision': 'First', '<other>': 'Second'}}
        rows = [row(question_type='choice', decision='decision', expected='decision',
                    probabilities={'decision': .75, '<other>': .25}),
                row(case='missing', probabilities=None),
                row(case='bad', probabilities={'decision': float('nan')})]
        values = probability_data(rows, question, 'decision')
        self.assertEqual(len(values), 1)
        self.assertEqual(values[0]['Selection'], 'Selected answer')
        self.assertEqual(values[0]['Value'], .75)

    def test_timing_counts_context_once_and_combines_execution(self):
        rows = [row(inference_seconds=2), row(question_id='q2', inference_seconds=2),
                row(case='two', inference_seconds=6), row(case='error', status='error', inference_seconds=100),
                row('jev', execution='hosted', inference_seconds=.4),
                row('jev', case='bad', execution='hosted', inference_seconds=float('inf'))]
        values = timing_data(rows)
        self.assertEqual(values[0]['Execution'], 'hosted')
        self.assertEqual(values[0]['Timed contexts'], 1)
        self.assertEqual(values[1]['Seconds'], 4)
        self.assertEqual(values[1]['Timed contexts'], 2)
        spec = timing_spec(values)
        self.assertEqual(len(spec['encoding']['y']['sort']), 2)
        self.assertNotIn('facet', spec)
        self.assertEqual(spec['encoding']['x']['scale']['domain'][0], 0)
        self.assertGreater(spec['encoding']['x']['scale']['domain'][1], max(v['Seconds'] for v in values))

    def test_brier_scales_stay_separate_and_specs_are_valid(self):
        rows = [row(), row(case='choice', question_type='choice', expected='a', decision='a',
                           probabilities={'a': .8, 'b': .2})]
        binary = brier_data(rows, 'noul')
        choice = brier_data(rows, 'choice')
        self.assertAlmostEqual(binary[0]['Value'], .04)
        self.assertAlmostEqual(choice[0]['Value'], .08)
        self.assertEqual(brier_spec(binary, 'noul')['encoding']['x']['scale']['domain'], [0, 1])
        self.assertEqual(brier_spec(choice, 'choice')['encoding']['x']['scale']['domain'], [0, 2])
        for values, kind in [(binary, 'noul'), (choice, 'choice')]:
            self.assertEqual(brier_spec(values, kind)['encoding']['tooltip'][-1]['format'], '.8f')
        # Validate the actual chart protocol against the installed library schema.
        import altair as alt
        for spec in (score_spec(score_data(rows)), probability_spec(probability_data(rows[:1], {'type':'noul'}, 'Yes'), True),
                     probability_spec(probability_data(rows[:1], {'type':'noul'}, 'No')),
                     timing_spec(timing_data(rows)), brier_spec(binary, 'noul'), brier_spec(choice, 'choice')):
            alt.Chart.from_dict(spec, validate=True)

    def test_metric_sorting_stable_ties_and_registry_order_are_independent(self):
        rows = [row('jev', execution='hosted', probability_yes=.9, inference_seconds=2),
                row('kev', probability_yes=.9, inference_seconds=2),
                row(correct=False, probability_yes=.4, inference_seconds=4),
                row('kev9b', expected=None, correct=None, inference_seconds=1)]
        original = deepcopy(rows)
        registry = list(MODELS)
        scores = score_data(rows)
        names = list(dict.fromkeys(v['Model'] for v in scores))
        self.assertEqual(names, [MODELS[k]['name'] for k in ['kev', 'jev', 'laya', 'kev9b']])
        self.assertEqual([v['Model'] for v in brier_data(rows, 'noul')],
                         [MODELS[k]['name'] for k in ['kev', 'jev', 'laya']])
        self.assertEqual([v['Model'] for v in timing_data(rows)],
                         [MODELS[k]['name'] for k in ['kev9b', 'kev', 'jev', 'laya']])
        self.assertEqual([v['Value'] for v in brier_data(rows, 'noul')], sorted(v['Value'] for v in brier_data(rows, 'noul')))
        self.assertEqual(rows, original)
        self.assertEqual(list(MODELS), registry)
        self.assertEqual([r['model_key'] for r in ordered_results(rows)], ['laya', 'kev', 'kev9b', 'jev'])
        self.assertEqual(ordered_model_keys([r['model_key'] for r in rows]), ['laya', 'kev', 'kev9b', 'jev'])
        self.assertEqual([s['model'] for s in summarize(rows)], [MODELS[k]['name'] for k in ['laya', 'kev', 'kev9b', 'jev']])

    def test_coverage_only_sorts_descending_without_inventing_accuracy(self):
        rows = [row(expected=None, correct=None, status='error'),
                row('kev', expected=None, correct=None)]
        values = score_data(rows)
        self.assertEqual([v['Metric'] for v in values], ['Coverage', 'Coverage'])
        self.assertEqual([v['Value'] for v in values], [1, 0])

    def test_api_identity_and_color_agree_across_charts_and_legacy_rows(self):
        api = row('jev')
        api.pop('execution')
        rows = [api, row()]
        datasets = [score_data(rows), brier_data(rows, 'noul'), timing_data(rows),
                    probability_data(rows, {'type': 'noul'}, 'Yes')]
        specs = [score_spec(datasets[0]), brier_spec(datasets[1], 'noul'), timing_spec(datasets[2]),
                 probability_spec(datasets[3], True)]
        for values, spec in zip(datasets, specs):
            hosted = next(v for v in values if v['Model'] == MODELS['jev']['name'])
            self.assertEqual(hosted['Runtime'], 'Hosted API')
            self.assertTrue(hosted['Chart model'].startswith('API · '))
            self.assertEqual(spec['encoding']['color']['scale'], specs[0]['encoding']['color']['scale'])
            self.assertEqual(spec['encoding']['y']['sort'], list(dict.fromkeys(v['Chart model'] for v in values)))
        self.assertEqual(specs[0]['encoding']['shape']['field'], 'Metric')
        self.assertEqual(specs[3]['layer'][2]['encoding']['shape']['field'], 'Selection')

    def test_probability_order_does_not_rank_support_as_correctness(self):
        rows = [row('jev', execution='hosted', probability_yes=1, probability_no=0),
                row('kev', probability_yes=.1, probability_no=.9, decision=False, correct=False),
                row(probability_yes=.8, probability_no=.2)]
        for option in ['Yes', 'No']:
            values = probability_data(rows, {'type': 'noul'}, option)
            self.assertEqual([v['Model'] for v in values], [MODELS[k]['name'] for k in ['laya', 'kev', 'jev']])

    def test_empty_chart_inputs_are_safe(self):
        self.assertEqual(score_data([]), [])
        self.assertEqual(probability_data([], {'type':'noul'}, 'Yes'), [])
        self.assertEqual(timing_data([]), [])
        self.assertEqual(brier_data([], 'choice'), [])


if __name__ == '__main__':
    unittest.main()
