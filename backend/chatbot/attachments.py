"""Parse chat attachments: images for Gemini vision, documents as extracted text."""

import base64
import binascii
from dataclasses import dataclass, field

IMAGE_MIME_TYPES = {
    "image/jpeg",
    "image/jpg",
    "image/png",
    "image/webp",
    "image/gif",
}
DOCUMENT_MIME_TYPES = {
    "text/plain",
    "text/markdown",
    "application/pdf",
}
ALLOWED_MIME_TYPES = IMAGE_MIME_TYPES | DOCUMENT_MIME_TYPES

EXTENSION_MIME = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
    ".gif": "image/gif",
    ".txt": "text/plain",
    ".md": "text/markdown",
    ".pdf": "application/pdf",
}


@dataclass
class ProcessedAttachments:
    images: list[dict] = field(default_factory=list)
    document_text: str = ""
    document_names: list[str] = field(default_factory=list)
    display_labels: list[str] = field(default_factory=list)


def _normalize_mime_type(mime_type: str, filename: str) -> str:
    cleaned = (mime_type or "").split(";")[0].strip().lower()
    if cleaned in ALLOWED_MIME_TYPES:
        return cleaned
    extension = ""
    if filename and "." in filename:
        extension = "." + filename.rsplit(".", 1)[-1].lower()
    return EXTENSION_MIME.get(extension, cleaned)


def _decode_attachment_data(data: str) -> bytes:
    payload = data.strip()
    if "," in payload and payload.startswith("data:"):
        payload = payload.split(",", 1)[1]
    try:
        return base64.b64decode(payload, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise ValueError("Attachment data is not valid base64.") from exc


def _extract_pdf_text(content: bytes) -> str:
    try:
        from pypdf import PdfReader
    except ImportError:
        raise ValueError("PDF support is not available on the server.")

    from io import BytesIO

    reader = PdfReader(BytesIO(content))
    pages = []
    for page in reader.pages[:20]:
        text = page.extract_text() or ""
        if text.strip():
            pages.append(text.strip())
    if not pages:
        return ""
    return "\n\n".join(pages)


def _extract_document_text(content: bytes, mime_type: str, filename: str) -> str:
    if mime_type == "application/pdf":
        return _extract_pdf_text(content)
    try:
        return content.decode("utf-8")
    except UnicodeDecodeError:
        return content.decode("utf-8", errors="ignore")


def parse_attachments(
    raw_attachments,
    *,
    max_count: int,
    max_bytes: int,
    max_document_chars: int,
) -> ProcessedAttachments:
    if not raw_attachments:
        return ProcessedAttachments()

    if not isinstance(raw_attachments, list):
        raise ValueError("attachments must be a list.")

    if len(raw_attachments) > max_count:
        raise ValueError(f"You can attach up to {max_count} files per message.")

    result = ProcessedAttachments()
    document_chunks: list[str] = []

    for index, item in enumerate(raw_attachments):
        if not isinstance(item, dict):
            raise ValueError(f"Attachment {index + 1} is invalid.")

        filename = str(item.get("name") or f"file-{index + 1}").strip()[:120]
        mime_type = _normalize_mime_type(str(item.get("mime_type") or ""), filename)
        data = item.get("data")
        if not data:
            raise ValueError(f"Attachment '{filename}' is missing data.")

        content = _decode_attachment_data(str(data))
        if len(content) > max_bytes:
            raise ValueError(
                f"Attachment '{filename}' is too large. "
                f"Maximum size is {max_bytes // (1024 * 1024)} MB."
            )

        if mime_type in IMAGE_MIME_TYPES:
            result.images.append({
                "mime_type": mime_type,
                "data": base64.b64encode(content).decode("ascii"),
            })
            result.display_labels.append(filename)
            continue

        if mime_type not in DOCUMENT_MIME_TYPES:
            raise ValueError(
                f"Attachment '{filename}' has unsupported type. "
                "Use images (JPG, PNG, WEBP) or documents (TXT, MD, PDF)."
            )

        extracted = _extract_document_text(content, mime_type, filename).strip()
        if not extracted:
            raise ValueError(f"Could not extract text from '{filename}'.")

        document_chunks.append(f"--- {filename} ---\n{extracted}")
        result.document_names.append(filename)
        result.display_labels.append(filename)

    if document_chunks:
        combined = "\n\n".join(document_chunks)
        if len(combined) > max_document_chars:
            combined = combined[:max_document_chars] + "\n\n[Document truncated]"
        result.document_text = combined

    return result


def build_user_message_with_attachments(message: str, processed: ProcessedAttachments) -> str:
    parts = [message.strip()] if message and message.strip() else []
    if processed.document_text:
        parts.append(
            "Attached document content for reference:\n"
            f"{processed.document_text}"
        )
    if processed.images and not parts:
        parts.append("Please review the attached image(s) and answer my question.")
    return "\n\n".join(parts).strip() or "Please review the attached file(s)."
