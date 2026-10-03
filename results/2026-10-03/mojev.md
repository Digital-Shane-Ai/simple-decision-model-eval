# MoJev

[All results and exact inputs](README.md) · [Project overview](../../README.md) · [Original JSON](comparison.json)

Captured run: `2026-10-03T10:37:16.523083+00:00`. Question: `request_type`.

1 answer did not match the expected labels: `refund-history` was `refund` instead of `order_status`.

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
| Choice Brier | 0.104383 |
| Mean inference (ms) | 136.051 |
| Load time (s) | 2.796 |

## Answers

Expected labels come from the saved run. All rows have execution status `ok`; an incorrect classification is not an execution error.

| Case | Expected | Selected | Correct | Selected probability | Choice Brier | Inference (ms) |
| --- | --- | --- | --- | --- | --- | --- |
| `refund-headphones` | refund | refund | Yes | 0.998801 | 0.000002 | 212.205 |
| `replacement-only` | replacement | replacement | Yes | 0.926681 | 0.010621 | 131.164 |
| `before-purchase` | other | other | Yes | 0.977027 | 0.000846 | 124.677 |
| `money-back` | refund | refund | Yes | 0.997646 | 0.000008 | 145.165 |
| `refund-charge` | refund | refund | Yes | 0.999049 | 0.000001 | 158.556 |
| `keep-product` | other | other | Yes | 0.913650 | 0.010705 | 130.922 |
| `refund-polite` | refund | refund | Yes | 0.979107 | 0.000770 | 132.904 |
| `repair-only` | repair | repair | Yes | 0.987549 | 0.000215 | 124.616 |
| `shipping` | order_status | order_status | Yes | 0.919130 | 0.009568 | 130.131 |
| `refund-indirect` | refund | refund | Yes | 0.993267 | 0.000078 | 128.518 |
| `cancel-refund` | refund | refund | Yes | 0.999078 | 0.000001 | 127.819 |
| `refund-history` | order_status | refund | No | 0.761030 | 1.219779 | 85.937 |

## Probabilities

| Case | refund | replacement | repair | order_status | other |
| --- | --- | --- | --- | --- | --- |
| `refund-headphones` | 0.998801 | 0.000451 | 0.000323 | 0.000046 | 0.000379 |
| `replacement-only` | 0.000709 | 0.926681 | 0.072422 | 0.000058 | 0.000130 |
| `before-purchase` | 0.000227 | 0.017437 | 0.002413 | 0.002896 | 0.977027 |
| `money-back` | 0.997646 | 0.001319 | 0.000431 | 0.000090 | 0.000513 |
| `refund-charge` | 0.999049 | 0.000508 | 0.000244 | 0.000035 | 0.000164 |
| `keep-product` | 0.002803 | 0.049134 | 0.028043 | 0.006369 | 0.913650 |
| `refund-polite` | 0.979107 | 0.002038 | 0.018123 | 0.000078 | 0.000654 |
| `repair-only` | 0.000483 | 0.005494 | 0.987549 | 0.001191 | 0.005283 |
| `shipping` | 0.000171 | 0.042875 | 0.003512 | 0.919130 | 0.034311 |
| `refund-indirect` | 0.993267 | 0.005686 | 0.000554 | 0.000077 | 0.000416 |
| `cancel-refund` | 0.999078 | 0.000340 | 0.000217 | 0.000194 | 0.000170 |
| `refund-history` | 0.761030 | 0.009311 | 0.001831 | 0.200152 | 0.027676 |

## Native confidence fields

These are the fields returned by the model, not a common confidence scale. **Not reported** is distinct from zero.

| Case | Returned confidence | Returned answer confidence |
| --- | --- | --- |
| `refund-headphones` | 0.998801 | Not reported |
| `replacement-only` | 0.926681 | Not reported |
| `before-purchase` | 0.977027 | Not reported |
| `money-back` | 0.997646 | Not reported |
| `refund-charge` | 0.999049 | Not reported |
| `keep-product` | 0.913650 | Not reported |
| `refund-polite` | 0.979107 | Not reported |
| `repair-only` | 0.987549 | Not reported |
| `shipping` | 0.919131 | Not reported |
| `refund-indirect` | 0.993267 | Not reported |
| `cancel-refund` | 0.999078 | Not reported |
| `refund-history` | 0.761030 | Not reported |

## Model and runtime

| Field | Recorded value |
| --- | --- |
| Model key | `mojev` |
| Model identifier | `MoLeMo-Lab/mojev` |
| Execution | local |
| Reported device | `mps` |
| Timing scope | Local inference call on the reported device; model loading excluded |
| Checkpoint revision | 0c8695b6252f4205907433d4e196a94f032e60c3 |
| Source repository | `https://github.com/MoLeMo-Lab/mojev` |
| Source revision | a74d58cd19ec573e83e8e27f9fecd837b8d830fb |
| Runtime: python | `3.13.15` |
| Runtime: torch | `2.8.0` |

Local timing excludes loading and includes the first inference call. No separate warm-up was recorded.

This is one small initial screen. Read the [scoring and limitations](README.md#scoring-and-limits) before using it to choose a model for a larger evaluation.
