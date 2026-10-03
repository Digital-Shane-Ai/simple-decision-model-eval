"""Verify README graphs against the real saved run, without model calls."""

from copy import deepcopy
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
LOADER = importlib.util.spec_from_file_location('saved_chart_generator', ROOT / 'results/2026-10-03/charts/generate.py')
generator = importlib.util.module_from_spec(LOADER)
LOADER.loader.exec_module(generator)
NS = {'s': 'http://www.w3.org/2000/svg'}


class SavedChartTests(unittest.TestCase):
    def test_saved_values_order_labels_and_shared_timing_axis(self):
        _, records = generator.collect(generator.SOURCE.read_bytes())
        original = deepcopy(records)
        with tempfile.TemporaryDirectory() as folder, patch.object(generator, 'HERE', Path(folder)):
            for render, name, field, reverse in [
                (generator.accuracy, 'accuracy.svg', 'accuracy', True),
                (generator.brier, 'brier.svg', 'choice_brier_score', False),
                (generator.timing, 'timing.svg', 'mean_call_ms', False),
            ]:
                render(records)
                tree = ET.parse(Path(folder) / name)
                text = [node.text for node in tree.findall('.//s:text', NS)]
                expected = sorted(records, key=lambda r: r[field], reverse=reverse)
                labels = [('API · ' if r['execution'] == 'hosted' else '') + r['model'] for r in expected]
                shown = [t for t in text if t in labels]
                # Brier also has its explicitly separate scale detail; the first 19 rows include every model.
                self.assertEqual(shown[:19], labels)
                self.assertEqual(sum(t.startswith('API · ') for t in shown[:19]), 3)
                self.assertIn('Local GPU', text)
                self.assertIn('Hosted API', text)
                self.assertIn(generator.LOCAL, (Path(folder) / name).read_text())
                self.assertIn(generator.HOSTED, (Path(folder) / name).read_text())
                if name == 'timing.svg':
                    self.assertEqual(len(shown), 19)
                    self.assertEqual(text.count('0'), 1)
                    self.assertEqual(text.count('500'), 1)
                    self.assertTrue(any('Different execution environment' in t for t in text))
                if name == 'accuracy.svg':
                    self.assertEqual(sum('100.0%' in t for t in text), 11)
                if name == 'brier.svg':
                    self.assertIn('0.00000000', text)
                    self.assertIn('0.00004113', text)
                    self.assertIn('0.95497872', text)
        self.assertEqual(records, original)

    def test_brier_labels_use_eight_decimal_places(self):
        _, records = generator.collect(generator.SOURCE.read_bytes())
        records = deepcopy(records)
        next(r for r in records if r['model_key'] == 'jev')['choice_brier_score'] = 1.23456789e-16
        original = deepcopy(records)
        self.assertEqual(generator.format_brier(0), '0.00000000')
        self.assertEqual(generator.format_brier(1.23456789e-16), '0.00000000')
        self.assertEqual(generator.format_brier(4.11283356670168e-05), '0.00004113')
        with tempfile.TemporaryDirectory() as folder, patch.object(generator, 'HERE', Path(folder)):
            generator.brier(records)
            tree = ET.parse(Path(folder) / 'brier.svg')
            values = [n.text for n in tree.findall('.//s:text', NS)
                      if n.get('x') == str(generator.RIGHT) and n.get('font-size') == '16']
            self.assertEqual(values.count('0.00000000'), 2)  # Both panels.
            for value in values:
                self.assertRegex(value, r'^\d+\.\d{8}$')
        self.assertEqual(records, original)


if __name__ == '__main__':
    unittest.main()
