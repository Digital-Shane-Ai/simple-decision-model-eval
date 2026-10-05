# Results from October 5, 2026

[Project overview](../../README.md)

These results were downloaded with **Export JSON** from the existing local Chrome Decision models tab at
`http://127.0.0.1:8501/`. The saved run's completion timestamp is `2026-10-05T11:10:07.883712+00:00`.
The browser was not reloaded, and no new inference was run to create these files.

The [original JSON export](comparison.json) retains all 228 answers, full precision probabilities, raw provider responses,
runtime metadata, and model configuration. Its SHA-256 is
`e2b08136498a417ae763d201af2e4f8e8eac216c8de4e5a50ccbb15055e159d6`.

There were 12 contexts, one question, and 19 models: 16 local and three hosted. Every model answered all 12 labeled pairs,
with 100% coverage and zero execution errors. There were 211 correct answers and 17 incorrect answers across all models.
This pooled count describes this run and is not a score for any individual model.

## Question and choices

Question ID: `request_type`. Answer type: `choice`.

> What is the customer’s current primary request? Classify the action requested now, not a past refund or an option they explicitly reject.

| Choice | Meaning |
| --- | --- |
| refund | A current request for money back, including cancellation with a refund. |
| replacement | Send another item instead of a refund. |
| repair | Repair the existing item instead of a refund. |
| order_status | Shipping, tracking, or delivery status for an existing order. |
| other | Pre-purchase questions, keeping the product, or no current request in the other categories. |

## Contexts and expected answers

Each model received the same question, choice definitions, and messages. Expected labels and case IDs were kept out of
the model inputs. All 12 pairs were labeled. The export's legacy binary `expected` fields are null; the labels for this
run are in `expected_answers.request_type` and each result's `expected` field.

| Case | Message | Expected |
| --- | --- | --- |
| `refund-headphones` | I bought a pair of wireless headphones last week, but the left earbud doesn't work. I'd like to return them and get a full refund, please. | refund |
| `replacement-only` | The headphones arrived broken. Please send a replacement. I do not want a refund. | replacement |
| `before-purchase` | Are these headphones compatible with my laptop? I haven't purchased them yet. | other |
| `money-back` | The shoes arrived in the wrong size. Please return my money to the card I paid with. | refund |
| `refund-charge` | You charged me twice for the same coffee maker. Refund the duplicate payment, please. | refund |
| `keep-product` | I thought about returning the blender, but I changed my mind. I'm keeping it and don't need a refund. | other |
| `refund-polite` | Could you please give me a refund for the jacket? The zipper is broken. | refund |
| `repair-only` | Can you repair my laptop under warranty? I'd prefer a repair and am not asking for my money back. | repair |
| `shipping` | My order hasn't arrived. Can you send me the tracking number? | order_status |
| `refund-indirect` | These speakers don't work. I want my money back. | refund |
| `cancel-refund` | Please cancel my undelivered desk order and refund the payment. | refund |
| `refund-history` | Thanks, I received the refund for my old order. For my new order, when will the shoes ship? | order_status |

There were six refund cases, two order-status cases, two other cases, one replacement case, and one repair case.
Always choosing refund would score 6/12.

## Local results

Times are per-context inference calls on the reported device, excluding model loading. The mean includes the first call;
there was no separate warm-up in this captured run. Load time is reported separately and counted once per model.

| Model                                       | Correct | Choice Brier | Log loss (nats) | Mean inference (ms) | Load (s) | Device    |
| ------------------------------------------- | ------- | ------------ | --------------- | ------------------- | -------- | --------- |
| [Laya](laya.md)                             | 10/12   | 0.394375     | 0.721999        | 38.642              | 2.394    | `mps`     |
| [Kev-4B](kev-4b.md)                         | 11/12   | 0.085338     | 0.195767        | 66.840              | 7.128    | `mlx:gpu` |
| [Kev-9B](kev-9b.md)                         | 11/12   | 0.060004     | 0.141359        | 108.610             | 6.387    | `mlx:gpu` |
| [Kev-27B](kev-27b.md)                       | 12/12   | 0.001037     | 0.020332        | 449.118             | 26.595   | `mlx:gpu` |
| [Lumma-Fev-4B](lumma-fev-4b.md)             | 12/12   | 0.017443     | 0.038638        | 275.884             | 4.614    | `mps`     |
| [Lumma-Fev-9B](lumma-fev-9b.md)             | 12/12   | 0.000041     | 0.001436        | 285.406             | 5.414    | `mps`     |
| [MoJev](mojev.md)                           | 11/12   | 0.104383     | 0.160711        | 117.241             | 2.751    | `mps`     |
| [AgentJev](agentjev.md)                     | 11/12   | 0.222491     | 0.465962        | 73.072              | 3.213    | `mps`     |
| [VerQen](verqen.md)                         | 8/12    | 0.520406     | 1.096018        | 20.904              | 1.330    | `mps`     |
| [Fragment-2](fragment-2.md)                 | 6/12    | 0.954979     | ∞               | 13.472              | 0.559    | `mps:0`   |
| [Circuit-1.7B](circuit-1-7b.md)             | 12/12   | 0.051119     | 0.126921        | 49.668              | 3.454    | `mps`     |
| [Circuit-8B](circuit-8b.md)                 | 12/12   | 0.000473     | 0.008508        | 102.020             | 5.586    | `mps`     |
| [WEV-1.7B](wev-1-7b.md)                     | 11/12   | 0.080869     | 0.139012        | 76.195              | 3.025    | `mps:0`   |
| [WEV-4B](wev-4b.md)                         | 12/12   | 0.032238     | 0.063559        | 139.262             | 4.540    | `mps:0`   |
| [WEV-8B](wev-8b.md)                         | 12/12   | 0.002407     | 0.012691        | 210.977             | 7.650    | `mps:0`   |
| [OpenThai-SystemOne](openthai-systemone.md) | 12/12   | 0.001163     | 0.020060        | 120.922             | 2.163    | `mps`     |

## Hosted results

Times are API round trips, including network time and provider queueing. Hosted load time is not reported; it is not zero.
The hosted results should not be treated as a comparison of local GPU inference speeds.

| Model                                               | Correct | Choice Brier | Log loss (nats) | Mean API round trip (ms) |
| --------------------------------------------------- | ------- | ------------ | --------------- | ------------------------ |
| [Jev 1.13 (OpenRouter)](jev-1-13-openrouter.md)     | 12/12   | 0.000000     | 0.000000        | 299.735                  |
| [CLEF Flash (Cloudflare)](clef-flash-cloudflare.md) | 12/12   | 0.003206     | 0.038455        | 474.753                  |
| [CLEF (Cloudflare)](clef-cloudflare.md)             | 12/12   | 0.000691     | 0.020381        | 510.894                  |

All three hosted models completed successfully in this run. Historical configuration notes about unverified access
describe integration work and do not mean these captured answers failed.

## Scoring and limits

Accuracy is correct answers divided by answered labeled pairs. Coverage is answered pairs divided by all pairs.
Choice Brier is the mean, over labeled answers, of the sum of `(probability - one_hot_label)^2` across the five choices.
Lower is better. Binary Brier is not applicable to this multiple-choice run, so its null values do not mean zero.

Log loss is the mean `-ln P(expected)` over the 12 labeled answers, in nats. Lower is better. Zero probabilities are
not clipped: Fragment-2 assigned `P(other) = 0` on `before-purchase`, giving it infinite loss. The JSON stores this as
`log_loss: null`, `log_loss_status: "infinite"`, and `log_loss_zero_probability_count: 1`; it is not an unavailable score.

Probabilities, Brier scores, and finite log loss in these tables are rounded to six decimal places. Inference and API times are
shown in milliseconds to three decimal places. The JSON retains the original values. Native confidence fields are shown
separately from the probability assigned to the selected choice; different models use different definitions. Missing
values are marked **Not reported**.

This was one simple English screening question on 12 hand-labeled, refund-heavy messages. The export contains one run,
with no repeated measurements, held-out evaluation, or uncertainty intervals. These results can narrow further evaluation for this task;
they do not establish a model's general quality. Hardware specifications are not stored in the export. The recorded
device and runtime are listed for each model, and hosted checkpoint revisions are not reported.
