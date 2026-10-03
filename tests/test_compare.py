import json
from pathlib import Path
import subprocess
import unittest
from unittest.mock import patch

from compare import normalize_result, ordered_model_keys, ordered_results, run_model, summarize, validate_cases


def raw(p):
    return {"answers": {"refund_requested": {"noul": p}}}


class ComparisonTests(unittest.TestCase):
    def test_family_order_is_independent_of_selection_order(self):
        shuffled = ['lumma9b', 'kev27b', 'lumma', 'kev9b', 'kev']
        expected = ['kev', 'kev9b', 'kev27b', 'lumma', 'lumma9b']
        self.assertEqual(ordered_model_keys(shuffled), expected)
        rows = [{'model_key': key, 'case_id': case} for key in shuffled for case in ['b', 'a']]
        ordered = ordered_results(rows)
        self.assertEqual([r['model_key'] for r in ordered[::2]], expected)
        self.assertEqual([r['case_id'] for r in ordered[:2]], ['b', 'a'])

    def test_negative_confidence_is_not_probability_yes(self):
        result = normalize_result(raw(0.02))
        self.assertFalse(result["wants_refund"])
        self.assertAlmostEqual(result["selected_probability"], 0.98)
        self.assertIsNone(result["returned_confidence"])
        self.assertIsNone(result["returned_answer_confidence"])

    def test_native_confidence_preserved_and_probability_rejected(self):
        response = raw(0.8)
        response['answers']['refund_requested']['confidence'] = 0.6
        self.assertEqual(normalize_result(response)['returned_confidence'], 0.6)
        for value in [float('nan'), float('inf'), -0.1, 1.1, True]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                normalize_result(raw(value))

    def test_labels_never_enter_worker_input_and_errors_are_visible(self):
        cases = [{'id': 'a', 'message': 'refund please', 'expected': True},
                 {'id': 'b', 'message': 'a repair', 'expected': False}]
        packet = {'device': 'cpu', 'load_seconds': 1, 'results': [
            {'status': 'ok', 'raw_response': raw(0.9), 'inference_seconds': .2},
            {'status': 'error', 'error': 'inference failed'}]}
        with patch('compare.subprocess.run', return_value=subprocess.CompletedProcess([], 0, json.dumps(packet))) as run:
            rows = run_model('laya', cases)
        payload = json.loads(run.call_args.kwargs['input'])
        self.assertEqual(set(payload), {'messages', 'questions'})
        self.assertEqual(payload['messages'], ['refund please', 'a repair'])
        summary = summarize(rows)[0]
        self.assertEqual(summary['accuracy_on_answered'], 1)
        self.assertEqual(summary['coverage'], .5)
        self.assertEqual(summary['correct_over_labelled'], .5)
        self.assertAlmostEqual(summary['brier_score'], .01)
        self.assertEqual(summary['errors'], 1)

    def test_worker_failure_is_not_a_no_vote(self):
        with patch('compare.subprocess.run', side_effect=subprocess.TimeoutExpired('worker', 1)):
            rows = run_model('mojev', [{'id':'x','message':'refund','expected':False}])
        self.assertEqual(rows[0]['status'], 'error')
        self.assertNotIn('wants_refund', rows[0])
        self.assertIsNone(summarize(rows)[0]['accuracy_on_answered'])
        self.assertEqual(summarize(rows)[0]['correct_over_labelled'], 0)

    def test_suite_validation(self):
        for cases in [[], [{'id':'x','message':'','expected':True}],
                      [{'id':'x','message':'hello','expected':'false'}],
                      [{'id':'x','message':'a'}, {'id':'x','message':'b'}]]:
            with self.subTest(cases=cases), self.assertRaises(ValueError):
                validate_cases(cases)
        self.assertIsNone(validate_cases([{'message':'test'}])[0]['expected'])


if __name__ == '__main__':
    unittest.main()
