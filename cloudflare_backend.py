"""Cloudflare Workers AI CLEF typed decisions; no chat or text parsing.

Text binary/choice suites use the existing workbench contract. Score questions
and embedded images are supported by Cloudflare but are outside this UI's scope.
"""

import json
import math
import os
import re
from time import perf_counter

import requests

from model_config import provider_eligibility

API_ROOT = "https://api.cloudflare.com/client/v4"
MODEL_SELECTORS = {
    "@cf/cloudflare/clef": "clef",
    "@cf/cloudflare/clef-flash": "clef-flash",
}
QUESTION_ID_PATTERN = re.compile(r"[A-Za-z0-9_.-]{1,100}")


def configuration_error():
    """Check explicit app configuration locally; never probe account access."""
    return provider_eligibility("cloudflare").error


def validate_request(questions, model):
    if model not in MODEL_SELECTORS:
        raise ValueError("Unknown CLEF model ID; choose @cf/cloudflare/clef or @cf/cloudflare/clef-flash.")
    if not isinstance(questions, dict) or not 1 <= len(questions) <= 64:
        raise ValueError("CLEF requires 1–64 questions per context.")
    for qid, question in questions.items():
        if not isinstance(qid, str) or not QUESTION_ID_PATTERN.fullmatch(qid):
            raise ValueError("CLEF question IDs must be 1–100 letters, digits, underscores, periods, or hyphens.")
        if not isinstance(question, dict) or question.get("type") not in ("noul", "choice"):
            raise ValueError("This workbench's CLEF adapter supports text noul and choice questions.")
        if not isinstance(question.get("instructions"), str) or not question["instructions"].strip():
            raise ValueError("Every CLEF question needs nonempty text instructions.")
        if question["type"] == "choice":
            criteria = question.get("criteria")
            if not isinstance(criteria, dict) or not 2 <= len(criteria) <= 255:
                raise ValueError("CLEF choice questions require 2–255 named choices.")
            if any(not isinstance(name, str) or not name.strip() for name in criteria):
                raise ValueError("CLEF choices need nonempty names.")


def probability(value, field):
    if type(value) not in (int, float) or not 0 <= value <= 1 or not math.isfinite(value):
        raise ValueError(f"CLEF returned an invalid {field} probability.")


def validate_response(raw, questions, model):
    if not isinstance(raw, dict) or raw.get("model") not in {model, MODEL_SELECTORS[model]}:
        raise ValueError("CLEF returned an unexpected or missing model ID.")
    answers = raw.get("answers")
    if not isinstance(answers, dict) or set(answers) != set(questions):
        raise ValueError("CLEF must return exactly the requested question IDs.")
    usage = raw.get("usage")
    if not isinstance(usage, dict) or any(type(usage.get(k)) is not int or usage[k] < 0
                                         for k in ("input_tokens", "output_tokens")):
        raise ValueError("CLEF returned missing or invalid token usage.")
    for qid, question in questions.items():
        answer = answers[qid]
        if not isinstance(answer, dict) or answer.get("type") != question["type"]:
            raise ValueError("CLEF returned a missing or incorrect answer type.")
        if question["type"] == "noul":
            probability(answer.get("noul"), "yes")
        else:
            probabilities = answer.get("probabilities")
            criteria = question["criteria"]
            if not isinstance(probabilities, dict) or set(probabilities) != set(criteria):
                raise ValueError("CLEF choice probabilities must match exactly the supplied choices.")
            for value in probabilities.values():
                probability(value, "choice")
            total = sum(probabilities.values())
            if abs(total - 1) > max(.001, len(criteria) * .000051):
                raise ValueError("CLEF choice probabilities must sum to one.")
            choice = answer.get("choice")
            if not isinstance(choice, str) or choice not in criteria:
                raise ValueError("CLEF selected a missing or unknown choice.")
            if probabilities[choice] < max(probabilities.values()) - 1e-6:
                raise ValueError("CLEF selected choice does not match the largest probability.")
            probability(answer.get("confidence"), "confidence")


def predict_messages(messages, questions, model):
    packet = {"results": [], "device": "Cloudflare Workers AI", "load_seconds": None,
              "runtime": {"backend": "Cloudflare Workers AI typed decisions", "model_id": model}}
    error = configuration_error()
    try:
        validate_request(questions, model)
    except ValueError as exc:
        error = str(exc)
    if error:
        packet["results"] = [{"status": "error", "error": error} for _ in messages]
        return packet
    account_id = os.environ["CLOUDFLARE_ACCOUNT_ID"].strip()
    token = os.environ["CLOUDFLARE_AUTH_TOKEN"].strip()
    endpoint = f"{API_ROOT}/accounts/{account_id}/ai/run/{model}"
    with requests.Session() as session:
        for message in messages:
            start = perf_counter()
            try:
                response = session.post(
                    endpoint,
                    headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                    json={"model": MODEL_SELECTORS[model], "state": message, "questions": questions},
                    timeout=(10, 60), allow_redirects=False,
                )
                # Scrub even an echoed credential before retaining raw API data.
                envelope = json.loads(response.text.replace(token, "[REDACTED]"))
                if not isinstance(envelope, dict):
                    raise ValueError("CLEF returned an invalid Workers AI response envelope.")
                if response.status_code != 200 or envelope.get("success") is not True or envelope.get("errors"):
                    errors = envelope.get("errors")
                    detail = errors[0].get("message", "Request failed") if isinstance(errors, list) and errors and isinstance(errors[0], dict) else "Request failed"
                    raise ValueError(f"Cloudflare HTTP {response.status_code}: {str(detail)[:500]}")
                raw = envelope.get("result")
                validate_response(raw, questions, model)
                packet["results"].append({
                    "status": "ok", "raw_response": raw, "api_response": envelope,
                    "inference_seconds": perf_counter() - start,
                    "timing_scope": "API round trip including network and provider queue",
                    # Workers AI reports tokens, not billed dollar cost in this schema.
                    "cost_usd": None,
                })
            except requests.Timeout:
                packet["results"].append({"status": "error", "error": "Cloudflare timed out. No automatic retry was made; the provider may have processed the request."})
            except requests.RequestException:
                packet["results"].append({"status": "error", "error": "Cloudflare connection failed. Check network access; no automatic retry was made."})
            except (ValueError, TypeError, AttributeError) as exc:
                packet["results"].append({"status": "error", "error": str(exc).replace(token, "[REDACTED]")[:700]})
    return packet
