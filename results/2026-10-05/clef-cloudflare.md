# CLEF (Cloudflare)

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
| Choice Brier             | 0.000691       |
| Log loss (nats)          | 0.020381       |
| Zero-probability truths  | 0              |
| Mean API round trip (ms) | 510.894        |
| Load time (s)            | Not reported   |
| API cost (USD)           | Not reported   |

## Answers

Expected labels come from the saved run. All rows have execution status `ok`; an incorrect classification is not an execution error.

| Case                | Expected     | Selected     | Correct | Selected probability | Choice Brier | Log loss (nats) | API round trip (ms) |
| ------------------- | ------------ | ------------ | ------- | -------------------- | ------------ | --------------- | ------------------- |
| `refund-headphones` | refund       | refund       | Yes     | 0.968400             | 0.001337     | 0.032110        | 596.784             |
| `replacement-only`  | replacement  | replacement  | Yes     | 0.978300             | 0.000661     | 0.021939        | 822.936             |
| `before-purchase`   | other        | other        | Yes     | 0.984400             | 0.000304     | 0.015723        | 408.711             |
| `money-back`        | refund       | refund       | Yes     | 0.984500             | 0.000316     | 0.015621        | 410.961             |
| `refund-charge`     | refund       | refund       | Yes     | 0.976400             | 0.000708     | 0.023883        | 716.390             |
| `keep-product`      | other        | other        | Yes     | 0.963300             | 0.001769     | 0.037390        | 511.769             |
| `refund-polite`     | refund       | refund       | Yes     | 0.959400             | 0.002249     | 0.041447        | 306.966             |
| `repair-only`       | repair       | repair       | Yes     | 0.983900             | 0.000335     | 0.016231        | 614.248             |
| `shipping`          | order_status | order_status | Yes     | 0.995400             | 0.000027     | 0.004611        | 412.341             |
| `refund-indirect`   | refund       | refund       | Yes     | 0.985000             | 0.000299     | 0.015114        | 509.905             |
| `cancel-refund`     | refund       | refund       | Yes     | 0.991500             | 0.000091     | 0.008536        | 342.510             |
| `refund-history`    | order_status | order_status | Yes     | 0.988100             | 0.000196     | 0.011971        | 477.206             |

## Probabilities

| Case                | refund   | replacement | repair   | order_status | other    |
| ------------------- | -------- | ----------- | -------- | ------------ | -------- |
| `refund-headphones` | 0.968400 | 0.012400    | 0.012800 | 0.002900     | 0.003500 |
| `replacement-only`  | 0.003000 | 0.978300    | 0.012800 | 0.002600     | 0.003300 |
| `before-purchase`   | 0.003700 | 0.003800    | 0.003800 | 0.004300     | 0.984400 |
| `money-back`        | 0.984500 | 0.007000    | 0.004100 | 0.002000     | 0.002400 |
| `refund-charge`     | 0.976400 | 0.006400    | 0.008300 | 0.003600     | 0.005300 |
| `keep-product`      | 0.016700 | 0.005600    | 0.009200 | 0.005200     | 0.963300 |
| `refund-polite`     | 0.959400 | 0.012800    | 0.020200 | 0.003400     | 0.004200 |
| `repair-only`       | 0.002400 | 0.005500    | 0.983900 | 0.002300     | 0.005900 |
| `shipping`          | 0.001100 | 0.001100    | 0.001000 | 0.995400     | 0.001400 |
| `refund-indirect`   | 0.985000 | 0.004300    | 0.007000 | 0.001700     | 0.002000 |
| `cancel-refund`     | 0.991500 | 0.002500    | 0.002500 | 0.001900     | 0.001600 |
| `refund-history`    | 0.001900 | 0.001600    | 0.001700 | 0.988100     | 0.006700 |

## Native confidence fields

These are the fields returned by the model, not a common confidence scale. **Not reported** is distinct from zero.

| Case                | Returned confidence | Returned answer confidence |
| ------------------- | ------------------- | -------------------------- |
| `refund-headphones` | 0.922800            | Not reported               |
| `replacement-only`  | 0.946700            | Not reported               |
| `before-purchase`   | 0.961400            | Not reported               |
| `money-back`        | 0.961700            | Not reported               |
| `refund-charge`     | 0.941900            | Not reported               |
| `keep-product`      | 0.910500            | Not reported               |
| `refund-polite`     | 0.901300            | Not reported               |
| `repair-only`       | 0.960200            | Not reported               |
| `shipping`          | 0.988600            | Not reported               |
| `refund-indirect`   | 0.962800            | Not reported               |
| `cancel-refund`     | 0.979000            | Not reported               |
| `refund-history`    | 0.970600            | Not reported               |

## Model and runtime

| Field                          | Recorded value                                      |
| ------------------------------ | --------------------------------------------------- |
| Model key                      | `clef`                                              |
| Model identifier               | `@cf/cloudflare/clef`                               |
| Execution                      | hosted                                              |
| Reported device                | `Cloudflare Workers AI`                             |
| Timing scope                   | API round trip including network and provider queue |
| Checkpoint revision            | Not reported                                        |
| Backend                        | cloudflare                                          |
| Configuration default_selected | false                                               |
| Runtime: backend               | `Cloudflare Workers AI typed decisions`             |
| Runtime: model_id              | `@cf/cloudflare/clef`                               |

API timing includes network and provider queueing. The export does not report a hosted checkpoint revision or load time.

This is one small initial screen. Read the [scoring and limitations](README.md#scoring-and-limits) before using it to choose a model for a larger evaluation.
