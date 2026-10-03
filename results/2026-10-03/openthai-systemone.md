# OpenThai-SystemOne

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
| Choice Brier | 0.001163 |
| Mean inference (ms) | 129.091 |
| Load time (s) | 2.241 |

## Answers

Expected labels come from the saved run. All rows have execution status `ok`; an incorrect classification is not an execution error.

| Case | Expected | Selected | Correct | Selected probability | Choice Brier | Inference (ms) |
| --- | --- | --- | --- | --- | --- | --- |
| `refund-headphones` | refund | refund | Yes | 0.991784 | 0.000087 | 228.146 |
| `replacement-only` | replacement | replacement | Yes | 0.988389 | 0.000172 | 129.088 |
| `before-purchase` | other | other | Yes | 0.991178 | 0.000100 | 126.686 |
| `money-back` | refund | refund | Yes | 0.987675 | 0.000199 | 132.208 |
| `refund-charge` | refund | refund | Yes | 0.990072 | 0.000126 | 124.129 |
| `keep-product` | other | other | Yes | 0.925714 | 0.007782 | 129.257 |
| `refund-polite` | refund | refund | Yes | 0.988597 | 0.000167 | 123.940 |
| `repair-only` | repair | repair | Yes | 0.985381 | 0.000285 | 134.917 |
| `shipping` | order_status | order_status | Yes | 0.990910 | 0.000104 | 124.266 |
| `refund-indirect` | refund | refund | Yes | 0.991142 | 0.000101 | 91.537 |
| `cancel-refund` | refund | refund | Yes | 0.991926 | 0.000083 | 88.939 |
| `refund-history` | order_status | order_status | Yes | 0.941732 | 0.004747 | 115.978 |

## Probabilities

| Case | refund | replacement | repair | order_status | other |
| --- | --- | --- | --- | --- | --- |
| `refund-headphones` | 0.991784 | 0.002950 | 0.001530 | 0.000937 | 0.002798 |
| `replacement-only` | 0.003353 | 0.988389 | 0.003634 | 0.001227 | 0.003397 |
| `before-purchase` | 0.001957 | 0.003290 | 0.002673 | 0.000903 | 0.991178 |
| `money-back` | 0.987675 | 0.003480 | 0.002061 | 0.001483 | 0.005300 |
| `refund-charge` | 0.990072 | 0.002567 | 0.002239 | 0.001322 | 0.003801 |
| `keep-product` | 0.007725 | 0.041032 | 0.022622 | 0.002908 | 0.925714 |
| `refund-polite` | 0.988597 | 0.003426 | 0.003816 | 0.000987 | 0.003174 |
| `repair-only` | 0.002697 | 0.007205 | 0.985381 | 0.001792 | 0.002924 |
| `shipping` | 0.002547 | 0.002685 | 0.001633 | 0.990910 | 0.002226 |
| `refund-indirect` | 0.991142 | 0.002790 | 0.001820 | 0.001028 | 0.003219 |
| `cancel-refund` | 0.991926 | 0.002229 | 0.001628 | 0.001281 | 0.002935 |
| `refund-history` | 0.017302 | 0.006469 | 0.002837 | 0.941732 | 0.031661 |

## Native confidence fields

These are the fields returned by the model, not a common confidence scale. **Not reported** is distinct from zero.

| Case | Returned confidence | Returned answer confidence |
| --- | --- | --- |
| `refund-headphones` | 0.963792 | Not reported |
| `replacement-only` | 0.951164 | Not reported |
| `before-purchase` | 0.961503 | Not reported |
| `money-back` | 0.948969 | Not reported |
| `refund-charge` | 0.957258 | Not reported |
| `keep-product` | 0.787038 | Not reported |
| `refund-polite` | 0.952079 | Not reported |
| `repair-only` | 0.941343 | Not reported |
| `shipping` | 0.960092 | Not reported |
| `refund-indirect` | 0.961316 | Not reported |
| `cancel-refund` | 0.964117 | Not reported |
| `refund-history` | 0.822741 | Not reported |

## Model and runtime

| Field | Recorded value |
| --- | --- |
| Model key | `openthai` |
| Model identifier | `iapp/OpenThai-SystemOne` |
| Execution | local |
| Reported device | `mps` |
| Timing scope | Local inference call on the reported device; model loading excluded |
| Checkpoint revision | f3709948b5e3cc9606a57e74ba62b7a639d17dd3 |
| Source repository | `https://github.com/iapp-technology/openthai-systemone` |
| Source revision | 5d04bcca0c58bd10e7dac2d3d369d8f760bea6cf |
| Configured environment | `.venv-modern` |
| Runtime: python | `3.13.15` |
| Runtime: torch | `2.14.0` |

Local timing excludes loading and includes the first inference call. No separate warm-up was recorded.

This is one small initial screen. Read the [scoring and limitations](README.md#scoring-and-limits) before using it to choose a model for a larger evaluation.
