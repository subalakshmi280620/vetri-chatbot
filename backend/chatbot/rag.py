from pathlib import Path

from django.conf import settings

from .vector_rag import EXCLUDED_INDEX_FILES, vector_rag_available

DATA_DIR = Path(__file__).resolve().parent / "data"
CHUNK_SIZE = 700
CHUNK_OVERLAP = 100
STOPWORDS = {
    "a", "an", "the", "and", "or", "to", "of", "in", "on", "for", "is", "are",
    "what", "how", "would", "i", "me", "my", "that", "this", "with", "about",
}

MISSING_INFO_GUARD = (
    "If the excerpts below do not contain enough information to answer the question, "
    "say you do not have that specific detail and direct the user to "
    "support@vetri-it.com or +91 84381 54827. Never invent facts, prices, or features."
)


def _tokenize(text: str) -> set[str]:
    words = "".join(ch.lower() if ch.isalnum() else " " for ch in text).split()
    return {word for word in words if word not in STOPWORDS and len(word) > 1}


def _chunk_text(text: str, source: str) -> list[dict]:
    cleaned = " ".join(text.split())
    chunks = []
    start = 0
    index = 0
    while start < len(cleaned):
        end = min(len(cleaned), start + CHUNK_SIZE)
        piece = cleaned[start:end].strip()
        if piece:
            chunks.append({"source": source, "text": piece, "index": index})
            index += 1
        if end == len(cleaned):
            break
        start = max(end - CHUNK_OVERLAP, start + 1)
    return chunks


_CHUNKS_CACHE: list[dict] | None = None


def load_chunks() -> list[dict]:
    global _CHUNKS_CACHE
    if _CHUNKS_CACHE is not None:
        return _CHUNKS_CACHE

    chunks = []
    if not DATA_DIR.exists():
        _CHUNKS_CACHE = chunks
        return chunks
    for path in sorted(DATA_DIR.glob("*")):
        if path.suffix.lower() not in {".md", ".txt"}:
            continue
        if path.name in EXCLUDED_INDEX_FILES:
            continue
        chunks.extend(_chunk_text(path.read_text(encoding="utf-8"), path.name))
    _CHUNKS_CACHE = chunks
    return chunks


def lexical_retrieve(query: str, limit: int = 4) -> list[dict]:
    query_tokens = _tokenize(query)
    scored = []
    chunks = load_chunks()
    for chunk in chunks:
        overlap = query_tokens & _tokenize(chunk["text"])
        if not overlap:
            continue
        scored.append((len(overlap), chunk))
    scored.sort(key=lambda item: item[0], reverse=True)
    if scored:
        return [chunk for _, chunk in scored[:limit]]

    vis_chunks = [chunk for chunk in chunks if chunk["source"] == "vis_website.md"]
    if vis_chunks:
        return vis_chunks[:limit]
    return chunks[:limit]


def retrieve(query: str, limit: int = 4) -> list[dict]:
    """Vector search on PostgreSQL; lexical keyword fallback elsewhere."""
    if vector_rag_available():
        from .vector_rag import vector_retrieve

        vector_chunks = vector_retrieve(query, limit=limit)
        if vector_chunks:
            return vector_chunks
    return lexical_retrieve(query, limit=limit)


def format_context(chunks: list[dict]) -> str:
    if not chunks:
        return ""
    parts = [MISSING_INFO_GUARD, "Relevant VIS knowledge excerpts:"]
    for chunk in chunks:
        section = chunk.get("section", "")
        label = chunk["source"]
        if section:
            label = f"{label} — {section}"
        parts.append(f"[{label}]\n{chunk['text']}")
    return "\n\n".join(parts)
