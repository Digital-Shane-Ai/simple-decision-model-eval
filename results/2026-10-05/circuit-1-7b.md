# Circuit-1.7B

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
| Choice Brier            | 0.051119       |
| Log loss (nats)         | 0.126921       |
| Zero-probability truths | 0              |
| Mean inference (ms)     | 49.668         |
| Load time (s)           | 3.454          |

## Answers

Expected labels come from the saved run. All rows have execution status `ok`; an incorrect classification is not an execution error.

| Case                | Expected     | Selected     | Correct | Selected probability | Choice Brier | Log loss (nats) | Inference (ms) |
| ------------------- | ------------ | ------------ | ------- | -------------------- | ------------ | --------------- | -------------- |
| `refund-headphones` | refund       | refund       | Yes     | 0.894201             | 0.019526     | 0.111825        | 116.180        |
| `replacement-only`  | replacement  | replacement  | Yes     | 0.943449             | 0.006234     | 0.058213        | 48.275         |
| `before-purchase`   | other        | other        | Yes     | 0.996709             | 0.000014     | 0.003296        | 44.743         |
| `money-back`        | refund       | refund       | Yes     | 0.927599             | 0.008761     | 0.075156        | 46.063         |
| `refund-charge`     | refund       | refund       | Yes     | 0.993892             | 0.000053     | 0.006127        | 43.298         |
| `keep-product`      | other        | other        | Yes     | 0.454384             | 0.467789     | 0.788812        | 42.447         |
| `refund-polite`     | refund       | refund       | Yes     | 0.903618             | 0.015306     | 0.101348        | 41.873         |
| `repair-only`       | repair       | repair       | Yes     | 0.985181             | 0.000399     | 0.014930        | 44.759         |
| `shipping`          | order_status | order_status | Yes     | 0.993828             | 0.000074     | 0.006191        | 43.208         |
| `refund-indirect`   | refund       | refund       | Yes     | 0.774487             | 0.082740     | 0.255555        | 42.580         |
| `cancel-refund`     | refund       | refund       | Yes     | 0.989010             | 0.000186     | 0.011051        | 42.047         |
| `refund-history`    | order_status | order_status | Yes     | 0.913424             | 0.012350     | 0.090556        | 40.544         |

## Probabilities

| Case                | refund   | replacement | repair   | order_status | other    |
| ------------------- | -------- | ----------- | -------- | ------------ | -------- |
| `refund-headphones` | 0.894201 | 0.090637    | 0.009197 | 0.000266     | 0.005699 |
| `replacement-only`  | 0.000716 | 0.943449    | 0.055092 | 0.000017     | 0.000726 |
| `before-purchase`   | 0.000688 | 0.001351    | 0.000810 | 0.000441     | 0.996709 |
| `money-back`        | 0.927599 | 0.058528    | 0.003966 | 0.001155     | 0.008753 |
| `refund-charge`     | 0.993892 | 0.002117    | 0.000611 | 0.000119     | 0.003260 |
| `keep-product`      | 0.136844 | 0.388536    | 0.020143 | 0.000092     | 0.454384 |
| `refund-polite`     | 0.903618 | 0.017961    | 0.075404 | 0.000074     | 0.002943 |
| `repair-only`       | 0.000306 | 0.001149    | 0.985181 | 0.000010     | 0.013353 |
| `shipping`          | 0.000067 | 0.000100    | 0.000053 | 0.993828     | 0.005952 |
| `refund-indirect`   | 0.774487 | 0.174688    | 0.031793 | 0.000133     | 0.018899 |
| `cancel-refund`     | 0.989010 | 0.007847    | 0.000334 | 0.001303     | 0.001506 |
| `refund-history`    | 0.068741 | 0.007232    | 0.002094 | 0.913424     | 0.008510 |

## Native confidence fields

These are the fields returned by the model, not a common confidence scale. **Not reported** is distinct from zero.

| Case                | Returned confidence | Returned answer confidence |
| ------------------- | ------------------- | -------------------------- |
| `refund-headphones` | Not reported        | Not reported               |
| `replacement-only`  | Not reported        | Not reported               |
| `before-purchase`   | Not reported        | Not reported               |
| `money-back`        | Not reported        | Not reported               |
| `refund-charge`     | Not reported        | Not reported               |
| `keep-product`      | Not reported        | Not reported               |
| `refund-polite`     | Not reported        | Not reported               |
| `repair-only`       | Not reported        | Not reported               |
| `shipping`          | Not reported        | Not reported               |
| `refund-indirect`   | Not reported        | Not reported               |
| `cancel-refund`     | Not reported        | Not reported               |
| `refund-history`    | Not reported        | Not reported               |

## Model and runtime

| Field                  | Recorded value                                                      |
| ---------------------- | ------------------------------------------------------------------- |
| Model key              | `circuit`                                                           |
| Model identifier       | `jbarney/circuit-1.7b`                                              |
| Execution              | local                                                               |
| Reported device        | `mps`                                                               |
| Timing scope           | Local inference call on the reported device; model loading excluded |
| Checkpoint revision    | bf3b1fdf2602bd68b1d4ce64a3764fd9e90471b0                            |
| Source repository      | `https://github.com/Barneyjm/circuit`                               |
| Source revision        | ef47613f6699a4b0deb63ddab1cddcdb4ed7f68a                            |
| Base model             | `Qwen/Qwen3-1.7B-Base`                                              |
| Base revision          | ea980cb0a6c2ae4b936e82123acc929f1cec04c1                            |
| Configured environment | `.venv-modern`                                                      |
| Runtime: python        | `3.13.15`                                                           |
| Runtime: torch         | `2.14.0`                                                            |

Local timing excludes loading and includes the first inference call. No separate warm-up was recorded.

This is one small initial screen. Read the [scoring and limitations](README.md#scoring-and-limits) before using it to choose a model for a larger evaluation.
