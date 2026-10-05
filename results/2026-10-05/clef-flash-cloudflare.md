# CLEF Flash (Cloudflare)

[All results and exact inputs](README.md) · [Project overview](../../README.md) · [Original JSON](comparison.json)

Captured run: `2026-10-05T11:10:07.883712+00:00`. Question: `request_type`.

All 12 answers matched the expected labels in this run.

## Summary

| Metric                   | Value          |
| ------------------------ | -------------- |
| Answer pairs             | 12             |
| Answered                 | 12             |
| Labeled                  | 12             |
| Correct                  | 12             |
| Incorrect                | 0              |
| Execution errors         | 0              |
| Accuracy                 | 12/12 (100.0%) |
| Coverage                 | 12/12 (100%)   |
| Choice Brier             | 0.003206       |
| Log loss (nats)          | 0.038455       |
| Zero-probability truths  | 0              |
| Mean API round trip (ms) | 474.753        |
| Load time (s)            | Not reported   |
| API cost (USD)           | Not reported   |

## Answers

Expected labels come from the saved run. All rows have execution status `ok`; an incorrect classification is not an execution error.

| Case                | Expected     | Selected     | Correct | Selected probability | Choice Brier | Log loss (nats) | API round trip (ms) |
| ------------------- | ------------ | ------------ | ------- | -------------------- | ------------ | --------------- | ------------------- |
| `refund-headphones` | refund       | refund       | Yes     | 0.970600             | 0.001109     | 0.029841        | 684.066             |
| `replacement-only`  | replacement  | replacement  | Yes     | 0.971200             | 0.001121     | 0.029223        | 508.757             |
| `before-purchase`   | other        | other        | Yes     | 0.927900             | 0.006528     | 0.074831        | 566.617             |
| `money-back`        | refund       | refund       | Yes     | 0.982800             | 0.000381     | 0.017350        | 529.090             |
| `refund-charge`     | refund       | refund       | Yes     | 0.969500             | 0.001188     | 0.030975        | 440.934             |
| `keep-product`      | other        | other        | Yes     | 0.863500             | 0.023816     | 0.146761        | 458.166             |
| `refund-polite`     | refund       | refund       | Yes     | 0.965500             | 0.001545     | 0.035109        | 334.251             |
| `repair-only`       | repair       | repair       | Yes     | 0.976200             | 0.000713     | 0.024088        | 540.527             |
| `shipping`          | order_status | order_status | Yes     | 0.990900             | 0.000104     | 0.009142        | 612.971             |
| `refund-indirect`   | refund       | refund       | Yes     | 0.982200             | 0.000400     | 0.017960        | 440.057             |
| `cancel-refund`     | refund       | refund       | Yes     | 0.984400             | 0.000306     | 0.015723        | 378.043             |
| `refund-history`    | order_status | order_status | Yes     | 0.970000             | 0.001263     | 0.030459        | 203.551             |

## Probabilities

| Case                | refund   | replacement | repair   | order_status | other    |
| ------------------- | -------- | ----------- | -------- | ------------ | -------- |
| `refund-headphones` | 0.970600 | 0.009100    | 0.010800 | 0.004300     | 0.005200 |
| `replacement-only`  | 0.005200 | 0.971200    | 0.015100 | 0.004700     | 0.003800 |
| `before-purchase`   | 0.019200 | 0.014500    | 0.016600 | 0.021800     | 0.927900 |
| `money-back`        | 0.982800 | 0.006900    | 0.004600 | 0.002700     | 0.003000 |
| `refund-charge`     | 0.969500 | 0.009600    | 0.008500 | 0.003300     | 0.009100 |
| `keep-product`      | 0.051500 | 0.023600    | 0.024000 | 0.037400     | 0.863500 |
| `refund-polite`     | 0.965500 | 0.009800    | 0.014300 | 0.005100     | 0.005300 |
| `repair-only`       | 0.004900 | 0.005800    | 0.976200 | 0.005400     | 0.007700 |
| `shipping`          | 0.002300 | 0.001800    | 0.002100 | 0.990900     | 0.002900 |
| `refund-indirect`   | 0.982200 | 0.004800    | 0.006000 | 0.003300     | 0.003700 |
| `cancel-refund`     | 0.984400 | 0.004200    | 0.004700 | 0.003600     | 0.003100 |
| `refund-history`    | 0.004800 | 0.005700    | 0.002100 | 0.970000     | 0.017400 |

## Native confidence fields

These are the fields returned by the model, not a common confidence scale. **Not reported** is distinct from zero.

| Case                | Returned confidence | Returned answer confidence |
| ------------------- | ------------------- | -------------------------- |
| `refund-headphones` | 0.927900            | Not reported               |
| `replacement-only`  | 0.929500            | Not reported               |
| `before-purchase`   | 0.827900            | Not reported               |
| `money-back`        | 0.957500            | Not reported               |
| `refund-charge`     | 0.925100            | Not reported               |
| `keep-product`      | 0.688500            | Not reported               |
| `refund-polite`     | 0.915600            | Not reported               |
| `repair-only`       | 0.941400            | Not reported               |
| `shipping`          | 0.977400            | Not reported               |
| `refund-indirect`   | 0.955900            | Not reported               |
| `cancel-refund`     | 0.961400            | Not reported               |
| `refund-history`    | 0.926600            | Not reported               |

## Model and runtime

| Field                          | Recorded value                                      |
| ------------------------------ | --------------------------------------------------- |
| Model key                      | `clef_flash`                                        |
| Model identifier               | `@cf/cloudflare/clef-flash`                         |
| Execution                      | hosted                                              |
| Reported device                | `Cloudflare Workers AI`                             |
| Timing scope                   | API round trip including network and provider queue |
| Checkpoint revision            | Not reported                                        |
| Backend                        | cloudflare                                          |
| Configuration default_selected | false                                               |
| Runtime: backend               | `Cloudflare Workers AI typed decisions`             |
| Runtime: model_id              | `@cf/cloudflare/clef-flash`                         |

API timing includes network and provider queueing. The export does not report a hosted checkpoint revision or load time.

This is one small initial screen. Read the [scoring and limitations](README.md#scoring-and-limits) before using it to choose a model for a larger evaluation.
