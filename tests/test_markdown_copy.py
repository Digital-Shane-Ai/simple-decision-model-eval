import json
from pathlib import Path
import unittest
from unittest.mock import Mock, patch

import pandas as pd
from streamlit.testing.v1 import AppTest

from markdown_copy import cases_table, table_markdown

ROOT = Path(__file__).resolve().parents[1]


class MarkdownCopyTests(unittest.TestCase):
    def test_table_rounds_numbers_and_escapes_customer_text(self):
        frame = pd.DataFrame([{
            "Message": 'a | b\n<script>alert("x")</script> **bold** `code`',
            "Probability": 0.08478184789419174, "Missing": None,
            "Brier score": 0.000000087419174,
        }])
        text = table_markdown(frame)
        self.assertEqual(len(text.splitlines()), 3)
        self.assertIn('a \\| b<br>&lt;script&gt;', text)
        self.assertNotIn('<script>', text)
        self.assertIn('\\*\\*bold\\*\\* \\`code\\`', text)
        self.assertIn('0.08 |  |', text)
        self.assertNotIn('0.08478184789419174', text)
        self.assertIn(str(frame.iloc[0]["Brier score"]), text)

    def test_unknown_case_label_and_empty_cases(self):
        frame = cases_table([{'id': 'a', 'message': 'hello', 'expected': None}])
        self.assertIn('| a | hello | Unknown |', table_markdown(frame))
        self.assertEqual(len(table_markdown(cases_table([])).splitlines()), 2)

    def test_editing_inputs_does_not_change_copied_saved_cases(self):
        saved = json.loads((ROOT / 'examples/gpu-additional-results.json').read_text())
        copied = Mock()
        with patch('markdown_copy.make_copy_table_button', return_value=copied), patch('compare.run_model') as runner:
            app = AppTest.from_file(str(ROOT / 'app.py'))
            app.session_state.comparison = saved
            app.run()
            copied.reset_mock()
            revision = app.session_state.suite_revision
            app.session_state[f'suite_editor_{revision}'] = {
                'edited_rows': {0: {'message': 'Edited input | with a new message'}},
                'added_rows': [], 'deleted_rows': []}
            app.run()
            self.assertFalse(app.exception)
            tables = {call.args[2]: call.args[0] for call in copied.call_args_list}
            self.assertEqual(tables['copy_pending_cases'].iloc[0]['Context'], 'Edited input | with a new message')
            self.assertEqual(tables['copy_run_cases'].iloc[0]['Context'], saved['cases'][0]['message'])
            self.assertEqual(len(tables['copy_all_results']), len(saved['results']))
            self.assertEqual(len(tables['copy_summary']), len(saved['models']))
            runner.assert_not_called()


if __name__ == '__main__':
    unittest.main()
