# WEV-1.7B

[All results and exact inputs](README.md) · [Project overview](../../README.md) · [Original JSON](comparison.json)

Captured run: `2026-10-03T10:37:16.523083+00:00`. Question: `request_type`.

1 answer did not match the expected labels: `refund-history` was `replacement` instead of `order_status`.

## Summary

| Metric | Value |
| --- | --- |
| Answer pairs | 12 |
| Answered | 12 |
| Labeled | 12 |
| Correct | 11 |
| Incorrect | 1 |
| Execution errors | 0 |
| Accuracy | 11/12 (91.7%) |
| Coverage | 12/12 (100%) |
| Choice Brier | 0.080869 |
| Mean inference (ms) | 78.622 |
| Load time (s) | 2.925 |

## Answers

Expected labels come from the saved run. All rows have execution status `ok`; an incorrect classification is not an execution error.

| Case | Expected | Selected | Correct | Selected probability | Choice Brier | Inference (ms) |
| --- | --- | --- | --- | --- | --- | --- |
| `refund-headphones` | refund | refund | Yes | 0.999800 | 0.000000 | 162.128 |
| `replacement-only` | replacement | replacement | Yes | 0.999400 | 0.000001 | 67.543 |
| `before-purchase` | other | other | Yes | 0.998600 | 0.000003 | 71.033 |
| `money-back` | refund | refund | Yes | 0.992300 | 0.000108 | 83.221 |
| `refund-charge` | refund | refund | Yes | 1.000000 | 0.000000 | 77.004 |
| `keep-product` | other | other | Yes | 0.946200 | 0.004924 | 76.058 |
| `refund-polite` | refund | refund | Yes | 0.676100 | 0.159103 | 69.555 |
| `repair-only` | repair | repair | Yes | 0.999700 | 0.000000 | 76.884 |
| `shipping` | order_status | order_status | Yes | 0.993999 | 0.000064 | 68.886 |
| `refund-indirect` | refund | refund | Yes | 0.999600 | 0.000000 | 73.269 |
| `cancel-refund` | refund | refund | Yes | 1.000000 | 0.000000 | 68.315 |
| `refund-history` | order_status | replacement | No | 0.550010 | 0.806228 | 49.567 |

## Probabilities

| Case | refund | replacement | repair | order_status | other |
| --- | --- | --- | --- | --- | --- |
| `refund-headphones` | 0.999800 | 0.000200 | 0.000000 | 0.000000 | 0.000000 |
| `replacement-only` | 0.000300 | 0.999400 | 0.000200 | 0.000000 | 0.000100 |
| `before-purchase` | 0.000200 | 0.000900 | 0.000000 | 0.000300 | 0.998600 |
| `money-back` | 0.992300 | 0.007000 | 0.000300 | 0.000200 | 0.000200 |
| `refund-charge` | 1.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| `keep-product` | 0.044300 | 0.008100 | 0.001300 | 0.000100 | 0.946200 |
| `refund-polite` | 0.676100 | 0.199900 | 0.119200 | 0.000000 | 0.004800 |
| `repair-only` | 0.000100 | 0.000100 | 0.999700 | 0.000000 | 0.000100 |
| `shipping` | 0.000000 | 0.000800 | 0.000000 | 0.993999 | 0.005201 |
| `refund-indirect` | 0.999600 | 0.000300 | 0.000000 | 0.000000 | 0.000100 |
| `cancel-refund` | 1.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| `refund-history` | 0.107622 | 0.550010 | 0.000200 | 0.299760 | 0.042408 |

## Native confidence fields

These are the fields returned by the model, not a common confidence scale. **Not reported** is distinct from zero.

| Case | Returned confidence | Returned answer confidence |
| --- | --- | --- |
| `refund-headphones` | 0.999700 | Not reported |
| `replacement-only` | 0.999200 | Not reported |
| `before-purchase` | 0.998200 | Not reported |
| `money-back` | 0.990400 | Not reported |
| `refund-charge` | 1.000000 | Not reported |
| `keep-product` | 0.932800 | Not reported |
| `refund-polite` | 0.595100 | Not reported |
| `repair-only` | 0.999600 | Not reported |
| `shipping` | 0.992400 | Not reported |
| `refund-indirect` | 0.999500 | Not reported |
| `cancel-refund` | 0.999800 | Not reported |
| `refund-history` | 0.437400 | Not reported |

## Model and runtime

| Field | Recorded value |
| --- | --- |
| Model key | `wev` |
| Model identifier | `alanhuangya/wev-1.7b` |
| Execution | local |
| Reported device | `mps:0` |
| Timing scope | Local inference call on the reported device; model loading excluded |
| Checkpoint revision | 39a7e396ed7e5c1dd7e8455d6f6bab6669f85011 |
| Source repository | `https://github.com/alanhuangyoo/wev` |
| Source revision | a4dc555e152f58f9b818c4a08082188007bd5348 |
| Configured environment | `.venv-wev` |
| Runtime: python | `3.13.15` |
| Runtime: torch | `2.8.0` |

Local timing excludes loading and includes the first inference call. No separate warm-up was recorded.

This is one small initial screen. Read the [scoring and limitations](README.md#scoring-and-limits) before using it to choose a model for a larger evaluation.
