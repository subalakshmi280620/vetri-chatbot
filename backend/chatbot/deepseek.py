import json
import urllib.error
import urllib.request

from django.conf import settings


def ask_deepseek(user_message: str, system_prompt: str, history=None) -> str:
    api_key = settings.DEEPSEEK_API_KEY
    if not api_key:
        raise RuntimeError("DEEPSEEK_API_KEY is not set")

    messages = [{"role": "system", "content": system_prompt}]
    for item in history or []:
        role = "assistant" if item["role"] == "bot" else "user"
        messages.append({"role": role, "content": item["text"]})
    messages.append({"role": "user", "content": user_message})

    payload = {
        "model": settings.DEEPSEEK_MODEL,
        "messages": messages,
        "temperature": 0.4,
    }
    request = urllib.request.Request(
        f"{settings.DEEPSEEK_BASE_URL}/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"DeepSeek HTTP {exc.code}: {detail[:300]}") from exc

    choices = data.get("choices") or []
    if not choices:
        raise RuntimeError("DeepSeek returned no choices")

    content = choices[0].get("message", {}).get("content", "").strip()
    if not content:
        raise RuntimeError("DeepSeek returned an empty reply")
    return content
