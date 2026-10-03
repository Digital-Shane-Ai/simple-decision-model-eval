# Kev-4B

[All results and exact inputs](README.md) · [Project overview](../../README.md) · [Original JSON](comparison.json)

Captured run: `2026-10-03T10:37:16.523083+00:00`. Question: `request_type`.

1 answer did not match the expected labels: `refund-history` was `other` instead of `order_status`.

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
| Choice Brier | 0.085338 |
| Mean inference (ms) | 68.711 |
| Load time (s) | 6.075 |

## Answers

Expected labels come from the saved run. All rows have execution status `ok`; an incorrect classification is not an execution error.

| Case | Expected | Selected | Correct | Selected probability | Choice Brier | Inference (ms) |
| --- | --- | --- | --- | --- | --- | --- |
| `refund-headphones` | refund | refund | Yes | 0.795100 | 0.064030 | 99.390 |
| `replacement-only` | replacement | replacement | Yes | 0.957900 | 0.002844 | 69.262 |
| `before-purchase` | other | other | Yes | 0.985700 | 0.000258 | 68.806 |
| `money-back` | refund | refund | Yes | 0.908400 | 0.014141 | 68.895 |
| `refund-charge` | refund | refund | Yes | 0.776922 | 0.095327 | 69.044 |
| `keep-product` | other | other | Yes | 0.795180 | 0.053130 | 69.266 |
| `refund-polite` | refund | refund | Yes | 0.897200 | 0.015645 | 68.932 |
| `repair-only` | repair | repair | Yes | 0.924808 | 0.010231 | 68.885 |
| `shipping` | order_status | order_status | Yes | 0.806219 | 0.067526 | 59.974 |
| `refund-indirect` | refund | refund | Yes | 0.917400 | 0.010801 | 56.191 |
| `cancel-refund` | refund | refund | Yes | 0.927500 | 0.009519 | 56.534 |
| `refund-history` | order_status | other | No | 0.563500 | 0.680605 | 69.347 |

## Probabilities

| Case | refund | replacement | repair | order_status | other |
| --- | --- | --- | --- | --- | --- |
| `refund-headphones` | 0.795100 | 0.033400 | 0.022300 | 0.006400 | 0.142800 |
| `replacement-only` | 0.002000 | 0.957900 | 0.007000 | 0.001200 | 0.031900 |
| `before-purchase` | 0.003900 | 0.004400 | 0.002500 | 0.003500 | 0.985700 |
| `money-back` | 0.908400 | 0.012700 | 0.002000 | 0.002200 | 0.074700 |
| `refund-charge` | 0.776922 | 0.004200 | 0.002600 | 0.002900 | 0.213379 |
| `keep-product` | 0.050705 | 0.053305 | 0.068907 | 0.031903 | 0.795180 |
| `refund-polite` | 0.897200 | 0.019700 | 0.015000 | 0.001300 | 0.066800 |
| `repair-only` | 0.002800 | 0.003500 | 0.924808 | 0.001400 | 0.067493 |
| `shipping` | 0.009399 | 0.009899 | 0.001900 | 0.806219 | 0.172583 |
| `refund-indirect` | 0.917400 | 0.011000 | 0.008500 | 0.001600 | 0.061500 |
| `cancel-refund` | 0.927500 | 0.002000 | 0.001000 | 0.004400 | 0.065100 |
| `refund-history` | 0.012400 | 0.022400 | 0.003700 | 0.398000 | 0.563500 |

## Native confidence fields

These are the fields returned by the model, not a common confidence scale. **Not reported** is distinct from zero.

| Case | Returned confidence | Returned answer confidence |
| --- | --- | --- |
| `refund-headphones` | 0.743900 | Not reported |
| `replacement-only` | 0.947400 | Not reported |
| `before-purchase` | 0.982200 | Not reported |
| `money-back` | 0.885500 | Not reported |
| `refund-charge` | 0.721200 | Not reported |
| `keep-product` | 0.743900 | Not reported |
| `refund-polite` | 0.871400 | Not reported |
| `repair-only` | 0.906100 | Not reported |
| `shipping` | 0.757900 | Not reported |
| `refund-indirect` | 0.896800 | Not reported |
| `cancel-refund` | 0.909300 | Not reported |
| `refund-history` | 0.454400 | Not reported |

## Model and runtime

| Field | Recorded value |
| --- | --- |
| Model key | `kev` |
| Model identifier | `jaredpalmer/kev-4b` |
| Execution | local |
| Reported device | `mlx:gpu` |
| Timing scope | Local inference call on the reported device; model loading excluded |
| Checkpoint revision | 139fdd94f1b6a6ad80cc15e08fcb99cac885a101 |
| Source repository | `https://github.com/jaredpalmer/kev` |
| Source revision | 0c142becde423a0c68ec857f7831dac0315588a1 |
| Runtime: python | `3.13.15` |
| Runtime: torch | `2.8.0` |

Local timing excludes loading and includes the first inference call. No separate warm-up was recorded.

This is one small initial screen. Read the [scoring and limitations](README.md#scoring-and-limits) before using it to choose a model for a larger evaluation.
