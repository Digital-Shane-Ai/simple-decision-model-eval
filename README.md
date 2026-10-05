# Simple Decision Model Evaluation

I wanted a simple way to evaluate which recently released decision models were worth spending more extensive time
evaluating. This experiment uses
short customer support messages to check whether a model can identify what someone is asking for. If a model struggles
here, then I consider it useless for more advanced use cases. Correct answers are only part of that decision.
I also want to know whether the probabilities behind those answers make sense, and how long each model takes to answer.

The Python/Streamlit app sends the same contexts and editable binary or multiple choice questions to each selected model.
You can replace the example messages, change the question and choice meanings, and supply your own expected labels.
Expected labels and case IDs are kept out of the model inputs.

## October 4th 2026 Evaluation Run

This run used **12 messages, one multiple-choice question, and 19 models**.
The question was: “What is the customer’s current primary request?” The choices were `refund`, `replacement`, `repair`,
`order_status`, and `other`. The messages included explicit and indirect refund requests, rejected refunds, pre-purchase
questions, and a past refund followed by a question about a new order. There were six refund cases, two order-status
cases, two other cases, one replacement case, and one repair case. **Always choosing refund would score 6/12 (50%).**
The [full run details](results/2026-10-05/README.md) contain the exact question, choice definitions, messages, and labels.

### Accuracy

Accuracy counts how often the selected answer matched the expected label.

![Accuracy for all 19 models](results/2026-10-05/charts/accuracy.svg)

### Brier scores and the probabilities behind the answers

Accuracy treats a correct answer the same whether the model gave it a 46% probability or a 99% probability.
**Choice Brier scores also measure the probabilities assigned to all five choices.** They reward probability placed on
the expected answer and penalize probability placed on the other answers. A confident mistake receives a larger penalty
than a more uncertain mistake. Lower is better.

```text
// N = 12 for every model in this run

Choice Brier = (1 / N) × Σ answers Σ five choices (probability − target)²
```

![Choice Brier scores sorted lowest first](results/2026-10-05/charts/brier.svg)

### Log loss

**Log loss measures the probability assigned to the expected answer.** It uses the natural logarithm, measured in nats,
and gives larger penalties as that probability approaches zero. Lower is better. A zero probability gives infinite loss.

```text
Log loss = (1 / N) × Σ answers −ln(probability of expected answer)
```

![Log loss scores sorted lowest first](results/2026-10-05/charts/log-loss.svg)

### Observed timings

Time to call the models. Time to load the model into the GPU is excluded.

![Observed mean call times for all 19 models](results/2026-10-05/charts/timing.svg)

### Numeric overview and model reports

Each model link opens its full answers, probability distributions, per-answer scores, timings, configuration, and runtime
details. Accuracy, Choice Brier, and log loss each use 12 answered, labeled cases for every model.

| Model                                                                  | Execution | Correct | Accuracy | Choice Brier ↓ | Log loss (nats) ↓ | Mean call (ms) |     Load (s) |
| ---------------------------------------------------------------------- | --------- | ------: | -------: | -------------: | ----------------: | -------------: | -----------: |
| [Laya](results/2026-10-05/laya.md)                                     | Local     |   10/12 |    83.3% |     0.39437534 |        0.72199938 |         38.642 |        2.394 |
| [Kev-4B](results/2026-10-05/kev-4b.md)                                 | Local     |   11/12 |    91.7% |     0.08533800 |        0.19576652 |         66.840 |        7.128 |
| [Kev-9B](results/2026-10-05/kev-9b.md)                                 | Local     |   11/12 |    91.7% |     0.06000359 |        0.14135930 |        108.610 |        6.387 |
| [Kev-27B](results/2026-10-05/kev-27b.md)                               | Local     |   12/12 |   100.0% |     0.00103700 |        0.02033212 |        449.118 |       26.595 |
| [Lumma-Fev-4B](results/2026-10-05/lumma-fev-4b.md)                     | Local     |   12/12 |   100.0% |     0.01744319 |        0.03863754 |        275.884 |        4.614 |
| [Lumma-Fev-9B](results/2026-10-05/lumma-fev-9b.md)                     | Local     |   12/12 |   100.0% |     0.00004113 |        0.00143553 |        285.406 |        5.414 |
| [MoJev](results/2026-10-05/mojev.md)                                   | Local     |   11/12 |    91.7% |     0.10438279 |        0.16071060 |        117.241 |        2.751 |
| [AgentJev](results/2026-10-05/agentjev.md)                             | Local     |   11/12 |    91.7% |     0.22249095 |        0.46596170 |         73.072 |        3.213 |
| [VerQen](results/2026-10-05/verqen.md)                                 | Local     |    8/12 |    66.7% |     0.52040630 |        1.09601792 |         20.904 |        1.330 |
| [Fragment-2](results/2026-10-05/fragment-2.md)                         | Local     |    6/12 |    50.0% |     0.95497872 |                 ∞ |         13.472 |        0.559 |
| [Circuit-1.7B](results/2026-10-05/circuit-1-7b.md)                     | Local     |   12/12 |   100.0% |     0.05111934 |        0.12692146 |         49.668 |        3.454 |
| [Circuit-8B](results/2026-10-05/circuit-8b.md)                         | Local     |   12/12 |   100.0% |     0.00047325 |        0.00850799 |        102.020 |        5.586 |
| [WEV-1.7B](results/2026-10-05/wev-1-7b.md)                             | Local     |   11/12 |    91.7% |     0.08086927 |        0.13901156 |         76.195 |        3.025 |
| [WEV-4B](results/2026-10-05/wev-4b.md)                                 | Local     |   12/12 |   100.0% |     0.03223834 |        0.06355864 |        139.262 |        4.540 |
| [WEV-8B](results/2026-10-05/wev-8b.md)                                 | Local     |   12/12 |   100.0% |     0.00240693 |        0.01269078 |        210.977 |        7.650 |
| [OpenThai-SystemOne](results/2026-10-05/openthai-systemone.md)         | Local     |   12/12 |   100.0% |     0.00116280 |        0.02006038 |        120.922 |        2.163 |
| [Jev 1.13 (OpenRouter)](results/2026-10-05/jev-1-13-openrouter.md)     | Hosted    |   12/12 |   100.0% |     0.00000000 |        0.00000000 |        299.735 | Not reported |
| [CLEF Flash (Cloudflare)](results/2026-10-05/clef-flash-cloudflare.md) | Hosted    |   12/12 |   100.0% |     0.00320619 |        0.03845516 |        474.753 | Not reported |
| [CLEF (Cloudflare)](results/2026-10-05/clef-cloudflare.md)             | Hosted    |   12/12 |   100.0% |     0.00069102 |        0.02038140 |        510.894 | Not reported |

## Run your own screen

For a new checkout, install Git, `just`, and Python 3.13, then run from the project folder:

```sh
just setup
just download-models
just serve
```

Setup creates the isolated environments and installs pinned dependencies and model sources. Downloads are cached;
you can select local model keys, for example `just download-models laya kev lumma9b`. MoJev requires approved Hugging Face
access and `HF_TOKEN` or a local login. Hosted Jev requires `OR_TOKEN`; CLEF requires `CLOUDFLARE_AUTH_TOKEN` and
`CLOUDFLARE_ACCOUNT_ID`. Hosted models stay disabled until their configuration is present, and both CLEF models are
optional and unselected by default. The supported launcher reports missing configuration before starting the app.

In the browser, choose models, edit the context and question tables, provide expected labels, and run the comparison.
Export JSON to preserve the full results. `just` lists the available commands; `just serve --server.port 8502` changes
the port. The CLI also accepts question and context files; see the [examples](examples/) and
`.venv/bin/python compare.py --help`.
