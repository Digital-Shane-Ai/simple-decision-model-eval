# Lumma-Fev-4B

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
| Choice Brier            | 0.017443       |
| Log loss (nats)         | 0.038638       |
| Zero-probability truths | 0              |
| Mean inference (ms)     | 275.884        |
| Load time (s)           | 4.614          |

## Answers

Expected labels come from the saved run. All rows have execution status `ok`; an incorrect classification is not an execution error.

| Case                | Expected     | Selected     | Correct | Selected probability | Choice Brier | Log loss (nats) | Inference (ms) |
| ------------------- | ------------ | ------------ | ------- | -------------------- | ------------ | --------------- | -------------- |
| `refund-headphones` | refund       | refund       | Yes     | 0.985200             | 0.000421     | 0.014911        | 419.601        |
| `replacement-only`  | replacement  | replacement  | Yes     | 0.998200             | 0.000006     | 0.001802        | 219.834        |
| `before-purchase`   | other        | other        | Yes     | 1.000000             | 0.000000     | 0.000000        | 230.878        |
| `money-back`        | refund       | refund       | Yes     | 0.999900             | 0.000000     | 0.000100        | 313.320        |
| `refund-charge`     | refund       | refund       | Yes     | 1.000000             | 0.000000     | 0.000000        | 307.579        |
| `keep-product`      | other        | other        | Yes     | 0.964100             | 0.002307     | 0.036560        | 315.413        |
| `refund-polite`     | refund       | refund       | Yes     | 0.673933             | 0.206377     | 0.394625        | 235.460        |
| `repair-only`       | repair       | repair       | Yes     | 0.999600             | 0.000000     | 0.000400        | 316.470        |
| `shipping`          | order_status | order_status | Yes     | 0.999400             | 0.000001     | 0.000600        | 226.183        |
| `refund-indirect`   | refund       | refund       | Yes     | 0.994500             | 0.000058     | 0.005515        | 222.069        |
| `cancel-refund`     | refund       | refund       | Yes     | 0.999500             | 0.000000     | 0.000500        | 220.320        |
| `refund-history`    | order_status | order_status | Yes     | 0.991400             | 0.000148     | 0.008637        | 283.484        |

## Probabilities

| Case                | refund   | replacement | repair   | order_status | other    |
| ------------------- | -------- | ----------- | -------- | ------------ | -------- |
| `refund-headphones` | 0.985200 | 0.000500    | 0.014200 | 0.000000     | 0.000100 |
| `replacement-only`  | 0.000000 | 0.998200    | 0.001800 | 0.000000     | 0.000000 |
| `before-purchase`   | 0.000000 | 0.000000    | 0.000000 | 0.000000     | 1.000000 |
| `money-back`        | 0.999900 | 0.000100    | 0.000000 | 0.000000     | 0.000000 |
| `refund-charge`     | 1.000000 | 0.000000    | 0.000000 | 0.000000     | 0.000000 |
| `keep-product`      | 0.001400 | 0.002000    | 0.031800 | 0.000700     | 0.964100 |
| `refund-polite`     | 0.673933 | 0.009699    | 0.316168 | 0.000000     | 0.000200 |
| `repair-only`       | 0.000000 | 0.000000    | 0.999600 | 0.000000     | 0.000400 |
| `shipping`          | 0.000000 | 0.000000    | 0.000000 | 0.999400     | 0.000600 |
| `refund-indirect`   | 0.994500 | 0.000200    | 0.005300 | 0.000000     | 0.000000 |
| `cancel-refund`     | 0.999500 | 0.000000    | 0.000000 | 0.000500     | 0.000000 |
| `refund-history`    | 0.000000 | 0.000000    | 0.000000 | 0.991400     | 0.008600 |

## Native confidence fields

These are the fields returned by the model, not a common confidence scale. **Not reported** is distinct from zero.

| Case                | Returned confidence | Returned answer confidence |
| ------------------- | ------------------- | -------------------------- |
| `refund-headphones` | 0.981500            | Not reported               |
| `replacement-only`  | 0.997800            | Not reported               |
| `before-purchase`   | 1.000000            | Not reported               |
| `money-back`        | 0.999800            | Not reported               |
| `refund-charge`     | 0.999900            | Not reported               |
| `keep-product`      | 0.955200            | Not reported               |
| `refund-polite`     | 0.592500            | Not reported               |
| `repair-only`       | 0.999500            | Not reported               |
| `shipping`          | 0.999200            | Not reported               |
| `refund-indirect`   | 0.993100            | Not reported               |
| `cancel-refund`     | 0.999300            | Not reported               |
| `refund-history`    | 0.989300            | Not reported               |

## Model and runtime

| Field               | Recorded value                                                      |
| ------------------- | ------------------------------------------------------------------- |
| Model key           | `lumma`                                                             |
| Model identifier    | `FrontiersMind/Lumma-fev-4b`                                        |
| Execution           | local                                                               |
| Reported device     | `mps`                                                               |
| Timing scope        | Local inference call on the reported device; model loading excluded |
| Checkpoint revision | bc5418792f2d4d0a5596776522b6b6a206507d96                            |
| Runtime: python     | `3.13.15`                                                           |
| Runtime: torch      | `2.8.0`                                                             |

Local timing excludes loading and includes the first inference call. No separate warm-up was recorded.

This is one small initial screen. Read the [scoring and limitations](README.md#scoring-and-limits) before using it to choose a model for a larger evaluation.
