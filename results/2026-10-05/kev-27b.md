# Kev-27B

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
| Choice Brier            | 0.001037       |
| Log loss (nats)         | 0.020332       |
| Zero-probability truths | 0              |
| Mean inference (ms)     | 449.118        |
| Load time (s)           | 26.595         |

## Answers

Expected labels come from the saved run. All rows have execution status `ok`; an incorrect classification is not an execution error.

| Case                | Expected     | Selected     | Correct | Selected probability | Choice Brier | Log loss (nats) | Inference (ms) |
| ------------------- | ------------ | ------------ | ------- | -------------------- | ------------ | --------------- | -------------- |
| `refund-headphones` | refund       | refund       | Yes     | 0.964696             | 0.001807     | 0.035942        | 1309.076       |
| `replacement-only`  | replacement  | replacement  | Yes     | 0.988900             | 0.000178     | 0.011162        | 391.171        |
| `before-purchase`   | other        | other        | Yes     | 0.995000             | 0.000031     | 0.005013        | 384.791        |
| `money-back`        | refund       | refund       | Yes     | 0.984298             | 0.000342     | 0.015826        | 384.457        |
| `refund-charge`     | refund       | refund       | Yes     | 0.979702             | 0.000690     | 0.020507        | 393.818        |
| `keep-product`      | other        | other        | Yes     | 0.976100             | 0.000758     | 0.024190        | 388.810        |
| `refund-polite`     | refund       | refund       | Yes     | 0.989800             | 0.000137     | 0.010252        | 384.400        |
| `repair-only`       | repair       | repair       | Yes     | 0.979598             | 0.000618     | 0.020613        | 386.737        |
| `shipping`          | order_status | order_status | Yes     | 0.977300             | 0.000857     | 0.022962        | 331.877        |
| `refund-indirect`   | refund       | refund       | Yes     | 0.994700             | 0.000038     | 0.005314        | 325.016        |
| `cancel-refund`     | refund       | refund       | Yes     | 0.992899             | 0.000069     | 0.007126        | 324.296        |
| `refund-history`    | order_status | order_status | Yes     | 0.936994             | 0.006920     | 0.065079        | 384.969        |

## Probabilities

| Case                | refund   | replacement | repair   | order_status | other    |
| ------------------- | -------- | ----------- | -------- | ------------ | -------- |
| `refund-headphones` | 0.964696 | 0.021902    | 0.005701 | 0.000800     | 0.006901 |
| `replacement-only`  | 0.001000 | 0.988900    | 0.006700 | 0.000500     | 0.002900 |
| `before-purchase`   | 0.001300 | 0.001100    | 0.001600 | 0.001000     | 0.995000 |
| `money-back`        | 0.984298 | 0.005901    | 0.001500 | 0.000700     | 0.007601 |
| `refund-charge`     | 0.979702 | 0.001900    | 0.001400 | 0.000500     | 0.016498 |
| `keep-product`      | 0.007100 | 0.003900    | 0.010800 | 0.002100     | 0.976100 |
| `refund-polite`     | 0.989800 | 0.003200    | 0.002900 | 0.000400     | 0.003700 |
| `repair-only`       | 0.002300 | 0.003600    | 0.979598 | 0.001000     | 0.013501 |
| `shipping`          | 0.001500 | 0.001900    | 0.001000 | 0.977300     | 0.018300 |
| `refund-indirect`   | 0.994700 | 0.001600    | 0.001000 | 0.000200     | 0.002500 |
| `cancel-refund`     | 0.992899 | 0.000900    | 0.000600 | 0.002000     | 0.003600 |
| `refund-history`    | 0.002700 | 0.005001    | 0.001300 | 0.936994     | 0.054005 |

## Native confidence fields

These are the fields returned by the model, not a common confidence scale. **Not reported** is distinct from zero.

| Case                | Returned confidence | Returned answer confidence |
| ------------------- | ------------------- | -------------------------- |
| `refund-headphones` | 0.955700            | Not reported               |
| `replacement-only`  | 0.986200            | Not reported               |
| `before-purchase`   | 0.993800            | Not reported               |
| `money-back`        | 0.980300            | Not reported               |
| `refund-charge`     | 0.974800            | Not reported               |
| `keep-product`      | 0.970100            | Not reported               |
| `refund-polite`     | 0.987300            | Not reported               |
| `repair-only`       | 0.974300            | Not reported               |
| `shipping`          | 0.971700            | Not reported               |
| `refund-indirect`   | 0.993400            | Not reported               |
| `cancel-refund`     | 0.991100            | Not reported               |
| `refund-history`    | 0.921200            | Not reported               |

## Model and runtime

| Field               | Recorded value                                                      |
| ------------------- | ------------------------------------------------------------------- |
| Model key           | `kev27b`                                                            |
| Model identifier    | `jaredpalmer/kev-27b`                                               |
| Execution           | local                                                               |
| Reported device     | `mlx:gpu`                                                           |
| Timing scope        | Local inference call on the reported device; model loading excluded |
| Checkpoint revision | 01b81998019be550f0ae858727df49bac9511195                            |
| Source repository   | `https://github.com/jaredpalmer/kev`                                |
| Source revision     | 0c142becde423a0c68ec857f7831dac0315588a1                            |
| Runtime: python     | `3.13.15`                                                           |
| Runtime: torch      | `2.8.0`                                                             |

Local timing excludes loading and includes the first inference call. No separate warm-up was recorded.

This is one small initial screen. Read the [scoring and limitations](README.md#scoring-and-limits) before using it to choose a model for a larger evaluation.
