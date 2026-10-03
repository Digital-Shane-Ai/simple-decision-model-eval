"""General questions use the native model protocol and score each answer independently."""
import contextlib
from copy import deepcopy
import io
import json
import subprocess
import sys
import unittest
from unittest.mock import Mock, patch

from compare import QUESTIONS, main, report, run_model, summarize, validate_cases, validate_questions
import model_worker

CUSTOM = {"replacement": {"type": "noul", "instructions": "Does the customer ask for a replacement?"},
          "damaged": {"type": "noul", "instructions": "Is the product damaged?"}}
CASES = [{"id": "private-case-label", "message": "Broken headphones. Send a replacement.",
          "expected_answers": {"replacement": True, "damaged": False}},
         {"id": "b", "message": "Working headphones.", "expected_answers": {"replacement": False}}]


def packet():
    return {"device": "cpu", "load_seconds": 1, "results": [
        {"status": "ok", "inference_seconds": .4, "raw_response": {"answers": {
            "replacement": {"noul": .9, "confidence": .6}, "damaged": {"noul": .8}}}},
        {"status": "ok", "inference_seconds": .2, "raw_response": {"answers": {
            "replacement": {"noul": .1}, "damaged": {"noul": .2}}}}]}


class QuestionTests(unittest.TestCase):
    def test_custom_questions_reach_one_worker_and_labels_stay_local(self):
        with patch('compare.subprocess.run', return_value=subprocess.CompletedProcess([], 0, json.dumps(packet()))) as worker:
            rows = run_model('laya', CASES, questions=CUSTOM)
        worker.assert_called_once()
        payload = json.loads(worker.call_args.kwargs['input'])
        self.assertEqual(payload, {'messages': [c['message'] for c in CASES], 'questions': CUSTOM})
        self.assertNotIn('private-case-label', json.dumps(payload))
        self.assertNotIn('expected', json.dumps(payload))
        self.assertEqual([(r['case_id'], r['question_id']) for r in rows],
                         [('private-case-label', 'replacement'), ('private-case-label', 'damaged'),
                          ('b', 'replacement'), ('b', 'damaged')])
        self.assertEqual([r['correct'] for r in rows], [True, False, True, None])
        self.assertNotIn('wants_refund', rows[0])
        self.assertEqual(rows[0]['returned_confidence'], .6)
        summary = summarize(rows)[0]
        self.assertEqual((summary['cases'], summary['contexts'], summary['labelled']), (4, 2, 3))
        self.assertAlmostEqual(summary['accuracy_on_answered'], 2/3)
        self.assertAlmostEqual(summary['mean_inference_seconds'], .3)
        self.assertAlmostEqual(summary['brier_score'], (.01 + .64 + .01)/3)

    def test_missing_and_invalid_answers_only_fail_their_question(self):
        data = packet()
        del data['results'][0]['raw_response']['answers']['damaged']
        data['results'][1]['raw_response']['answers']['damaged']['noul'] = True
        with patch('compare.subprocess.run', return_value=subprocess.CompletedProcess([], 0, json.dumps(data))):
            rows = run_model('laya', CASES, questions=CUSTOM)
        self.assertEqual([r['status'] for r in rows], ['ok', 'error', 'ok', 'error'])
        self.assertNotIn('decision', rows[1])
        self.assertEqual(summarize(rows)[0]['coverage'], .5)
        self.assertEqual(summarize(rows)[0]['correct_over_labelled'], 2/3)

    def test_worker_failure_expands_to_every_pair(self):
        with patch('compare.subprocess.run', side_effect=subprocess.TimeoutExpired('worker', 1)):
            rows = run_model('mojev', CASES, questions=CUSTOM)
        self.assertEqual(len(rows), 4)
        self.assertTrue(all(r['status'] == 'error' and 'decision' not in r for r in rows))

    def test_malformed_hosted_packet_is_a_visible_failure(self):
        for data in [None, [], {}, {'results': []}, {'results': [None, {'status': 'nonsense'}]}]:
            with self.subTest(data=data), patch.dict('os.environ', {'OR_TOKEN': 'fixture-key'}), patch('compare.predict_messages', return_value=data):
                rows = run_model('jev', CASES, questions=CUSTOM)
                self.assertEqual(len(rows), 4)
                self.assertTrue(all(r['status'] == 'error' for r in rows))

    def test_hosted_questions_and_labels(self):
        with patch.dict('os.environ', {'OR_TOKEN': 'fixture-key'}), patch('compare.predict_messages', return_value=packet()) as hosted:
            rows = run_model('jev', CASES, questions=CUSTOM)
        hosted.assert_called_once_with([c['message'] for c in CASES], CUSTOM, 'typesafe/jev-1.13')
        self.assertEqual(len(rows), 4)
        self.assertTrue(all(r['execution'] == 'hosted' for r in rows))

    def test_question_and_label_validation(self):
        for questions in [{}, [], {'': {'instructions': 'Does it work?'}},
                          {'x': {'instructions': '  '}}, {'x': {'type': 'choice', 'instructions': 'Choose'}}]:
            with self.subTest(questions=questions), self.assertRaises(ValueError):
                validate_questions(questions)
        self.assertEqual(validate_questions({'x': {'instructions': '  Is it broken?  '}})['x']['instructions'], 'Is it broken?')
        for labels in [{'other': True}, {'damaged': 'Yes'}, []]:
            with self.subTest(labels=labels), self.assertRaises(ValueError):
                validate_cases([{'message': 'test', 'expected_answers': labels}], CUSTOM)
        with self.assertRaisesRegex(ValueError, 'expected_answers'):
            validate_cases([{'message': 'test', 'expected': True}], CUSTOM)
        with self.assertRaises(ValueError):
            validate_cases([{'id': 'x', 'message': 'a'}, {'id': ' x ', 'message': 'b'}])
        self.assertEqual(validate_cases([{'message': 'test'}], CUSTOM)[0]['expected_answers'], {'replacement': None, 'damaged': None})
        self.assertTrue(validate_cases([{'message': 'refund', 'expected': True}])[0]['expected_answers']['refund_requested'])

    def test_saved_run_is_an_independent_snapshot(self):
        questions, cases = deepcopy(CUSTOM), deepcopy(CASES)
        with patch('compare.subprocess.run', return_value=subprocess.CompletedProcess([], 0, json.dumps(packet()))):
            rows = run_model('laya', cases, questions=questions)
        saved = report(cases, ['laya'], rows, questions)
        questions['replacement']['instructions'] = 'Changed wording'
        cases[0]['message'] = 'Changed context'
        rows[0]['raw_response']['answers']['replacement']['noul'] = .01
        self.assertEqual(saved['questions'], CUSTOM)
        self.assertEqual(saved['cases'][0]['message'], CASES[0]['message'])
        self.assertEqual(saved['results'][0]['raw_response']['answers']['replacement']['noul'], .9)
        self.assertEqual(saved['question_summaries']['replacement'][0]['accuracy_on_answered'], 1)
        self.assertEqual(saved['question_summaries']['damaged'][0]['accuracy_on_answered'], 0)

    def test_custom_cli_question_and_label(self):
        output = io.StringIO()
        with patch.object(sys, 'argv', ['compare.py', 'A broken item', '--question', 'Is it damaged?', '--expected', 'yes', '--models', 'laya']), \
                patch('compare.run_model', return_value=[]) as run, contextlib.redirect_stdout(output):
            main()
        call = run.call_args
        self.assertEqual(call.kwargs['questions'], {'question_1': {'type': 'noul', 'instructions': 'Is it damaged?'}})
        self.assertEqual(call.args[1][0]['expected_answers'], {'question_1': True})
        self.assertEqual(json.loads(output.getvalue())['questions'], call.kwargs['questions'])

    def test_worker_calls_predict_once_per_context_with_all_questions(self):
        predict = Mock(return_value={'answers': {qid: {'noul': .7} for qid in CUSTOM}})
        output = io.StringIO()
        with patch.object(sys, 'argv', ['model_worker.py', 'laya', '--device', 'cpu']), \
                patch.object(sys, 'stdin', io.StringIO(json.dumps({'messages': ['a', 'b'], 'questions': CUSTOM}))), \
                patch('model_worker.device_name', return_value='cpu'), \
                patch('model_worker.load_model', return_value=(predict, 'cpu')), \
                patch('model_worker.synchronize'), contextlib.redirect_stdout(output):
            model_worker.main()
        self.assertEqual([call.args for call in predict.call_args_list], [('a', CUSTOM), ('b', CUSTOM)])
        self.assertEqual(len(json.loads(output.getvalue())['results']), 2)


if __name__ == '__main__':
    unittest.main()
