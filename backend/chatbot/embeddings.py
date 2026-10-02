"""Gemini embedding API for vector RAG (semantic search)."""

import json
import logging
import urllib.error
import urllib.parse
import urllib.request

from django.conf import settings

logger = logging.getLogger(__name__)

# gemini-embedding-001: current Gemini API text embedding model (768 dims recommended).
# Legacy text-embedding-004 is Vertex-only; not used here.
# Pricing: ~$0.025 per 1M input tokens (see ai.google.dev/pricing).
# Free tier: shared with Gemini API key; batch embed at index time keeps query cost low.


class EmbeddingAPIError(RuntimeError):
    def __init__(self, message: str, *, code: int | None = None):
        super().__init__(message)
        self.code = code


def _safe_error_message(code: int, detail: str) -> str:
    try:
        payload = json.loads(detail)
        message = payload.get("error", {}).get("message", "")
    except json.JSONDecodeError:
        message = detail[:200]
    message = (message or "Unknown embedding API error").replace("\n", " ").strip()
    return f"Embedding HTTP {code}: {message[:240]}"


def _embed_request(texts: list[str], task_type: str) -> list[list[float]]:
    if not settings.GEMINI_API_KEY:
        raise EmbeddingAPIError("GEMINI_API_KEY is not configured")
    if not texts:
        return []

    model = settings.EMBEDDING_MODEL
    url = (
        f"{settings.GEMINI_BASE_URL.rstrip('/')}/models/"
        f"{urllib.parse.quote(model, safe='')}:batchEmbedContents"
        f"?key={urllib.parse.quote(settings.GEMINI_API_KEY, safe='')}"
    )
    requests = []
    for text in texts:
        requests.append({
            "model": f"models/{model}",
            "content": {"parts": [{"text": text[:8000]}]},
            "taskType": task_type,
            "outputDimensionality": settings.EMBEDDING_DIMENSION,
        })

    body = json.dumps({"requests": requests}).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=settings.GEMINI_REQUEST_TIMEOUT) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise EmbeddingAPIError(_safe_error_message(exc.code, detail), code=exc.code) from exc
    except urllib.error.URLError as exc:
        raise EmbeddingAPIError(f"Embedding request failed: {exc.reason}") from exc

    embeddings = []
    for item in payload.get("embeddings", []):
        values = item.get("values") or item.get("embedding", {}).get("values", [])
        if not values:
            raise EmbeddingAPIError("Embedding response missing values")
        embeddings.append([float(v) for v in values])
    if len(embeddings) != len(texts):
        raise EmbeddingAPIError(
            f"Expected {len(texts)} embeddings, got {len(embeddings)}"
        )
    return embeddings


def embed_documents(texts: list[str]) -> list[list[float]]:
    """Embed knowledge chunks for indexing (RETRIEVAL_DOCUMENT)."""
    return _embed_request(texts, task_type="RETRIEVAL_DOCUMENT")


def embed_query(text: str) -> list[float]:
    """Embed a user query for semantic search (RETRIEVAL_QUERY)."""
    return _embed_request([text], task_type="RETRIEVAL_QUERY")[0]


def embed_documents_batched(texts: list[str], batch_size: int = 20) -> list[list[float]]:
    """Embed documents in batches to respect API limits."""
    if not texts:
        return []
    results: list[list[float]] = []
    for start in range(0, len(texts), batch_size):
        batch = texts[start : start + batch_size]
        results.extend(embed_documents(batch))
    return results
