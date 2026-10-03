# Kev-9B

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
| Choice Brier | 0.060004 |
| Mean inference (ms) | 111.065 |
| Load time (s) | 6.576 |

## Answers

Expected labels come from the saved run. All rows have execution status `ok`; an incorrect classification is not an execution error.

| Case | Expected | Selected | Correct | Selected probability | Choice Brier | Inference (ms) |
| --- | --- | --- | --- | --- | --- | --- |
| `refund-headphones` | refund | refund | Yes | 0.953300 | 0.002872 | 138.307 |
| `replacement-only` | replacement | replacement | Yes | 0.987601 | 0.000223 | 113.616 |
| `before-purchase` | other | other | Yes | 0.965400 | 0.001500 | 113.139 |
| `money-back` | refund | refund | Yes | 0.926700 | 0.007427 | 113.854 |
| `refund-charge` | refund | refund | Yes | 0.942300 | 0.004820 | 112.754 |
| `keep-product` | other | other | Yes | 0.927600 | 0.006630 | 113.895 |
| `refund-polite` | refund | refund | Yes | 0.976298 | 0.000732 | 112.938 |
| `repair-only` | repair | repair | Yes | 0.975600 | 0.000858 | 113.212 |
| `shipping` | order_status | order_status | Yes | 0.799320 | 0.065266 | 96.314 |
| `refund-indirect` | refund | refund | Yes | 0.986199 | 0.000247 | 95.129 |
| `cancel-refund` | refund | refund | Yes | 0.959800 | 0.002288 | 94.966 |
| `refund-history` | order_status | other | No | 0.421300 | 0.627179 | 114.655 |

## Probabilities

| Case | refund | replacement | repair | order_status | other |
| --- | --- | --- | --- | --- | --- |
| `refund-headphones` | 0.953300 | 0.012400 | 0.012300 | 0.002500 | 0.019500 |
| `replacement-only` | 0.001000 | 0.987601 | 0.007699 | 0.000700 | 0.003000 |
| `before-purchase` | 0.008500 | 0.010300 | 0.008100 | 0.007700 | 0.965400 |
| `money-back` | 0.926700 | 0.016500 | 0.010200 | 0.006100 | 0.040500 |
| `refund-charge` | 0.942300 | 0.011200 | 0.006000 | 0.004300 | 0.036200 |
| `keep-product` | 0.016200 | 0.021700 | 0.022700 | 0.011800 | 0.927600 |
| `refund-polite` | 0.976298 | 0.007001 | 0.006301 | 0.001500 | 0.008901 |
| `repair-only` | 0.002200 | 0.005100 | 0.975600 | 0.002000 | 0.015100 |
| `shipping` | 0.015898 | 0.017898 | 0.010999 | 0.799320 | 0.155884 |
| `refund-indirect` | 0.986199 | 0.004500 | 0.003200 | 0.001100 | 0.005001 |
| `cancel-refund` | 0.959800 | 0.007800 | 0.004300 | 0.004100 | 0.024000 |
| `refund-history` | 0.058400 | 0.124600 | 0.050100 | 0.345600 | 0.421300 |

## Native confidence fields

These are the fields returned by the model, not a common confidence scale. **Not reported** is distinct from zero.

| Case | Returned confidence | Returned answer confidence |
| --- | --- | --- |
| `refund-headphones` | 0.941600 | Not reported |
| `replacement-only` | 0.984600 | Not reported |
| `before-purchase` | 0.956800 | Not reported |
| `money-back` | 0.908300 | Not reported |
| `refund-charge` | 0.927800 | Not reported |
| `keep-product` | 0.909500 | Not reported |
| `refund-polite` | 0.970300 | Not reported |
| `repair-only` | 0.969500 | Not reported |
| `shipping` | 0.749300 | Not reported |
| `refund-indirect` | 0.982600 | Not reported |
| `cancel-refund` | 0.949800 | Not reported |
| `refund-history` | 0.276700 | Not reported |

## Model and runtime

| Field | Recorded value |
| --- | --- |
| Model key | `kev9b` |
| Model identifier | `jaredpalmer/kev-9b` |
| Execution | local |
| Reported device | `mlx:gpu` |
| Timing scope | Local inference call on the reported device; model loading excluded |
| Checkpoint revision | 2629c06a5aeb0feb3b9783bafed17ed8f39ecf5c |
| Source repository | `https://github.com/jaredpalmer/kev` |
| Source revision | 0c142becde423a0c68ec857f7831dac0315588a1 |
| Runtime: python | `3.13.15` |
| Runtime: torch | `2.8.0` |

Local timing excludes loading and includes the first inference call. No separate warm-up was recorded.

This is one small initial screen. Read the [scoring and limitations](README.md#scoring-and-limits) before using it to choose a model for a larger evaluation.
