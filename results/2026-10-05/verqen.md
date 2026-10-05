# VerQen

[All results and exact inputs](README.md) · [Project overview](../../README.md) · [Original JSON](comparison.json)

Captured run: `2026-10-05T11:10:07.883712+00:00`. Question: `request_type`.

4 answers did not match the expected labels: `refund-charge` was `replacement` instead of `refund`; `keep-product` was `replacement` instead of `other`; `refund-polite` was `replacement` instead of `refund`; `repair-only` was `refund` instead of `repair`.

## Summary

| Metric                  | Value        |
| ----------------------- | ------------ |
| Answer pairs            | 12           |
| Answered                | 12           |
| Labeled                 | 12           |
| Correct                 | 8            |
| Incorrect               | 4            |
| Execution errors        | 0            |
| Accuracy                | 8/12 (66.7%) |
| Coverage                | 12/12 (100%) |
| Choice Brier            | 0.520406     |
| Log loss (nats)         | 1.096018     |
| Zero-probability truths | 0            |
| Mean inference (ms)     | 20.904       |
| Load time (s)           | 1.330        |

## Answers

Expected labels come from the saved run. All rows have execution status `ok`; an incorrect classification is not an execution error.

| Case                | Expected     | Selected     | Correct | Selected probability | Choice Brier | Log loss (nats) | Inference (ms) |
| ------------------- | ------------ | ------------ | ------- | -------------------- | ------------ | --------------- | -------------- |
| `refund-headphones` | refund       | refund       | Yes     | 0.616762             | 0.188406     | 0.483272        | 58.927         |
| `replacement-only`  | replacement  | replacement  | Yes     | 0.818338             | 0.042007     | 0.200480        | 19.408         |
| `before-purchase`   | other        | other        | Yes     | 0.273582             | 0.674023     | 1.296153        | 17.694         |
| `money-back`        | refund       | refund       | Yes     | 0.605021             | 0.210040     | 0.502492        | 17.259         |
| `refund-charge`     | refund       | replacement  | No      | 0.658596             | 1.109630     | 1.691755        | 17.432         |
| `keep-product`      | other        | replacement  | No      | 0.377864             | 1.171140     | 2.885462        | 17.302         |
| `refund-polite`     | refund       | replacement  | No      | 0.710216             | 1.457738     | 3.234294        | 17.102         |
| `repair-only`       | repair       | refund       | No      | 0.595501             | 1.023093     | 1.642767        | 17.166         |
| `shipping`          | order_status | order_status | Yes     | 0.812963             | 0.043864     | 0.207069        | 17.063         |
| `refund-indirect`   | refund       | refund       | Yes     | 0.633798             | 0.176175     | 0.456025        | 17.310         |
| `cancel-refund`     | refund       | refund       | Yes     | 0.772801             | 0.066002     | 0.257734        | 17.179         |
| `refund-history`    | order_status | order_status | Yes     | 0.744746             | 0.082757     | 0.294712        | 17.000         |

## Probabilities

| Case                | refund   | replacement | repair   | order_status | other    |
| ------------------- | -------- | ----------- | -------- | ------------ | -------- |
| `refund-headphones` | 0.616762 | 0.129424    | 0.127835 | 0.078916     | 0.047063 |
| `replacement-only`  | 0.055801 | 0.818338    | 0.060782 | 0.038856     | 0.026223 |
| `before-purchase`   | 0.253110 | 0.145258    | 0.103332 | 0.224717     | 0.273582 |
| `money-back`        | 0.605021 | 0.187216    | 0.123678 | 0.050722     | 0.033363 |
| `refund-charge`     | 0.184196 | 0.658596    | 0.089625 | 0.037584     | 0.029999 |
| `keep-product`      | 0.301313 | 0.377864    | 0.206658 | 0.058336     | 0.055829 |
| `refund-polite`     | 0.039388 | 0.710216    | 0.163600 | 0.046859     | 0.039937 |
| `repair-only`       | 0.595501 | 0.115718    | 0.193444 | 0.049118     | 0.046219 |
| `shipping`          | 0.038043 | 0.052098    | 0.044896 | 0.812963     | 0.052000 |
| `refund-indirect`   | 0.633798 | 0.164310    | 0.093777 | 0.068809     | 0.039306 |
| `cancel-refund`     | 0.772801 | 0.063070    | 0.085526 | 0.039935     | 0.038668 |
| `refund-history`    | 0.052644 | 0.085935    | 0.076215 | 0.744746     | 0.040460 |

## Native confidence fields

These are the fields returned by the model, not a common confidence scale. **Not reported** is distinct from zero.

| Case                | Returned confidence | Returned answer confidence |
| ------------------- | ------------------- | -------------------------- |
| `refund-headphones` | 0.674800            | Not reported               |
| `replacement-only`  | 0.802700            | Not reported               |
| `before-purchase`   | 0.153000            | Not reported               |
| `money-back`        | 0.684600            | Not reported               |
| `refund-charge`     | 0.746600            | Not reported               |
| `keep-product`      | 0.249900            | Not reported               |
| `refund-polite`     | 0.753900            | Not reported               |
| `repair-only`       | 0.689000            | Not reported               |
| `shipping`          | 0.820500            | Not reported               |
| `refund-indirect`   | 0.694400            | Not reported               |
| `cancel-refund`     | 0.806500            | Not reported               |
| `refund-history`    | 0.780700            | Not reported               |

## Model and runtime

| Field                  | Recorded value                                                      |
| ---------------------- | ------------------------------------------------------------------- |
| Model key              | `verqen`                                                            |
| Model identifier       | `zorqelis-ai/VerQen`                                                |
| Execution              | local                                                               |
| Reported device        | `mps`                                                               |
| Timing scope           | Local inference call on the reported device; model loading excluded |
| Checkpoint revision    | 09ea51c7773fb10d8432cec3b6d26961fd7a184b                            |
| Source repository      | `https://github.com/ZorQelis-AI/verqen`                             |
| Source revision        | ce76e187163df2e83ee189d020cca0feedfa5d06                            |
| Configured environment | `.venv-modern`                                                      |
| Runtime: python        | `3.13.15`                                                           |
| Runtime: torch         | `2.14.0`                                                            |

Local timing excludes loading and includes the first inference call. No separate warm-up was recorded.

This is one small initial screen. Read the [scoring and limitations](README.md#scoring-and-limits) before using it to choose a model for a larger evaluation.
