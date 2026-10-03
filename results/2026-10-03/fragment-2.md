# Fragment-2

[All results and exact inputs](README.md) · [Project overview](../../README.md) · [Original JSON](comparison.json)

Captured run: `2026-10-03T10:37:16.523083+00:00`. Question: `request_type`.

The model selected `refund` on all 12 cases. It matched the six refund labels and missed every other label, equaling the always-refund baseline.

## Summary

| Metric | Value |
| --- | --- |
| Answer pairs | 12 |
| Answered | 12 |
| Labeled | 12 |
| Correct | 6 |
| Incorrect | 6 |
| Execution errors | 0 |
| Accuracy | 6/12 (50.0%) |
| Coverage | 12/12 (100%) |
| Choice Brier | 0.954979 |
| Mean inference (ms) | 12.541 |
| Load time (s) | 0.572 |

## Answers

Expected labels come from the saved run. All rows have execution status `ok`; an incorrect classification is not an execution error.

| Case | Expected | Selected | Correct | Selected probability | Choice Brier | Inference (ms) |
| --- | --- | --- | --- | --- | --- | --- |
| `refund-headphones` | refund | refund | Yes | 0.868787 | 0.034329 | 83.917 |
| `replacement-only` | replacement | refund | No | 0.963500 | 1.857243 | 6.241 |
| `before-purchase` | other | refund | No | 0.954700 | 1.913450 | 5.943 |
| `money-back` | refund | refund | Yes | 0.959800 | 0.003200 | 8.588 |
| `refund-charge` | refund | refund | Yes | 0.979500 | 0.000824 | 4.239 |
| `keep-product` | other | refund | No | 0.937013 | 1.881660 | 5.836 |
| `refund-polite` | refund | refund | Yes | 0.958300 | 0.003453 | 4.216 |
| `repair-only` | repair | refund | No | 0.957000 | 1.917272 | 5.947 |
| `shipping` | order_status | refund | No | 0.954600 | 1.912842 | 5.701 |
| `refund-indirect` | refund | refund | Yes | 0.943194 | 0.006409 | 6.424 |
| `cancel-refund` | refund | refund | Yes | 0.972497 | 0.001502 | 7.496 |
| `refund-history` | order_status | refund | No | 0.962604 | 1.927560 | 5.940 |

## Probabilities

| Case | refund | replacement | repair | order_status | other |
| --- | --- | --- | --- | --- | --- |
| `refund-headphones` | 0.868787 | 0.130813 | 0.000300 | 0.000100 | 0.000000 |
| `replacement-only` | 0.963500 | 0.036200 | 0.000200 | 0.000100 | 0.000000 |
| `before-purchase` | 0.954700 | 0.044700 | 0.000400 | 0.000200 | 0.000000 |
| `money-back` | 0.959800 | 0.039800 | 0.000300 | 0.000100 | 0.000000 |
| `refund-charge` | 0.979500 | 0.020100 | 0.000300 | 0.000100 | 0.000000 |
| `keep-product` | 0.937013 | 0.062188 | 0.000500 | 0.000200 | 0.000100 |
| `refund-polite` | 0.958300 | 0.041400 | 0.000200 | 0.000100 | 0.000000 |
| `repair-only` | 0.957000 | 0.042700 | 0.000200 | 0.000100 | 0.000000 |
| `shipping` | 0.954600 | 0.044500 | 0.000600 | 0.000200 | 0.000100 |
| `refund-indirect` | 0.943194 | 0.056406 | 0.000300 | 0.000100 | 0.000000 |
| `cancel-refund` | 0.972497 | 0.027303 | 0.000100 | 0.000100 | 0.000000 |
| `refund-history` | 0.962604 | 0.036796 | 0.000400 | 0.000200 | 0.000000 |

## Native confidence fields

These are the fields returned by the model, not a common confidence scale. **Not reported** is distinct from zero.

| Case | Returned confidence | Returned answer confidence |
| --- | --- | --- |
| `refund-headphones` | 0.756100 | Not reported |
| `replacement-only` | 0.901400 | Not reported |
| `before-purchase` | 0.883100 | Not reported |
| `money-back` | 0.893700 | Not reported |
| `refund-charge` | 0.936300 | Not reported |
| `keep-product` | 0.851500 | Not reported |
| `refund-polite` | 0.891000 | Not reported |
| `repair-only` | 0.888400 | Not reported |
| `shipping` | 0.882300 | Not reported |
| `refund-indirect` | 0.862400 | Not reported |
| `cancel-refund` | 0.920700 | Not reported |
| `refund-history` | 0.898900 | Not reported |

## Model and runtime

| Field | Recorded value |
| --- | --- |
| Model key | `fragment2` |
| Model identifier | `FrameXlabs/fragment-2` |
| Execution | local |
| Reported device | `mps:0` |
| Timing scope | Local inference call on the reported device; model loading excluded |
| Checkpoint revision | 3691fff73738d8d31e7e1b8877bb515b792bce57 |
| Configured environment | `.venv-modern` |
| Runtime: python | `3.13.15` |
| Runtime: torch | `2.14.0` |

Local timing excludes loading and includes the first inference call. No separate warm-up was recorded.

This is one small initial screen. Read the [scoring and limitations](README.md#scoring-and-limits) before using it to choose a model for a larger evaluation.
