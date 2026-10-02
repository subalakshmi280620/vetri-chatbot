import json
import logging
import urllib.error
import urllib.request

from django.conf import settings

logger = logging.getLogger(__name__)


class GrokAPIError(RuntimeError):
    """xAI Grok API failure with safe metadata for logging (no API keys)."""

    def __init__(self, message: str, *, code: int | None = None):
        super().__init__(message)
        self.code = code


def _safe_api_error_message(code: int, detail: str) -> str:
    """Build a log-safe error string without API keys or long payloads."""
    try:
        payload = json.loads(detail)
        error_obj = payload.get("error", "")
        if isinstance(error_obj, str):
            message = error_obj
        elif isinstance(error_obj, dict):
            message = error_obj.get("message", "")
        else:
            message = payload.get("message", "")
    except json.JSONDecodeError:
        message = detail[:200]
    message = (message or "Unknown Grok API error").replace("\n", " ").strip()
    return f"Grok HTTP {code}: {message[:240]}"


def ask_grok(user_message: str, system_prompt: str, history=None) -> str:
    api_key = settings.XAI_API_KEY
    if not api_key:
        raise GrokAPIError("XAI_API_KEY is not set")

    messages = [{"role": "system", "content": system_prompt}]
    for item in history or []:
        role = "assistant" if item["role"] == "bot" else "user"
        messages.append({"role": role, "content": item["text"]})
    messages.append({"role": "user", "content": user_message})

    base_url = settings.GROK_BASE_URL.rstrip("/")
    payload = {
        "model": settings.GROK_MODEL,
        "messages": messages,
        "temperature": 0.65,
        "max_tokens": 512,
    }
    request = urllib.request.Request(
        f"{base_url}/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(
            request, timeout=settings.GROK_REQUEST_TIMEOUT
        ) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="ignore")
        raise GrokAPIError(
            _safe_api_error_message(exc.code, detail),
            code=exc.code,
        ) from exc
    except (TimeoutError, OSError) as exc:
        raise GrokAPIError(
            f"Grok request timed out: {type(exc).__name__}",
        ) from exc

    choices = data.get("choices") or []
    if not choices:
        raise GrokAPIError("Grok returned no choices")

    content = choices[0].get("message", {}).get("content", "").strip()
    if not content:
        raise GrokAPIError("Grok returned an empty reply")
    return content
