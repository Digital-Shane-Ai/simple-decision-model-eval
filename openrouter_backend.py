"""Native OpenRouter Decisions API adapter; no text generation or parsing."""

import json
import os
from time import perf_counter

import requests

from model_config import provider_eligibility

ENDPOINT = "https://openrouter.ai/api/alpha/decisions"


def predict_messages(messages, questions, model):
    results = []
    configuration = provider_eligibility("openrouter")
    if not configuration.enabled:
        return {"results": [{"status": "error", "error": configuration.error} for _ in messages],
                "device": "OpenRouter API", "load_seconds": None}
    token = os.environ["OR_TOKEN"].strip()
    with requests.Session() as session:
        for message in messages:
            start = perf_counter()
            try:
                response = session.post(
                    ENDPOINT,
                    headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                    json={"model": model, "state": message, "questions": questions},
                    timeout=(10, 60), allow_redirects=False,
                )
                # Redact credentials even if an upstream error ever echoes one.
                raw = json.loads(response.text.replace(token, "[REDACTED]"))
                if response.status_code != 200 or "error" in raw:
                    detail = raw.get("error", {})
                    detail = detail.get("message", "Request failed") if isinstance(detail, dict) else str(detail)
                    raise ValueError(f"OpenRouter HTTP {response.status_code}: {detail[:500]}")
                returned_model = raw.get("model", "")
                if returned_model != model and not returned_model.startswith(model + "-"):
                    raise ValueError(f"Unexpected response model: {returned_model!r}")
                results.append({"status": "ok", "raw_response": raw,
                                "inference_seconds": perf_counter() - start,
                                "timing_scope": "API round trip including network and provider queue",
                                "cost_usd": raw.get("usage", {}).get("cost")})
            except requests.Timeout:
                results.append({"status": "error", "error": "OpenRouter timed out. No automatic retry was made; the provider may have processed the request."})
            except requests.RequestException:
                results.append({"status": "error", "error": "OpenRouter connection failed. Check network access; no automatic retry was made."})
            except (ValueError, TypeError, AttributeError) as exc:
                results.append({"status": "error", "error": str(exc).replace(token, "[REDACTED]")[:700]})
    return {"results": results, "device": "OpenRouter API", "load_seconds": None,
            "runtime": {"backend": "OpenRouter Decisions API", "endpoint": ENDPOINT}}
