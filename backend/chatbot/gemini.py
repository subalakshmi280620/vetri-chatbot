import json
import logging
import time
import urllib.error
import urllib.parse
import urllib.request

from django.conf import settings

logger = logging.getLogger(__name__)

_RETRYABLE_CODES = {429, 503, 500, 502, 504}


def _gemini_model_chain() -> list[str]:
    models = [settings.GEMINI_MODEL, *settings.GEMINI_FALLBACK_MODELS]
    seen: set[str] = set()
    chain: list[str] = []
    for model in models:
        if model and model not in seen:
            seen.add(model)
            chain.append(model)
    return chain


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
        raise RuntimeError("GEMINI_API_KEY is not set")

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
            "temperature": 0.65,
            "maxOutputTokens": 400,
        },
    }
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"Gemini HTTP {exc.code}: {detail[:300]}") from exc

    candidates = data.get("candidates") or []
    if not candidates:
        raise RuntimeError("Gemini returned no candidates")

    parts = candidates[0].get("content", {}).get("parts") or []
    text = "".join(part.get("text", "") for part in parts).strip()
    if not text:
        raise RuntimeError("Gemini returned an empty reply")
    return text


def ask_gemini(
    user_message: str,
    system_prompt: str,
    history=None,
    images=None,
) -> str:
    last_error: Exception | None = None

    for model in _gemini_model_chain():
        for attempt in range(2):
            try:
                return _call_gemini_model(
                    model,
                    user_message,
                    system_prompt,
                    history,
                    images=images,
                )
            except RuntimeError as exc:
                last_error = exc
                code = None
                if "Gemini HTTP " in str(exc):
                    try:
                        code = int(str(exc).split("Gemini HTTP ", 1)[1][:3])
                    except ValueError:
                        code = None
                if code in _RETRYABLE_CODES and attempt == 0:
                    time.sleep(0.75)
                    continue
                logger.warning("Gemini model %s unavailable: %s", model, exc)
                break

    if last_error:
        raise last_error
    raise RuntimeError("Gemini is not configured")
