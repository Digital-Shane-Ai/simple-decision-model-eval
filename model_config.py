"""Local configuration eligibility for hosted models; never checks account access."""

from dataclasses import dataclass
import os
import re
import sys
from threading import Lock


@dataclass(frozen=True)
class Provider:
    name: str
    api_keys: tuple[str, ...]
    settings: tuple[str, ...] = ()


PROVIDERS = {
    "openrouter": Provider("OpenRouter", ("OR_TOKEN",)),
    "cloudflare": Provider("Cloudflare Workers AI", ("CLOUDFLARE_AUTH_TOKEN",),
                           ("CLOUDFLARE_ACCOUNT_ID",)),
}
HOSTED_BACKENDS = frozenset(PROVIDERS)


@dataclass(frozen=True)
class Eligibility:
    provider: str
    missing_api_keys: tuple[str, ...] = ()
    missing_settings: tuple[str, ...] = ()
    invalid_api_keys: tuple[str, ...] = ()
    invalid_settings: tuple[str, ...] = ()
    unsupported: bool = False

    @property
    def enabled(self):
        return not (self.missing_api_keys or self.missing_settings or
                    self.invalid_api_keys or self.invalid_settings or self.unsupported)

    def details(self):
        # Only static labels and environment variable NAMES reach diagnostics.
        parts = []
        for label, names in (("missing API keys", self.missing_api_keys),
                             ("missing nonsecret configuration", self.missing_settings),
                             ("invalid API key format", self.invalid_api_keys),
                             ("invalid nonsecret configuration format", self.invalid_settings)):
            if names:
                parts.append(f"{label}: {', '.join(names)}")
        if self.unsupported:
            parts.append("unsupported hosted backend; no configured adapter")
        return "; ".join(parts)

    @property
    def error(self):
        return None if self.enabled else f"{self.provider} is disabled: {self.details()}."


def is_hosted(spec):
    return spec.get("backend") not in (None, "local")


def provider_eligibility(backend, environ=None):
    if backend in (None, "local"):
        return Eligibility("Local inference")
    provider = PROVIDERS.get(backend)
    if provider is None:
        return Eligibility("Hosted model", unsupported=True)
    env = os.environ if environ is None else environ
    # Values are ephemeral and never retained in the returned eligibility object.
    values = {name: env.get(name, "").strip() for name in (*provider.api_keys, *provider.settings)}
    missing_keys = tuple(name for name in provider.api_keys if not values[name])
    missing_settings = tuple(name for name in provider.settings if not values[name])
    invalid_keys = tuple(name for name in provider.api_keys if values[name] and
                         any(c in values[name] for c in ("\r", "\n")))
    invalid_settings = ()
    if backend == "cloudflare" and values["CLOUDFLARE_ACCOUNT_ID"] and not re.fullmatch(
            r"[0-9a-fA-F]{32}", values["CLOUDFLARE_ACCOUNT_ID"]):
        invalid_settings = ("CLOUDFLARE_ACCOUNT_ID",)
    return Eligibility(provider.name, missing_keys, missing_settings, invalid_keys, invalid_settings)


def model_eligibility(spec, environ=None):
    return provider_eligibility(spec.get("backend"), environ)


def available_model_keys(models, environ=None):
    return [key for key, spec in models.items() if model_eligibility(spec, environ).enabled]


def default_model_keys(models, environ=None):
    return [key for key in available_model_keys(models, environ)
            if models[key].get("default_selected", True)]


def startup_diagnostics(models, environ=None):
    lines = ["Hosted model configuration (these API keys are optional for local inference):"]
    groups = {}
    for key, spec in models.items():
        if is_hosted(spec):
            groups.setdefault(spec["backend"], []).append((key, spec))
    for backend, entries in groups.items():
        eligibility = provider_eligibility(backend, environ)
        names = ", ".join(spec["name"] for _, spec in entries)
        mode = "opt-in" if all(not spec.get("default_selected", True) for _, spec in entries) else "available when configured"
        lines.append(f"- {eligibility.provider} / {names} ({mode}): " +
                     ("configuration present; account access and key validity unverified" if eligibility.enabled
                      else f"disabled; {eligibility.details()}"))
    if not groups:
        lines.append("- No hosted models registered.")
    lines.append("Configuration presence does not verify key validity or account access.")
    return "\n".join(lines)


_startup_lock = Lock()
_startup_pid = None


def print_startup_diagnostics(models, environ=None, stream=None):
    """Print at most once per process, including Streamlit reruns/sessions."""
    global _startup_pid
    with _startup_lock:
        pid = os.getpid()
        if _startup_pid == pid:
            return
        print(startup_diagnostics(models, environ), file=sys.stdout if stream is None else stream, flush=True)
        _startup_pid = pid
