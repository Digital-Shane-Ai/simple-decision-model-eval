# Lumma-Fev-9B

[All results and exact inputs](README.md) · [Project overview](../../README.md) · [Original JSON](comparison.json)

Captured run: `2026-10-05T11:10:07.883712+00:00`. Question: `request_type`.

All 12 answers matched the expected labels in this run.

## Summary

| Metric                  | Value          |
| ----------------------- | -------------- |
| Answer pairs            | 12             |
| Answered                | 12             |
| Labeled                 | 12             |
| Correct                 | 12             |
| Incorrect               | 0              |
| Execution errors        | 0              |
| Accuracy                | 12/12 (100.0%) |
| Coverage                | 12/12 (100%)   |
| Choice Brier            | 0.000041       |
| Log loss (nats)         | 0.001436       |
| Zero-probability truths | 0              |
| Mean inference (ms)     | 285.406        |
| Load time (s)           | 5.414          |

## Answers

Expected labels come from the saved run. All rows have execution status `ok`; an incorrect classification is not an execution error.

| Case                | Expected     | Selected     | Correct | Selected probability | Choice Brier | Log loss (nats) | Inference (ms) |
| ------------------- | ------------ | ------------ | ------- | -------------------- | ------------ | --------------- | -------------- |
| `refund-headphones` | refund       | refund       | Yes     | 0.999800             | 0.000000     | 0.000200        | 411.165        |
| `replacement-only`  | replacement  | replacement  | Yes     | 1.000000             | 0.000000     | 0.000000        | 234.621        |
| `before-purchase`   | other        | other        | Yes     | 1.000000             | 0.000000     | 0.000000        | 233.454        |
| `money-back`        | refund       | refund       | Yes     | 0.999800             | 0.000000     | 0.000200        | 326.879        |
| `refund-charge`     | refund       | refund       | Yes     | 1.000000             | 0.000000     | 0.000000        | 325.124        |
| `keep-product`      | other        | other        | Yes     | 0.999700             | 0.000000     | 0.000300        | 327.921        |
| `refund-polite`     | refund       | refund       | Yes     | 0.999700             | 0.000000     | 0.000300        | 234.932        |
| `repair-only`       | repair       | repair       | Yes     | 1.000000             | 0.000000     | 0.000000        | 324.690        |
| `shipping`          | order_status | order_status | Yes     | 1.000000             | 0.000000     | 0.000000        | 232.695        |
| `refund-indirect`   | refund       | refund       | Yes     | 0.999800             | 0.000000     | 0.000200        | 234.429        |
| `cancel-refund`     | refund       | refund       | Yes     | 0.999900             | 0.000000     | 0.000100        | 231.481        |
| `refund-history`    | order_status | order_status | Yes     | 0.984200             | 0.000493     | 0.015926        | 307.479        |

## Probabilities

| Case                | refund   | replacement | repair   | order_status | other    |
| ------------------- | -------- | ----------- | -------- | ------------ | -------- |
| `refund-headphones` | 0.999800 | 0.000100    | 0.000100 | 0.000000     | 0.000000 |
| `replacement-only`  | 0.000000 | 1.000000    | 0.000000 | 0.000000     | 0.000000 |
| `before-purchase`   | 0.000000 | 0.000000    | 0.000000 | 0.000000     | 1.000000 |
| `money-back`        | 0.999800 | 0.000200    | 0.000000 | 0.000000     | 0.000000 |
| `refund-charge`     | 1.000000 | 0.000000    | 0.000000 | 0.000000     | 0.000000 |
| `keep-product`      | 0.000000 | 0.000200    | 0.000100 | 0.000000     | 0.999700 |
| `refund-polite`     | 0.999700 | 0.000100    | 0.000200 | 0.000000     | 0.000000 |
| `repair-only`       | 0.000000 | 0.000000    | 1.000000 | 0.000000     | 0.000000 |
| `shipping`          | 0.000000 | 0.000000    | 0.000000 | 1.000000     | 0.000000 |
| `refund-indirect`   | 0.999800 | 0.000100    | 0.000100 | 0.000000     | 0.000000 |
| `cancel-refund`     | 0.999900 | 0.000000    | 0.000000 | 0.000100     | 0.000000 |
| `refund-history`    | 0.000000 | 0.000200    | 0.000000 | 0.984200     | 0.015600 |

## Native confidence fields

These are the fields returned by the model, not a common confidence scale. **Not reported** is distinct from zero.

| Case                | Returned confidence | Returned answer confidence |
| ------------------- | ------------------- | -------------------------- |
| `refund-headphones` | 0.999800            | Not reported               |
| `replacement-only`  | 0.999900            | Not reported               |
| `before-purchase`   | 1.000000            | Not reported               |
| `money-back`        | 0.999700            | Not reported               |
| `refund-charge`     | 1.000000            | Not reported               |
| `keep-product`      | 0.999600            | Not reported               |
| `refund-polite`     | 0.999600            | Not reported               |
| `repair-only`       | 0.999900            | Not reported               |
| `shipping`          | 1.000000            | Not reported               |
| `refund-indirect`   | 0.999800            | Not reported               |
| `cancel-refund`     | 0.999800            | Not reported               |
| `refund-history`    | 0.980200            | Not reported               |

## Model and runtime

| Field               | Recorded value                                                      |
| ------------------- | ------------------------------------------------------------------- |
| Model key           | `lumma9b`                                                           |
| Model identifier    | `FrontiersMind/Lumma-fev-9b`                                        |
| Execution           | local                                                               |
| Reported device     | `mps`                                                               |
| Timing scope        | Local inference call on the reported device; model loading excluded |
| Checkpoint revision | cfca86ba9cfd3696f1e0dffa8e4ba0c385f0670e                            |
| Runtime: python     | `3.13.15`                                                           |
| Runtime: torch      | `2.8.0`                                                             |

Local timing excludes loading and includes the first inference call. No separate warm-up was recorded.

This is one small initial screen. Read the [scoring and limitations](README.md#scoring-and-limits) before using it to choose a model for a larger evaluation.
