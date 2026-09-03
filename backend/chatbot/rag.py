from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent / "data"
CHUNK_SIZE = 700
CHUNK_OVERLAP = 100
STOPWORDS = {
    "a", "an", "the", "and", "or", "to", "of", "in", "on", "for", "is", "are",
    "what", "how", "would", "i", "me", "my", "that", "this", "with", "about",
}


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


def load_chunks() -> list[dict]:
    chunks = []
    if not DATA_DIR.exists():
        return chunks
    for path in sorted(DATA_DIR.glob("*")):
        if path.suffix.lower() not in {".md", ".txt"} or path.name == "README.txt":
            continue
        chunks.extend(_chunk_text(path.read_text(encoding="utf-8"), path.name))
    return chunks


def retrieve(query: str, limit: int = 4) -> list[dict]:
    query_tokens = _tokenize(query)
    scored = []
    for chunk in load_chunks():
        overlap = query_tokens & _tokenize(chunk["text"])
        if not overlap:
            continue
        scored.append((len(overlap), chunk))
    scored.sort(key=lambda item: item[0], reverse=True)
    return [chunk for _, chunk in scored[:limit]]


def format_context(chunks: list[dict]) -> str:
    if not chunks:
        return ""
    parts = ["Retrieved institute documents:"]
    for chunk in chunks:
        parts.append(f"[{chunk['source']}]\n{chunk['text']}")
    return "\n\n".join(parts)
