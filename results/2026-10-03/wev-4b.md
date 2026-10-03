# WEV-4B

[All results and exact inputs](README.md) · [Project overview](../../README.md) · [Original JSON](comparison.json)

Captured run: `2026-10-03T10:37:16.523083+00:00`. Question: `request_type`.

All 12 answers matched the expected labels in this run.

## Summary

| Metric | Value |
| --- | --- |
| Answer pairs | 12 |
| Answered | 12 |
| Labeled | 12 |
| Correct | 12 |
| Incorrect | 0 |
| Execution errors | 0 |
| Accuracy | 12/12 (100.0%) |
| Coverage | 12/12 (100%) |
| Choice Brier | 0.032238 |
| Mean inference (ms) | 137.656 |
| Load time (s) | 4.308 |

## Answers

Expected labels come from the saved run. All rows have execution status `ok`; an incorrect classification is not an execution error.

| Case | Expected | Selected | Correct | Selected probability | Choice Brier | Inference (ms) |
| --- | --- | --- | --- | --- | --- | --- |
| `refund-headphones` | refund | refund | Yes | 0.975102 | 0.000854 | 194.612 |
| `replacement-only` | replacement | replacement | Yes | 0.999100 | 0.000001 | 123.184 |
| `before-purchase` | other | other | Yes | 0.998000 | 0.000005 | 130.570 |
| `money-back` | refund | refund | Yes | 0.915700 | 0.012668 | 148.567 |
| `refund-charge` | refund | refund | Yes | 0.996800 | 0.000017 | 146.313 |
| `keep-product` | other | other | Yes | 0.992801 | 0.000093 | 144.503 |
| `refund-polite` | refund | refund | Yes | 0.965797 | 0.001752 | 128.294 |
| `repair-only` | repair | repair | Yes | 0.998700 | 0.000003 | 144.214 |
| `shipping` | order_status | order_status | Yes | 0.997600 | 0.000011 | 123.781 |
| `refund-indirect` | refund | refund | Yes | 0.975700 | 0.000805 | 124.220 |
| `cancel-refund` | refund | refund | Yes | 0.993899 | 0.000054 | 125.740 |
| `refund-history` | order_status | order_status | Yes | 0.567300 | 0.370597 | 117.873 |

## Probabilities

| Case | refund | replacement | repair | order_status | other |
| --- | --- | --- | --- | --- | --- |
| `refund-headphones` | 0.975102 | 0.012799 | 0.006499 | 0.000300 | 0.005299 |
| `replacement-only` | 0.000200 | 0.999100 | 0.000400 | 0.000000 | 0.000300 |
| `before-purchase` | 0.000700 | 0.000500 | 0.000100 | 0.000700 | 0.998000 |
| `money-back` | 0.915700 | 0.074100 | 0.001000 | 0.000900 | 0.008300 |
| `refund-charge` | 0.996800 | 0.000400 | 0.000100 | 0.000200 | 0.002500 |
| `keep-product` | 0.006399 | 0.000400 | 0.000200 | 0.000200 | 0.992801 |
| `refund-polite` | 0.965797 | 0.011201 | 0.021302 | 0.000000 | 0.001700 |
| `repair-only` | 0.000100 | 0.000100 | 0.998700 | 0.000000 | 0.001100 |
| `shipping` | 0.000100 | 0.000100 | 0.000000 | 0.997600 | 0.002200 |
| `refund-indirect` | 0.975700 | 0.009500 | 0.004300 | 0.000200 | 0.010300 |
| `cancel-refund` | 0.993899 | 0.000400 | 0.000000 | 0.003000 | 0.002700 |
| `refund-history` | 0.003400 | 0.001100 | 0.000000 | 0.567300 | 0.428200 |

## Native confidence fields

These are the fields returned by the model, not a common confidence scale. **Not reported** is distinct from zero.

| Case | Returned confidence | Returned answer confidence |
| --- | --- | --- |
| `refund-headphones` | 0.969000 | Not reported |
| `replacement-only` | 0.998800 | Not reported |
| `before-purchase` | 0.997500 | Not reported |
| `money-back` | 0.894700 | Not reported |
| `refund-charge` | 0.996100 | Not reported |
| `keep-product` | 0.991100 | Not reported |
| `refund-polite` | 0.957100 | Not reported |
| `repair-only` | 0.998400 | Not reported |
| `shipping` | 0.997100 | Not reported |
| `refund-indirect` | 0.969600 | Not reported |
| `cancel-refund` | 0.992200 | Not reported |
| `refund-history` | 0.459100 | Not reported |

## Model and runtime

| Field | Recorded value |
| --- | --- |
| Model key | `wev4b` |
| Model identifier | `alanhuangya/wev-4b` |
| Execution | local |
| Reported device | `mps:0` |
| Timing scope | Local inference call on the reported device; model loading excluded |
| Checkpoint revision | 0c52b5224092355ef34b77381ffd93e80c161195 |
| Source repository | `https://github.com/alanhuangyoo/wev` |
| Source revision | a4dc555e152f58f9b818c4a08082188007bd5348 |
| Configured environment | `.venv-wev` |
| Runtime: python | `3.13.15` |
| Runtime: torch | `2.8.0` |

Local timing excludes loading and includes the first inference call. No separate warm-up was recorded.

This is one small initial screen. Read the [scoring and limitations](README.md#scoring-and-limits) before using it to choose a model for a larger evaluation.
