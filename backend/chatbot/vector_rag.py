"""Vector semantic search over indexed knowledge chunks (PostgreSQL + Gemini embeddings)."""

import hashlib
import logging
import re
from pathlib import Path

from django.conf import settings
from django.db import connection, transaction

from .embeddings import EmbeddingAPIError, embed_documents_batched, embed_query
from .knowledge_export import EXPORT_VERSION, export_knowledge_chunks
from .models import KnowledgeChunk, KnowledgeIndexState

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).resolve().parent / "data"
EXCLUDED_INDEX_FILES = {"README.txt", "vetrifresh.md"}
CHUNK_SIZE = 700
CHUNK_OVERLAP = 100


def is_postgresql() -> bool:
    return connection.vendor == "postgresql"


def vector_rag_available() -> bool:
    return bool(settings.VECTOR_RAG_ENABLED and is_postgresql())


def cosine_similarity(a: list[float], b: list[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(y * y for y in b) ** 0.5
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def chunk_markdown(text: str, source: str) -> list[dict]:
    """Split markdown on headings; fall back to fixed-size windows."""
    sections = re.split(r"(?=\n## )", text.strip())
    chunks: list[dict] = []
    index = 0
    for section in sections:
        section = section.strip()
        if not section:
            continue
        heading = ""
        if section.startswith("##"):
            lines = section.split("\n", 1)
            heading = lines[0].lstrip("#").strip()
            body = lines[1].strip() if len(lines) > 1 else ""
        else:
            body = section
        if len(body) <= CHUNK_SIZE:
            if body:
                chunks.append({
                    "source": source,
                    "section": heading or f"section_{index}",
                    "text": body,
                    "index": index,
                })
                index += 1
            continue
        start = 0
        while start < len(body):
            end = min(len(body), start + CHUNK_SIZE)
            piece = body[start:end].strip()
            if piece:
                chunks.append({
                    "source": source,
                    "section": heading or f"section_{index}",
                    "text": piece,
                    "index": index,
                })
                index += 1
            if end == len(body):
                break
            start = max(end - CHUNK_OVERLAP, start + 1)
    return chunks


def load_file_chunks() -> list[dict]:
    chunks: list[dict] = []
    if not DATA_DIR.exists():
        return chunks
    for path in sorted(DATA_DIR.glob("*")):
        if path.suffix.lower() not in {".md", ".txt"}:
            continue
        if path.name in EXCLUDED_INDEX_FILES:
            continue
        chunks.extend(chunk_markdown(path.read_text(encoding="utf-8"), path.name))
    return chunks


def collect_source_chunks() -> list[dict]:
    return export_knowledge_chunks() + load_file_chunks()


def compute_content_hash() -> str:
    parts = [EXPORT_VERSION]
    for chunk in collect_source_chunks():
        parts.append(f"{chunk['source']}|{chunk['section']}|{chunk['index']}|{chunk['text']}")
    digest = hashlib.sha256("\n".join(parts).encode("utf-8")).hexdigest()
    return digest


def content_hash_changed() -> bool:
    current = compute_content_hash()
    state = KnowledgeIndexState.objects.first()
    if not state:
        return True
    return state.content_hash != current


def vector_retrieve(query: str, limit: int = 4) -> list[dict]:
    """Return top semantic matches above the score threshold."""
    if not vector_rag_available():
        return []
    if not KnowledgeChunk.objects.exists():
        logger.info("Vector RAG: index empty — run index_knowledge")
        return []

    try:
        query_embedding = embed_query(query)
    except EmbeddingAPIError as exc:
        logger.warning("Vector RAG query embed failed: %s", exc)
        return []

    scored: list[tuple[float, KnowledgeChunk]] = []
    for chunk in KnowledgeChunk.objects.exclude(embedding__isnull=True).iterator():
        score = cosine_similarity(query_embedding, chunk.embedding)
        if score >= settings.VECTOR_RAG_MIN_SCORE:
            scored.append((score, chunk))

    scored.sort(key=lambda item: item[0], reverse=True)
    results = []
    for score, chunk in scored[:limit]:
        results.append({
            "source": chunk.source,
            "section": chunk.section,
            "text": chunk.text,
            "index": chunk.chunk_index,
            "score": round(score, 4),
        })
    return results


def index_knowledge(force: bool = False) -> dict:
    """
    Index knowledge chunks when content changes (or when --force).
    Requires PostgreSQL + GEMINI_API_KEY.
    """
    if not is_postgresql():
        return {"status": "skipped", "reason": "postgresql_required"}
    if not settings.GEMINI_API_KEY:
        return {"status": "skipped", "reason": "gemini_api_key_missing"}

    content_hash = compute_content_hash()
    state = KnowledgeIndexState.objects.first()
    if state and state.content_hash == content_hash and not force:
        return {
            "status": "unchanged",
            "content_hash": content_hash,
            "chunk_count": state.chunk_count,
        }

    source_chunks = collect_source_chunks()
    texts = [chunk["text"] for chunk in source_chunks]
    try:
        embeddings = embed_documents_batched(texts, batch_size=settings.EMBEDDING_BATCH_SIZE)
    except EmbeddingAPIError as exc:
        return {"status": "error", "reason": str(exc)}

    to_create = []
    for chunk, embedding in zip(source_chunks, embeddings):
        chunk_hash = hashlib.sha256(
            f"{chunk['source']}|{chunk['section']}|{chunk['index']}|{chunk['text']}".encode()
        ).hexdigest()
        to_create.append(KnowledgeChunk(
            source=chunk["source"],
            section=chunk["section"],
            text=chunk["text"],
            chunk_index=chunk["index"],
            content_hash=chunk_hash,
            embedding=embedding,
        ))

    with transaction.atomic():
        KnowledgeChunk.objects.all().delete()
        KnowledgeChunk.objects.bulk_create(to_create, batch_size=100)
        KnowledgeIndexState.objects.all().delete()
        KnowledgeIndexState.objects.create(
            content_hash=content_hash,
            chunk_count=len(to_create),
        )

    return {
        "status": "indexed",
        "content_hash": content_hash,
        "chunk_count": len(to_create),
    }
