# WEV-8B

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
| Choice Brier | 0.002407 |
| Mean inference (ms) | 225.937 |
| Load time (s) | 7.875 |

## Answers

Expected labels come from the saved run. All rows have execution status `ok`; an incorrect classification is not an execution error.

| Case | Expected | Selected | Correct | Selected probability | Choice Brier | Inference (ms) |
| --- | --- | --- | --- | --- | --- | --- |
| `refund-headphones` | refund | refund | Yes | 0.997800 | 0.000007 | 301.759 |
| `replacement-only` | replacement | replacement | Yes | 0.998700 | 0.000003 | 207.436 |
| `before-purchase` | other | other | Yes | 0.998600 | 0.000003 | 229.254 |
| `money-back` | refund | refund | Yes | 0.998100 | 0.000006 | 254.989 |
| `refund-charge` | refund | refund | Yes | 0.999900 | 0.000000 | 241.026 |
| `keep-product` | other | other | Yes | 0.996400 | 0.000020 | 241.281 |
| `refund-polite` | refund | refund | Yes | 0.992600 | 0.000081 | 196.923 |
| `repair-only` | repair | repair | Yes | 0.999600 | 0.000000 | 228.137 |
| `shipping` | order_status | order_status | Yes | 0.996700 | 0.000022 | 211.726 |
| `refund-indirect` | refund | refund | Yes | 0.998900 | 0.000002 | 195.916 |
| `cancel-refund` | refund | refund | Yes | 0.999100 | 0.000001 | 199.988 |
| `refund-history` | order_status | order_status | Yes | 0.879288 | 0.028737 | 202.809 |

## Probabilities

| Case | refund | replacement | repair | order_status | other |
| --- | --- | --- | --- | --- | --- |
| `refund-headphones` | 0.997800 | 0.001400 | 0.000500 | 0.000000 | 0.000300 |
| `replacement-only` | 0.000000 | 0.998700 | 0.001200 | 0.000000 | 0.000100 |
| `before-purchase` | 0.000100 | 0.000200 | 0.000000 | 0.001100 | 0.998600 |
| `money-back` | 0.998100 | 0.001500 | 0.000000 | 0.000000 | 0.000400 |
| `refund-charge` | 0.999900 | 0.000000 | 0.000000 | 0.000000 | 0.000100 |
| `keep-product` | 0.002600 | 0.000500 | 0.000300 | 0.000200 | 0.996400 |
| `refund-polite` | 0.992600 | 0.003000 | 0.004200 | 0.000000 | 0.000200 |
| `repair-only` | 0.000000 | 0.000000 | 0.999600 | 0.000000 | 0.000400 |
| `shipping` | 0.000000 | 0.000000 | 0.000000 | 0.996700 | 0.003300 |
| `refund-indirect` | 0.998900 | 0.000800 | 0.000200 | 0.000000 | 0.000100 |
| `cancel-refund` | 0.999100 | 0.000100 | 0.000000 | 0.000400 | 0.000400 |
| `refund-history` | 0.001200 | 0.000500 | 0.000000 | 0.879288 | 0.119012 |

## Native confidence fields

These are the fields returned by the model, not a common confidence scale. **Not reported** is distinct from zero.

| Case | Returned confidence | Returned answer confidence |
| --- | --- | --- |
| `refund-headphones` | 0.997200 | Not reported |
| `replacement-only` | 0.998200 | Not reported |
| `before-purchase` | 0.998200 | Not reported |
| `money-back` | 0.997700 | Not reported |
| `refund-charge` | 0.999800 | Not reported |
| `keep-product` | 0.995500 | Not reported |
| `refund-polite` | 0.990800 | Not reported |
| `repair-only` | 0.999400 | Not reported |
| `shipping` | 0.995800 | Not reported |
| `refund-indirect` | 0.998600 | Not reported |
| `cancel-refund` | 0.999000 | Not reported |
| `refund-history` | 0.849000 | Not reported |

## Model and runtime

| Field | Recorded value |
| --- | --- |
| Model key | `wev8b` |
| Model identifier | `alanhuangya/wev-8b` |
| Execution | local |
| Reported device | `mps:0` |
| Timing scope | Local inference call on the reported device; model loading excluded |
| Checkpoint revision | 813fb695bb37bc254d977710daf4f301819200d3 |
| Source repository | `https://github.com/alanhuangyoo/wev` |
| Source revision | a4dc555e152f58f9b818c4a08082188007bd5348 |
| Configured environment | `.venv-wev` |
| Runtime: python | `3.13.15` |
| Runtime: torch | `2.8.0` |

Local timing excludes loading and includes the first inference call. No separate warm-up was recorded.

This is one small initial screen. Read the [scoring and limitations](README.md#scoring-and-limits) before using it to choose a model for a larger evaluation.
