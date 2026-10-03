import json
import unittest
from unittest.mock import Mock, patch

import requests

from compare import run_model
from openrouter_backend import ENDPOINT, predict_messages
from refund_demo import QUESTIONS


class OpenRouterTests(unittest.TestCase):
    def test_missing_token_never_calls_network(self):
        with patch.dict('os.environ', {'OR_TOKEN': ''}), patch('openrouter_backend.requests.Session') as session:
            packet = predict_messages(['refund'], QUESTIONS, 'typesafe/jev-1.13')
        session.assert_not_called()
        self.assertEqual(packet['results'][0]['status'], 'error')
        self.assertIn('OR_TOKEN', packet['results'][0]['error'])

    def test_native_endpoint_and_no_label_leak(self):
        native={'model':'typesafe/jev-1.13-20260917', 'provider':'TypeSafe',
                'answers':{'refund_requested':{'type':'noul','noul':.95}},'usage':{'cost':.000001}}
        response=Mock(status_code=200,text=json.dumps(native))
        with patch.dict('os.environ', {'OR_TOKEN':'fake-test-token'}), patch('openrouter_backend.requests.Session') as factory:
            session=factory.return_value.__enter__.return_value
            session.post.return_value=response
            rows=run_model('jev',[{'id':'private-label-id','message':'Refund my shoes please','expected':True}])
        args=session.post.call_args
        self.assertEqual(args.args[0],ENDPOINT)
        self.assertEqual(args.kwargs['headers']['Authorization'],'Bearer fake-test-token')
        self.assertEqual(args.kwargs['json'],{'model':'typesafe/jev-1.13','state':'Refund my shoes please','questions':QUESTIONS})
        self.assertFalse(args.kwargs['allow_redirects'])
        self.assertEqual(rows[0]['raw_response'],native)
        self.assertTrue(rows[0]['correct'])
        self.assertEqual(rows[0]['execution'],'hosted')
        self.assertIsNone(rows[0]['returned_confidence'])
        self.assertNotIn('fake-test-token',json.dumps(rows))

    def test_errors_and_timeouts_do_not_become_no_votes_or_retry(self):
        with patch.dict('os.environ', {'OR_TOKEN':'fake-test-token'}), patch('openrouter_backend.requests.Session') as factory:
            session=factory.return_value.__enter__.return_value
            session.post.side_effect=[Mock(status_code=401,text=json.dumps({'error':{'message':'invalid fake-test-token'}})),requests.Timeout()]
            packet=predict_messages(['one','two'],QUESTIONS,'typesafe/jev-1.13')
        self.assertEqual(session.post.call_count,2)
        self.assertTrue(all(r['status']=='error' for r in packet['results']))
        self.assertNotIn('fake-test-token',json.dumps(packet))
        self.assertIn('[REDACTED]',packet['results'][0]['error'])

    def test_wrong_model_is_rejected(self):
        with patch.dict('os.environ', {'OR_TOKEN':'fake'}), patch('openrouter_backend.requests.Session') as factory:
            factory.return_value.__enter__.return_value.post.return_value=Mock(status_code=200,text=json.dumps({'model':'typesafe/jev-latest','answers':{}}))
            packet=predict_messages(['one'],QUESTIONS,'typesafe/jev-1.13')
        self.assertEqual(packet['results'][0]['status'],'error')


if __name__=='__main__': unittest.main()
