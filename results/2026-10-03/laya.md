# Laya

[All results and exact inputs](README.md) · [Project overview](../../README.md) · [Original JSON](comparison.json)

Captured run: `2026-10-03T10:37:16.523083+00:00`. Question: `request_type`.

2 answers did not match the expected labels: `keep-product` was `refund` instead of `other`; `cancel-refund` was `order_status` instead of `refund`.

## Summary

| Metric | Value |
| --- | --- |
| Answer pairs | 12 |
| Answered | 12 |
| Labeled | 12 |
| Correct | 10 |
| Incorrect | 2 |
| Execution errors | 0 |
| Accuracy | 10/12 (83.3%) |
| Coverage | 12/12 (100%) |
| Choice Brier | 0.394375 |
| Mean inference (ms) | 37.652 |
| Load time (s) | 2.108 |

## Answers

Expected labels come from the saved run. All rows have execution status `ok`; an incorrect classification is not an execution error.

| Case | Expected | Selected | Correct | Selected probability | Choice Brier | Inference (ms) |
| --- | --- | --- | --- | --- | --- | --- |
| `refund-headphones` | refund | refund | Yes | 0.935000 | 0.005336 | 198.022 |
| `replacement-only` | replacement | replacement | Yes | 0.616862 | 0.260725 | 28.884 |
| `before-purchase` | other | other | Yes | 0.375600 | 0.538924 | 24.869 |
| `money-back` | refund | refund | Yes | 0.470400 | 0.473176 | 24.097 |
| `refund-charge` | refund | refund | Yes | 0.972400 | 0.000954 | 23.090 |
| `keep-product` | other | refund | No | 0.899610 | 1.747294 | 23.451 |
| `refund-polite` | refund | refund | Yes | 0.938894 | 0.005119 | 19.943 |
| `repair-only` | repair | repair | Yes | 0.826883 | 0.042330 | 22.769 |
| `shipping` | order_status | order_status | Yes | 0.970903 | 0.001098 | 25.348 |
| `refund-indirect` | refund | refund | Yes | 0.836816 | 0.034586 | 21.136 |
| `cancel-refund` | refund | order_status | No | 0.889289 | 1.620349 | 21.299 |
| `refund-history` | order_status | order_status | Yes | 0.957896 | 0.002613 | 18.912 |

## Probabilities

| Case | refund | replacement | repair | order_status | other |
| --- | --- | --- | --- | --- | --- |
| `refund-headphones` | 0.935000 | 0.021700 | 0.011300 | 0.016200 | 0.015800 |
| `replacement-only` | 0.336334 | 0.616862 | 0.013401 | 0.022702 | 0.010701 |
| `before-purchase` | 0.349000 | 0.118100 | 0.057100 | 0.100200 | 0.375600 |
| `money-back` | 0.470400 | 0.042000 | 0.026300 | 0.435400 | 0.025900 |
| `refund-charge` | 0.972400 | 0.007400 | 0.006600 | 0.005900 | 0.007700 |
| `keep-product` | 0.899610 | 0.023398 | 0.022098 | 0.022598 | 0.032297 |
| `refund-polite` | 0.938894 | 0.012501 | 0.033303 | 0.006601 | 0.008701 |
| `repair-only` | 0.077608 | 0.078708 | 0.826883 | 0.007601 | 0.009201 |
| `shipping` | 0.011299 | 0.009199 | 0.005199 | 0.970903 | 0.003400 |
| `refund-indirect` | 0.836816 | 0.059094 | 0.056994 | 0.030897 | 0.016198 |
| `cancel-refund` | 0.089309 | 0.008101 | 0.005601 | 0.889289 | 0.007701 |
| `refund-history` | 0.027603 | 0.003800 | 0.003500 | 0.957896 | 0.007201 |

## Native confidence fields

These are the fields returned by the model, not a common confidence scale. **Not reported** is distinct from zero.

| Case | Returned confidence | Returned answer confidence |
| --- | --- | --- |
| `refund-headphones` | 0.795600 | 0.935000 |
| `replacement-only` | 0.467500 | 0.616800 |
| `before-purchase` | 0.141700 | 0.375600 |
| `money-back` | 0.353700 | 0.470400 |
| `refund-charge` | 0.897800 | 0.972400 |
| `keep-product` | 0.711900 | 0.899700 |
| `refund-polite` | 0.812300 | 0.938800 |
| `repair-only` | 0.604800 | 0.826800 |
| `shipping` | 0.895100 | 0.971000 |
| `refund-indirect` | 0.593900 | 0.836900 |
| `cancel-refund` | 0.735400 | 0.889200 |
| `refund-history` | 0.864900 | 0.957800 |

## Model and runtime

| Field | Recorded value |
| --- | --- |
| Model key | `laya` |
| Model identifier | `convaiinnovations/laya` |
| Execution | local |
| Reported device | `mps` |
| Timing scope | Local inference call on the reported device; model loading excluded |
| Checkpoint revision | 55cf4c4ebb4ebe31b2550e8bdf3bd21b99753851 |
| Runtime: python | `3.14.7` |
| Runtime: torch | `2.14.0` |

Local timing excludes loading and includes the first inference call. No separate warm-up was recorded.

This is one small initial screen. Read the [scoring and limitations](README.md#scoring-and-limits) before using it to choose a model for a larger evaluation.
