import json
import logging
import time
import urllib.error
import urllib.parse
import urllib.request

from django.conf import settings

logger = logging.getLogger(__name__)

BACKOFF_BASE_SECONDS = 0.5

# Retry temporary overload / server errors on the same model.
RETRYABLE_CODES = {500, 502, 503, 504}
# Quota and client errors — do not retry the same model.
QUOTA_EXHAUSTED_CODES = {429}
NON_RETRYABLE_CODES = {400, 401, 403, 404}


class GeminiAPIError(RuntimeError):
    """Gemini API failure with safe metadata for logging (no API keys)."""

    def __init__(self, message: str, *, code: int | None = None, model: str = ""):
        super().__init__(message)
        self.code = code
        self.model = model


def _max_retries() -> int:
    return settings.GEMINI_MAX_RETRIES


def _gemini_model_chain() -> list[str]:
    models = [settings.GEMINI_MODEL, *settings.GEMINI_FALLBACK_MODELS]
    seen: set[str] = set()
    chain: list[str] = []
    for model in models:
        if model and model not in seen:
            seen.add(model)
            chain.append(model)
    return chain


def _safe_api_error_message(code: int, detail: str) -> str:
    """Build a log-safe error string without API keys or long payloads."""
    try:
        payload = json.loads(detail)
        message = payload.get("error", {}).get("message", "")
    except json.JSONDecodeError:
        message = detail[:200]
    message = (message or "Unknown Gemini API error").replace("\n", " ").strip()
    return f"Gemini HTTP {code}: {message[:240]}"


def _build_user_parts(user_message: str, images=None) -> list[dict]:
    parts: list[dict] = []
    for image in images or []:
        parts.append({
            "inline_data": {
                "mime_type": image["mime_type"],
                "data": image["data"],
            },
        })
    parts.append({"text": user_message})
    return parts


def _call_gemini_model(
    model: str,
    user_message: str,
    system_prompt: str,
    history=None,
    images=None,
) -> str:
    api_key = settings.GEMINI_API_KEY
    if not api_key:
        raise GeminiAPIError("GEMINI_API_KEY is not set")

    encoded_model = urllib.parse.quote(model, safe="")
    url = (
        f"{settings.GEMINI_BASE_URL}/models/{encoded_model}:generateContent"
        f"?key={urllib.parse.quote(api_key)}"
    )
    contents = []
    for item in history or []:
        role = "model" if item["role"] == "bot" else "user"
        contents.append({"role": role, "parts": [{"text": item["text"]}]})
    contents.append({
        "role": "user",
        "parts": _build_user_parts(user_message, images),
    })

    payload = {
        "systemInstruction": {"parts": [{"text": system_prompt}]},
        "contents": contents,
        "generationConfig": {
            "temperature": 0.85,
            "maxOutputTokens": 512,
            "topP": 0.95,
        },
    }
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(
            request, timeout=settings.GEMINI_REQUEST_TIMEOUT
        ) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="ignore")
        raise GeminiAPIError(
            _safe_api_error_message(exc.code, detail),
            code=exc.code,
            model=model,
        ) from exc

    candidates = data.get("candidates") or []
    if not candidates:
        raise GeminiAPIError("Gemini returned no candidates", model=model)

    parts = candidates[0].get("content", {}).get("parts") or []
    text = "".join(part.get("text", "") for part in parts).strip()
    if not text:
        raise GeminiAPIError("Gemini returned an empty reply", model=model)
    return text


def ask_gemini(
    user_message: str,
    system_prompt: str,
    history=None,
    images=None,
) -> str:
    last_error: GeminiAPIError | None = None
    quota_exhausted_models: set[str] = set()
    api_quota_exhausted = False

    for model in _gemini_model_chain():
        if api_quota_exhausted:
            logger.info(
                "Skipping remaining Gemini models — API key quota exhausted (HTTP 429)",
            )
            break
        if model in quota_exhausted_models:
            logger.info(
                "Skipping Gemini model %s — quota already exhausted this request",
                model,
            )
            continue

        max_retries = _max_retries()
        for attempt in range(1, max_retries + 1):
            try:
                reply = _call_gemini_model(
                    model,
                    user_message,
                    system_prompt,
                    history,
                    images=images,
                )
                if attempt > 1:
                    logger.info(
                        "Gemini model %s succeeded on attempt %d/%d",
                        model,
                        attempt,
                        max_retries,
                    )
                return reply
            except (TimeoutError, OSError) as exc:
                last_error = GeminiAPIError(
                    f"Gemini request timed out: {type(exc).__name__}",
                    model=model,
                )
                if attempt < max_retries:
                    delay = BACKOFF_BASE_SECONDS * (2 ** (attempt - 1))
                    logger.warning(
                        "Gemini model %s timeout on attempt %d/%d; retrying in %.1fs",
                        model,
                        attempt,
                        max_retries,
                        delay,
                    )
                    time.sleep(delay)
                    continue
                logger.warning(
                    "Gemini model %s failed after %d attempt(s) (timeout)",
                    model,
                    attempt,
                )
                break
            except GeminiAPIError as exc:
                last_error = exc
                code = exc.code

                if code in QUOTA_EXHAUSTED_CODES:
                    quota_exhausted_models.add(model)
                    api_quota_exhausted = True
                    logger.warning(
                        "Gemini API quota exhausted (HTTP %s) on model %s; "
                        "skipping all remaining Gemini models for this request",
                        code,
                        model,
                    )
                    break

                if code in NON_RETRYABLE_CODES:
                    logger.warning(
                        "Gemini model %s non-retryable error (HTTP %s) on attempt %d",
                        model,
                        code,
                        attempt,
                    )
                    break

                if code in RETRYABLE_CODES and attempt < max_retries:
                    delay = BACKOFF_BASE_SECONDS * (2 ** (attempt - 1))
                    logger.warning(
                        "Gemini model %s HTTP %s on attempt %d/%d; "
                        "retrying in %.1fs",
                        model,
                        code,
                        attempt,
                        max_retries,
                        delay,
                    )
                    time.sleep(delay)
                    continue

                logger.warning(
                    "Gemini model %s failed after %d attempt(s) (HTTP %s)",
                    model,
                    attempt,
                    code or "unknown",
                )
                break

    if last_error:
        raise last_error
    raise GeminiAPIError("Gemini is not configured")
