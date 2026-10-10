import json
import urllib.error
import urllib.request

from django.conf import settings


class GroqAPIError(RuntimeError):
    """Error raised when the Groq API request fails."""

    def __init__(self, message: str, *, code: int | None = None):
        super().__init__(message)
        self.code = code


def ask_groq(user_message: str, system_prompt: str, history=None) -> str:
    """Send a chat request to Groq and return its response."""

    api_key = settings.GROQ_API_KEY

    if not api_key:
        raise GroqAPIError("GROQ_API_KEY is not configured")

    messages = [
        {"role": "system", "content": system_prompt}
    ]

    for item in history or []:
        role = "assistant" if item.get("role") == "bot" else "user"
        text = item.get("text", "")

        if text:
            messages.append({
                "role": role,
                "content": text,
            })

    messages.append({
        "role": "user",
        "content": user_message,
    })

    payload = {
        "model": settings.GROQ_MODEL,
        "messages": messages,
        "temperature": 0.65,
        "max_tokens": 512,
    }

    request = urllib.request.Request(
        "https://api.groq.com/openai/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
            "User-Agent": "VetriAICoach/1.0",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(
            request,
            timeout=settings.GROQ_REQUEST_TIMEOUT,
        ) as response:
            data = json.loads(
                response.read().decode("utf-8")
            )

    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="ignore")

        try:
            error_data = json.loads(detail)
            error_info = error_data.get("error", {})

            if isinstance(error_info, dict):
                message = error_info.get(
                    "message",
                    "Unknown API error",
                )
            elif isinstance(error_info, str):
                message = error_info
            else:
                message = "Unknown API error"

        except (json.JSONDecodeError, AttributeError):
            message = "API request failed"

        raise GroqAPIError(
            f"Groq HTTP {exc.code}: {message[:200]}",
            code=exc.code,
        ) from exc

    except (TimeoutError, OSError) as exc:
        raise GroqAPIError(
            f"Groq request failed: {type(exc).__name__}"
        ) from exc

    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise GroqAPIError(
            "Groq returned an invalid response"
        ) from exc

    choices = data.get("choices", [])

    if not choices:
        raise GroqAPIError("Groq returned no response choices")

    content = (
        choices[0]
        .get("message", {})
        .get("content", "")
    )

    if not isinstance(content, str) or not content.strip():
        raise GroqAPIError("Groq returned an empty reply")

    return content.strip()