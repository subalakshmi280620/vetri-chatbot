import json
import urllib.error
import urllib.parse
import urllib.request

from django.conf import settings


def ask_gemini(user_message: str, system_prompt: str, history=None) -> str:
    api_key = settings.GEMINI_API_KEY
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not set")

    model = urllib.parse.quote(settings.GEMINI_MODEL, safe="")
    url = (
        f"{settings.GEMINI_BASE_URL}/models/{model}:generateContent"
        f"?key={urllib.parse.quote(api_key)}"
    )
    contents = []
    for item in history or []:
        role = "model" if item["role"] == "bot" else "user"
        contents.append({"role": role, "parts": [{"text": item["text"]}]})
    contents.append({"role": "user", "parts": [{"text": user_message}]})

    payload = {
        "systemInstruction": {"parts": [{"text": system_prompt}]},
        "contents": contents,
        "generationConfig": {"temperature": 0.4},
    }
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=45) as response:
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
