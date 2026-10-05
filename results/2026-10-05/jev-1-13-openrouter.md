# Jev 1.13 (OpenRouter)

[All results and exact inputs](README.md) · [Project overview](../../README.md) · [Original JSON](comparison.json)

Captured run: `2026-10-05T11:10:07.883712+00:00`. Question: `request_type`.

All 12 answers matched the expected labels in this run.

## Summary

| Metric                        | Value          |
| ----------------------------- | -------------- |
| Answer pairs                  | 12             |
| Answered                      | 12             |
| Labeled                       | 12             |
| Correct                       | 12             |
| Incorrect                     | 0              |
| Execution errors              | 0              |
| Accuracy                      | 12/12 (100.0%) |
| Coverage                      | 12/12 (100%)   |
| Choice Brier                  | 0.000000       |
| Log loss (nats)               | 0.000000       |
| Zero-probability truths       | 0              |
| Mean API round trip (ms)      | 299.735        |
| Load time (s)                 | Not reported   |
| Total reported API cost (USD) | 0.000222138    |

## Answers

Expected labels come from the saved run. All rows have execution status `ok`; an incorrect classification is not an execution error.

| Case                | Expected     | Selected     | Correct | Selected probability | Choice Brier | Log loss (nats) | API round trip (ms) |
| ------------------- | ------------ | ------------ | ------- | -------------------- | ------------ | --------------- | ------------------- |
| `refund-headphones` | refund       | refund       | Yes     | 1.000000             | 0.000000     | 0.000000        | 406.401             |
| `replacement-only`  | replacement  | replacement  | Yes     | 1.000000             | 0.000000     | 0.000000        | 193.138             |
| `before-purchase`   | other        | other        | Yes     | 1.000000             | 0.000000     | 0.000000        | 188.550             |
| `money-back`        | refund       | refund       | Yes     | 1.000000             | 0.000000     | 0.000000        | 181.102             |
| `refund-charge`     | refund       | refund       | Yes     | 1.000000             | 0.000000     | 0.000000        | 256.579             |
| `keep-product`      | other        | other        | Yes     | 1.000000             | 0.000000     | 0.000000        | 920.098             |
| `refund-polite`     | refund       | refund       | Yes     | 1.000000             | 0.000000     | 0.000000        | 189.692             |
| `repair-only`       | repair       | repair       | Yes     | 1.000000             | 0.000000     | 0.000000        | 321.572             |
| `shipping`          | order_status | order_status | Yes     | 1.000000             | 0.000000     | 0.000000        | 306.888             |
| `refund-indirect`   | refund       | refund       | Yes     | 1.000000             | 0.000000     | 0.000000        | 200.225             |
| `cancel-refund`     | refund       | refund       | Yes     | 1.000000             | 0.000000     | 0.000000        | 208.469             |
| `refund-history`    | order_status | order_status | Yes     | 1.000000             | 0.000000     | 0.000000        | 224.108             |

## Probabilities

| Case                | refund   | replacement | repair   | order_status | other    |
| ------------------- | -------- | ----------- | -------- | ------------ | -------- |
| `refund-headphones` | 1.000000 | 0.000000    | 0.000000 | 0.000000     | 0.000000 |
| `replacement-only`  | 0.000000 | 1.000000    | 0.000000 | 0.000000     | 0.000000 |
| `before-purchase`   | 0.000000 | 0.000000    | 0.000000 | 0.000000     | 1.000000 |
| `money-back`        | 1.000000 | 0.000000    | 0.000000 | 0.000000     | 0.000000 |
| `refund-charge`     | 1.000000 | 0.000000    | 0.000000 | 0.000000     | 0.000000 |
| `keep-product`      | 0.000000 | 0.000000    | 0.000000 | 0.000000     | 1.000000 |
| `refund-polite`     | 1.000000 | 0.000000    | 0.000000 | 0.000000     | 0.000000 |
| `repair-only`       | 0.000000 | 0.000000    | 1.000000 | 0.000000     | 0.000000 |
| `shipping`          | 0.000000 | 0.000000    | 0.000000 | 1.000000     | 0.000000 |
| `refund-indirect`   | 1.000000 | 0.000000    | 0.000000 | 0.000000     | 0.000000 |
| `cancel-refund`     | 1.000000 | 0.000000    | 0.000000 | 0.000000     | 0.000000 |
| `refund-history`    | 0.000000 | 0.000000    | 0.000000 | 1.000000     | 0.000000 |

## Native confidence fields

These are the fields returned by the model, not a common confidence scale. **Not reported** is distinct from zero.

| Case                | Returned confidence | Returned answer confidence |
| ------------------- | ------------------- | -------------------------- |
| `refund-headphones` | 1.000000            | Not reported               |
| `replacement-only`  | 1.000000            | Not reported               |
| `before-purchase`   | 1.000000            | Not reported               |
| `money-back`        | 1.000000            | Not reported               |
| `refund-charge`     | 1.000000            | Not reported               |
| `keep-product`      | 1.000000            | Not reported               |
| `refund-polite`     | 1.000000            | Not reported               |
| `repair-only`       | 1.000000            | Not reported               |
| `shipping`          | 1.000000            | Not reported               |
| `refund-indirect`   | 1.000000            | Not reported               |
| `cancel-refund`     | 1.000000            | Not reported               |
| `refund-history`    | 1.000000            | Not reported               |

## Model and runtime

| Field                 | Recorded value                                      |
| --------------------- | --------------------------------------------------- |
| Model key             | `jev`                                               |
| Model identifier      | `typesafe/jev-1.13`                                 |
| Execution             | hosted                                              |
| Reported device       | `OpenRouter API`                                    |
| Timing scope          | API round trip including network and provider queue |
| Checkpoint revision   | Not reported                                        |
| Backend               | openrouter                                          |
| Runtime: backend      | `OpenRouter Decisions API`                          |
| Runtime: endpoint     | `https://openrouter.ai/api/alpha/decisions`         |
| Returned served model | `typesafe/jev-1.13-20260917`                        |

API timing includes network and provider queueing. The export does not report a hosted checkpoint revision or load time.

This is one small initial screen. Read the [scoring and limitations](README.md#scoring-and-limits) before using it to choose a model for a larger evaluation.
