from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from compare import validate_questions, validate_cases, normalize_result, run_model, summarize, report, main
from additional_models import verqen_predict, circuit_predict
from model_worker import agentjev_predict
from markdown_copy import cases_table, table_markdown
from ui_state import draft_questions, preset_draft, context_rows, rows_to_cases

CHOICE = {'request': {'type':'choice', 'instructions':'What action is requested?',
                      'criteria':{'refund':'Return the payment', 'repair':'Repair the item', 'other':'Another request'}}}
CASE = [{'id':'private-label-id','message':'Please repair it.','expected_answers':{'request':'repair'}}]


def raw_choice(probabilities=None, choice='refund'):
    return {'answers':{'request': {'choice':choice,'probabilities':probabilities or {'refund':.7,'repair':.2,'other':.1},'confidence':.63}}}


class ChoiceTests(unittest.TestCase):
    def test_unknown_named_choice_is_distinct_from_unlabelled(self):
        questions={'q':{'type':'choice','instructions':'Category?', 'criteria':{'Unknown':'Unknown category','Known':'Known category'}}}
        cases=[{'id':'a','message':'A','expected_answers':{'q':'Unknown'}},
               {'id':'b','message':'B','expected_answers':{'q':None}}]
        rows=context_rows(cases,questions)
        self.assertEqual(rows[0]['q'],'Unknown'); self.assertIsNone(rows[1]['q'])
        self.assertEqual(rows_to_cases(rows,questions),cases)

    def test_choice_validation_and_type_specific_labels(self):
        self.assertEqual(validate_questions(CHOICE), CHOICE)
        self.assertEqual(validate_cases(CASE, CHOICE)[0]['expected_answers']['request'], 'repair')
        for value in [True, 1, 'missing']:
            bad=deepcopy(CASE); bad[0]['expected_answers']['request']=value
            with self.subTest(value=value), self.assertRaises(ValueError): validate_cases(bad, CHOICE)
        for criteria in [{}, {'only':'One'}, {' a':'A','b':'B'}, {'a':'','b':'B'}, {str(i):str(i) for i in range(256) }]:
            bad=deepcopy(CHOICE); bad['request']['criteria']=criteria
            with self.assertRaises(ValueError): validate_questions(bad)
        for kind in ['score','multi','text']:
            with self.assertRaises(ValueError): validate_questions({'q':{'type':kind,'instructions':'Q?'}})
        with self.assertRaises(ValueError):
            draft_questions([{'id':'q','instructions':'Q?'}], 'choice', {'q':[{'name':'a','meaning':'A'},{'name':'a','meaning':'Again'}]})

    def test_choice_distribution_validation_and_rounding(self):
        result=normalize_result(raw_choice(), 'request', CHOICE['request'])
        self.assertEqual(result['decision'],'refund'); self.assertAlmostEqual(result['selected_probability'],.7)
        self.assertEqual(result['returned_confidence'],.63)
        self.assertNotIn('probability_yes',result); self.assertNotIn('wants_refund',result)
        rounded=normalize_result(raw_choice({'refund':.3333,'repair':.3333,'other':.3333}), 'request', CHOICE['request'])
        self.assertAlmostEqual(sum(rounded['probabilities'].values()),1)
        invalid=[{'refund':True,'repair':0,'other':0}, {'refund':float('nan'),'repair':.2,'other':.1},
                 {'refund':.4,'repair':.2,'other':.1}, {'refund':1.1,'repair':0,'other':0},
                 {'refund':.8,'repair':.2}, {'refund':.7,'repair':.2,'other':.1,'extra':0}]
        for probabilities in invalid:
            with self.subTest(probabilities=probabilities), self.assertRaises(ValueError):
                normalize_result(raw_choice(probabilities), 'request', CHOICE['request'])
        for choice in ['unknown',None,'repair']:
            with self.assertRaises(ValueError): normalize_result(raw_choice(choice=choice), 'request', CHOICE['request'])

    def test_worker_payload_labels_scoring_and_report_export(self):
        packet={'results':[{'status':'ok','raw_response':raw_choice(),'inference_seconds':.1}]}
        with patch('compare.subprocess.run',return_value=subprocess.CompletedProcess([],0,json.dumps(packet))) as runner:
            rows=run_model('laya',CASE,questions=CHOICE)
        payload=json.loads(runner.call_args.kwargs['input'])
        self.assertEqual(payload,{'messages':['Please repair it.'],'questions':CHOICE})
        self.assertFalse(rows[0]['correct']); self.assertEqual(rows[0]['question_type'],'choice')
        stats=summarize(rows)[0]
        self.assertIsNone(stats['brier_score']); self.assertAlmostEqual(stats['choice_brier_score'],1.14)
        data=report(CASE,['laya'],rows,CHOICE)
        self.assertEqual(data['schema_version'],3)
        self.assertEqual(data['questions']['request']['criteria'],CHOICE['request']['criteria'])
        self.assertEqual(json.loads(json.dumps(data))['results'][0]['decision'],'refund')
        copied=table_markdown(cases_table(data['cases'],data['questions']))
        self.assertIn('repair',copied); self.assertIn('Return the payment',copied)
        CH=deepcopy(CHOICE); CH['request']['criteria']['refund']='Edited'
        self.assertNotEqual(data['questions'],CH)

    def test_mixed_questions_partial_failure_and_separate_scores(self):
        questions={**CHOICE,'binary':{'type':'noul','instructions':'Refund?'}}
        cases=[{'id':'a','message':'Context','expected_answers':{'request':'repair','binary':True}}]
        raw=raw_choice(); raw['answers']['binary']={'noul':.8}
        packet={'results':[{'status':'ok','raw_response':raw,'inference_seconds':.2}]}
        with patch.dict('os.environ', {'OR_TOKEN': 'fixture-key'}), patch('compare.predict_messages',return_value=packet) as runner:
            rows=run_model('jev',cases,questions=questions)
        self.assertEqual(runner.call_args.args[1],questions)
        summary=summarize(rows)[0]
        self.assertAlmostEqual(summary['brier_score'],.04); self.assertAlmostEqual(summary['choice_brier_score'],1.14)
        self.assertEqual(summary['mean_inference_seconds'],.2)
        del raw['answers']['request']['probabilities']['other']
        with patch.dict('os.environ', {'OR_TOKEN': 'fixture-key'}), patch('compare.predict_messages',return_value=packet): rows=run_model('jev',cases,questions=questions)
        self.assertEqual([r['status'] for r in rows],['error','ok'])
        self.assertEqual(summarize(rows)[0]['coverage'],.5)

    def test_agentjev_uses_native_choice_options_and_distribution(self):
        engine=Mock(temperatures={'choice':1})
        engine.evaluate.return_value={'results':[{'answers':[{'id':'request','value':'repair','distribution':{'refund':.1,'repair':.8,'other':.1}}]}]}
        raw=agentjev_predict(engine,'Please repair it.',CHOICE)
        request=engine.evaluate.call_args.args[0]
        self.assertEqual(request['questions'][0]['type'],'choice')
        self.assertEqual(request['questions'][0]['options']['repair'],'repair: Repair the item')
        self.assertEqual(normalize_result(raw,'request',CHOICE['request'])['decision'],'repair')
        self.assertIn('native_response',raw)

    def test_verqen_maps_rendered_options_back_to_names(self):
        model=Mock()
        model.decide.return_value={'selected':'repair: Repair the item','probabilities':{'refund: Return the payment':.1,'repair: Repair the item':.8,'other: Another request':.1},'p_correct':.91}
        raw=verqen_predict(model,'Please repair it.',CHOICE)
        self.assertEqual(model.decide.call_args.kwargs['options'],['refund: Return the payment','repair: Repair the item','other: Another request'])
        result=normalize_result(raw,'request',CHOICE['request'])
        self.assertEqual(result['decision'],'repair'); self.assertEqual(result['returned_confidence'],.91)

    def test_circuit_uses_native_choice_renderer_and_order(self):
        render=Mock(return_value='native choice prompt')
        scorer=Mock(layout='pointer')
        scorer.score.return_value=[SimpleNamespace(probabilities=[.1,.8,.1],logits=[0,2,0],input_tokens=33)]
        with patch.dict(sys.modules,{'s1proto':SimpleNamespace(),
             's1proto.schema':SimpleNamespace(NoulQuestion=lambda **q:q,ChoiceQuestion=lambda **q:q),
             's1proto.template':SimpleNamespace(render_noul=Mock(),render_choice=render)}):
            raw=circuit_predict(scorer,'Please repair it.',CHOICE)
        render.assert_called_once_with('Please repair it.',CHOICE['request'],layout='pointer')
        self.assertEqual(normalize_result(raw,'request',CHOICE['request'])['decision'],'repair')

    def test_preset_has_matching_choice_labels_for_all_twelve_contexts(self):
        draft=preset_draft('choice')
        questions=draft_questions(draft['questions_current'],'choice',draft['choices_current'])
        cases=validate_cases(draft['suite_latest'],questions)
        self.assertEqual(len(cases),12)
        self.assertEqual(set(c['expected_answers']['request_type'] for c in cases),set(questions['request_type']['criteria']))

    def test_cli_accepts_single_choice_expected_name(self):
        import tempfile
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'questions.json'; path.write_text(json.dumps(CHOICE))
            packet={'results':[{'status':'ok','raw_response':raw_choice()}]}
            with patch('sys.argv',['compare.py','Context','--questions',str(path),'--expected','repair','--models','laya']), \
                 patch('compare.subprocess.run',return_value=subprocess.CompletedProcess([],0,json.dumps(packet))), patch('builtins.print') as output:
                main()
            data=json.loads(output.call_args.args[0])
            self.assertEqual(data['cases'][0]['expected_answers']['request'],'repair')

if __name__=='__main__': unittest.main()
