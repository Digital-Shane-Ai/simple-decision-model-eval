import json
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from additional_models import circuit_predict, verqen_predict
from compare import MODELS, normalize_result, ordered_model_keys, run_model
from refund_demo import QUESTIONS
from scripts.download_models import download


class AdditionalModelTests(unittest.TestCase):
    def test_verqen_yes_probability_is_not_selected_confidence(self):
        native = {"p_true": 0.07, "p_correct": 0.82, "selected": "no", "should_escalate": True}
        model = Mock()
        model.decide.return_value = native
        raw = verqen_predict(model, "repair please", QUESTIONS)
        result = normalize_result(raw)
        self.assertEqual(result["probability_yes"], 0.07)
        self.assertEqual(result["returned_confidence"], 0.82)
        self.assertEqual(raw["native_response"]["refund_requested"], native)
        model.decide.assert_called_once_with(state="repair please", question=QUESTIONS["refund_requested"]["instructions"], question_type="noul")

    def test_circuit_reads_yes_first_and_uses_native_layout(self):
        render = Mock(return_value="prompt")
        scorer = Mock(layout="pointer")
        scorer.score.return_value = [SimpleNamespace(probabilities=[0.12, 0.88], logits=[-2, 0], input_tokens=24)]
        with patch.dict(sys.modules, {
            "s1proto": SimpleNamespace(),
            "s1proto.schema": SimpleNamespace(NoulQuestion=lambda **q: q, ChoiceQuestion=lambda **q: q),
            "s1proto.template": SimpleNamespace(render_noul=render, render_choice=Mock()),
        }):
            raw = circuit_predict(scorer, "repair please", QUESTIONS)
        self.assertEqual(normalize_result(raw)["probability_yes"], 0.12)
        render.assert_called_once_with("repair please", QUESTIONS["refund_requested"], layout="pointer")
        scorer.score.assert_called_once_with(["prompt"])

    def test_new_workers_use_isolated_environments_and_hide_labels(self):
        keys = ["verqen", "fragment2", "circuit", "circuit8b", "wev", "wev4b", "wev8b", "openthai"]
        packet = {"results": [{"status": "ok", "inference_seconds": 0.1,
                               "raw_response": {"answers": {"refund_requested": {"noul": 0.8}}}}]}
        for key in keys:
            with self.subTest(key=key), patch("compare.subprocess.run", return_value=subprocess.CompletedProcess([], 0, json.dumps(packet))) as run:
                rows = run_model(key, [{"id": "secret-label-id", "message": "refund please", "expected": True}])
                self.assertEqual(rows[0]["status"], "ok")
                self.assertIn(MODELS[key]["environment"], Path(run.call_args.args[0][0]).parts)
                self.assertNotIn("secret-label-id", run.call_args.kwargs["input"])
                self.assertNotIn("expected", json.loads(run.call_args.kwargs["input"]))
        self.assertEqual(ordered_model_keys(list(reversed(keys))), keys)

    def test_circuit_downloads_pinned_base_as_well_as_adapter(self):
        with patch.dict(sys.modules, {"huggingface_hub": SimpleNamespace(snapshot_download=Mock())}), patch("scripts.download_models.snapshot") as fetch:
            download("circuit8b", MODELS["circuit8b"])
        self.assertEqual([c.args[0] for c in fetch.call_args_list], [MODELS["circuit8b"], MODELS["circuit8b"]["base"]])


if __name__ == "__main__":
    unittest.main()
