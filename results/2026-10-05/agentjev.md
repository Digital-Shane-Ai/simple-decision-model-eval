# AgentJev

[All results and exact inputs](README.md) · [Project overview](../../README.md) · [Original JSON](comparison.json)

Captured run: `2026-10-05T11:10:07.883712+00:00`. Question: `request_type`.

1 answer did not match the expected labels: `refund-history` was `refund` instead of `order_status`.

## Summary

| Metric                  | Value         |
| ----------------------- | ------------- |
| Answer pairs            | 12            |
| Answered                | 12            |
| Labeled                 | 12            |
| Correct                 | 11            |
| Incorrect               | 1             |
| Execution errors        | 0             |
| Accuracy                | 11/12 (91.7%) |
| Coverage                | 12/12 (100%)  |
| Choice Brier            | 0.222491      |
| Log loss (nats)         | 0.465962      |
| Zero-probability truths | 0             |
| Mean inference (ms)     | 73.072        |
| Load time (s)           | 3.213         |

## Answers

Expected labels come from the saved run. All rows have execution status `ok`; an incorrect classification is not an execution error.

| Case                | Expected     | Selected     | Correct | Selected probability | Choice Brier | Log loss (nats) | Inference (ms) |
| ------------------- | ------------ | ------------ | ------- | -------------------- | ------------ | --------------- | -------------- |
| `refund-headphones` | refund       | refund       | Yes     | 0.771185             | 0.067658     | 0.259827        | 134.687        |
| `replacement-only`  | replacement  | replacement  | Yes     | 0.546182             | 0.299763     | 0.604803        | 71.225         |
| `before-purchase`   | other        | other        | Yes     | 0.548787             | 0.294538     | 0.600045        | 67.378         |
| `money-back`        | refund       | refund       | Yes     | 0.602685             | 0.210273     | 0.506361        | 70.921         |
| `refund-charge`     | refund       | refund       | Yes     | 0.836077             | 0.035840     | 0.179034        | 70.478         |
| `keep-product`      | other        | other        | Yes     | 0.473115             | 0.372215     | 0.748417        | 71.703         |
| `refund-polite`     | refund       | refund       | Yes     | 0.580596             | 0.233729     | 0.543701        | 66.878         |
| `repair-only`       | repair       | repair       | Yes     | 0.774109             | 0.079381     | 0.256042        | 71.171         |
| `shipping`          | order_status | order_status | Yes     | 0.926518             | 0.007460     | 0.076322        | 67.001         |
| `refund-indirect`   | refund       | refund       | Yes     | 0.849034             | 0.029625     | 0.163657        | 65.389         |
| `cancel-refund`     | refund       | refund       | Yes     | 0.736844             | 0.092254     | 0.305380        | 66.694         |
| `refund-history`    | order_status | refund       | No      | 0.628461             | 0.947156     | 1.347953        | 53.339         |

## Probabilities

| Case                | refund   | replacement | repair   | order_status | other    |
| ------------------- | -------- | ----------- | -------- | ------------ | -------- |
| `refund-headphones` | 0.771185 | 0.077318    | 0.083553 | 0.038091     | 0.029852 |
| `replacement-only`  | 0.029340 | 0.546182    | 0.284232 | 0.104244     | 0.036002 |
| `before-purchase`   | 0.028378 | 0.084386    | 0.055769 | 0.282680     | 0.548787 |
| `money-back`        | 0.602685 | 0.098598    | 0.066675 | 0.191272     | 0.040771 |
| `refund-charge`     | 0.836077 | 0.075268    | 0.050714 | 0.016444     | 0.021497 |
| `keep-product`      | 0.051977 | 0.248821    | 0.160143 | 0.065944     | 0.473115 |
| `refund-polite`     | 0.580596 | 0.110669    | 0.197972 | 0.066651     | 0.044112 |
| `repair-only`       | 0.014452 | 0.163261    | 0.774109 | 0.011232     | 0.036946 |
| `shipping`          | 0.010472 | 0.015399    | 0.006781 | 0.926518     | 0.040831 |
| `refund-indirect`   | 0.849034 | 0.032071    | 0.065594 | 0.033089     | 0.020212 |
| `cancel-refund`     | 0.736844 | 0.091962    | 0.037698 | 0.112648     | 0.020848 |
| `refund-history`    | 0.628461 | 0.036227    | 0.031096 | 0.259772     | 0.044445 |

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

| Field               | Recorded value                                                      |
| ------------------- | ------------------------------------------------------------------- |
| Model key           | `agentjev`                                                          |
| Model identifier    | `aimeigaoshou/agent-jev`                                            |
| Execution           | local                                                               |
| Reported device     | `mps`                                                               |
| Timing scope        | Local inference call on the reported device; model loading excluded |
| Checkpoint revision | 0e2593e6e6c0eade0700712ac13c4389aa7654cc                            |
| Source repository   | `https://github.com/malevrigns/agent-jev`                           |
| Source revision     | a965ca8ff06ccabc0c796dca5447b55cc2069cee                            |
| Runtime: python     | `3.13.15`                                                           |
| Runtime: torch      | `2.8.0`                                                             |

Local timing excludes loading and includes the first inference call. No separate warm-up was recorded.

This is one small initial screen. Read the [scoring and limitations](README.md#scoring-and-limits) before using it to choose a model for a larger evaluation.
