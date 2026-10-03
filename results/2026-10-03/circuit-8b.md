# Circuit-8B

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
| Choice Brier | 0.000473 |
| Mean inference (ms) | 106.555 |
| Load time (s) | 5.627 |

## Answers

Expected labels come from the saved run. All rows have execution status `ok`; an incorrect classification is not an execution error.

| Case | Expected | Selected | Correct | Selected probability | Choice Brier | Inference (ms) |
| --- | --- | --- | --- | --- | --- | --- |
| `refund-headphones` | refund | refund | Yes | 0.970080 | 0.001325 | 218.136 |
| `replacement-only` | replacement | replacement | Yes | 0.999886 | 0.000000 | 97.860 |
| `before-purchase` | other | other | Yes | 0.998860 | 0.000002 | 95.431 |
| `money-back` | refund | refund | Yes | 0.998747 | 0.000003 | 99.492 |
| `refund-charge` | refund | refund | Yes | 0.999889 | 0.000000 | 99.333 |
| `keep-product` | other | other | Yes | 0.985600 | 0.000284 | 100.763 |
| `refund-polite` | refund | refund | Yes | 0.950760 | 0.004049 | 96.886 |
| `repair-only` | repair | repair | Yes | 0.999937 | 0.000000 | 95.948 |
| `shipping` | order_status | order_status | Yes | 0.999983 | 0.000000 | 94.026 |
| `refund-indirect` | refund | refund | Yes | 0.996814 | 0.000015 | 93.980 |
| `cancel-refund` | refund | refund | Yes | 0.999480 | 0.000000 | 94.023 |
| `refund-history` | order_status | order_status | Yes | 0.999689 | 0.000000 | 92.777 |

## Probabilities

| Case | refund | replacement | repair | order_status | other |
| --- | --- | --- | --- | --- | --- |
| `refund-headphones` | 0.970080 | 0.013897 | 0.015371 | 0.000025 | 0.000627 |
| `replacement-only` | 0.000003 | 0.999886 | 0.000104 | 0.000001 | 0.000007 |
| `before-purchase` | 0.000551 | 0.000334 | 0.000175 | 0.000081 | 0.998860 |
| `money-back` | 0.998747 | 0.001206 | 0.000025 | 0.000005 | 0.000017 |
| `refund-charge` | 0.999889 | 0.000047 | 0.000026 | 0.000002 | 0.000036 |
| `keep-product` | 0.002956 | 0.004468 | 0.006957 | 0.000019 | 0.985600 |
| `refund-polite` | 0.950760 | 0.009739 | 0.039110 | 0.000013 | 0.000378 |
| `repair-only` | 0.000005 | 0.000019 | 0.999937 | 0.000000 | 0.000039 |
| `shipping` | 0.000003 | 0.000005 | 0.000002 | 0.999983 | 0.000008 |
| `refund-indirect` | 0.996814 | 0.001644 | 0.001485 | 0.000002 | 0.000055 |
| `cancel-refund` | 0.999480 | 0.000142 | 0.000041 | 0.000255 | 0.000082 |
| `refund-history` | 0.000049 | 0.000021 | 0.000005 | 0.999689 | 0.000235 |

## Native confidence fields

These are the fields returned by the model, not a common confidence scale. **Not reported** is distinct from zero.

| Case | Returned confidence | Returned answer confidence |
| --- | --- | --- |
| `refund-headphones` | Not reported | Not reported |
| `replacement-only` | Not reported | Not reported |
| `before-purchase` | Not reported | Not reported |
| `money-back` | Not reported | Not reported |
| `refund-charge` | Not reported | Not reported |
| `keep-product` | Not reported | Not reported |
| `refund-polite` | Not reported | Not reported |
| `repair-only` | Not reported | Not reported |
| `shipping` | Not reported | Not reported |
| `refund-indirect` | Not reported | Not reported |
| `cancel-refund` | Not reported | Not reported |
| `refund-history` | Not reported | Not reported |

## Model and runtime

| Field | Recorded value |
| --- | --- |
| Model key | `circuit8b` |
| Model identifier | `jbarney/circuit-8b` |
| Execution | local |
| Reported device | `mps` |
| Timing scope | Local inference call on the reported device; model loading excluded |
| Checkpoint revision | f64b4596186aac7bd45c9415cdeb4090fd83a648 |
| Source repository | `https://github.com/Barneyjm/circuit` |
| Source revision | ef47613f6699a4b0deb63ddab1cddcdb4ed7f68a |
| Base model | `Qwen/Qwen3-8B-Base` |
| Base revision | 49e3418fbbbca6ecbdf9608b4d22e5a407081db4 |
| Configured environment | `.venv-modern` |
| Runtime: python | `3.13.15` |
| Runtime: torch | `2.14.0` |

Local timing excludes loading and includes the first inference call. No separate warm-up was recorded.

This is one small initial screen. Read the [scoring and limitations](README.md#scoring-and-limits) before using it to choose a model for a larger evaluation.
