import os
import io
import re
import csv
import logging
from typing import List, Dict, Any, Tuple

logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".csv"}
ALLOWED_MIME_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain",
    "text/csv",
    "application/octet-stream", # frequently reported by browsers for some doc types
}


def validate_file(filename: str, file_size: int, max_mb: int = 10) -> Tuple[bool, str]:
    """Validates file extension and size."""
    ext = os.path.splitext(filename.lower())[1]
    if ext not in ALLOWED_EXTENSIONS:
        return False, f"Unsupported file extension '{ext}'. Allowed: PDF, DOCX, TXT, CSV."
    
    if file_size > max_mb * 1024 * 1024:
        return False, f"File exceeds maximum allowed size of {max_mb}MB."
    
    return True, ""


def extract_text(file_bytes: bytes, filename: str) -> List[Dict[str, Any]]:
    """
    Extracts text from file bytes based on file extension.
    Returns list of dicts: [{"text": str, "page": Optional[int], "section": Optional[str]}]
    """
    ext = os.path.splitext(filename.lower())[1]
    pages_or_sections = []

    if ext == ".pdf":
        try:
            import pypdf
            reader = pypdf.PdfReader(io.BytesIO(file_bytes))
            for i, page in enumerate(reader.pages):
                text = page.extract_text() or ""
                cleaned = clean_text(text)
                if cleaned:
                    pages_or_sections.append({"text": cleaned, "page": i + 1, "section": f"Page {i + 1}"})
        except Exception as e:
            logger.error(f"Error extracting PDF text: {e}")
            raise ValueError(f"Failed to parse PDF document: {e}")

    elif ext == ".docx":
        try:
            import docx
            doc = docx.Document(io.BytesIO(file_bytes))
            full_text = []
            for p in doc.paragraphs:
                if p.text.strip():
                    full_text.append(p.text.strip())
            joined = "\n\n".join(full_text)
            cleaned = clean_text(joined)
            if cleaned:
                pages_or_sections.append({"text": cleaned, "page": 1, "section": "Document Body"})
        except Exception as e:
            logger.error(f"Error extracting DOCX text: {e}")
            raise ValueError(f"Failed to parse DOCX document: {e}")

    elif ext == ".csv":
        try:
            content = file_bytes.decode("utf-8", errors="replace")
            reader = csv.reader(io.StringIO(content))
            rows = [", ".join(row) for row in reader if row]
            cleaned = clean_text("\n".join(rows))
            if cleaned:
                pages_or_sections.append({"text": cleaned, "page": 1, "section": "CSV Content"})
        except Exception as e:
            logger.error(f"Error extracting CSV text: {e}")
            raise ValueError(f"Failed to parse CSV document: {e}")

    elif ext == ".txt":
        try:
            content = file_bytes.decode("utf-8", errors="replace")
            cleaned = clean_text(content)
            if cleaned:
                pages_or_sections.append({"text": cleaned, "page": 1, "section": "Text Document"})
        except Exception as e:
            logger.error(f"Error extracting TXT text: {e}")
            raise ValueError(f"Failed to parse TXT document: {e}")

    else:
        raise ValueError(f"Unsupported file format: {ext}")

    return pages_or_sections


def clean_text(text: str) -> str:
    """Normalizes whitespace and removes unprintable control characters."""
    if not text:
        return ""
    # Remove null bytes and unprintable characters except tabs/newlines
    text = "".join(ch for ch in text if ch.isprintable() or ch in "\n\r\t")
    # Replace multiple spaces with a single space
    text = re.sub(r"[ \t]+", " ", text)
    # Replace more than 2 newlines with 2 newlines
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def chunk_document(
    sections: List[Dict[str, Any]],
    chunk_size: int = 500,
    chunk_overlap: int = 100
) -> List[Dict[str, Any]]:
    """
    Splits document sections into overlapping chunks.
    Preserves page numbers and section context.
    """
    chunks = []
    chunk_index = 0

    for section in sections:
        text = section["text"]
        page = section.get("page", 1)
        sec_name = section.get("section", "General")

        words = text.split(" ")
        if len(words) <= chunk_size:
            chunks.append({
                "chunk_index": chunk_index,
                "text": text,
                "page": page,
                "section": sec_name,
            })
            chunk_index += 1
            continue

        start = 0
        while start < len(words):
            end = min(start + chunk_size, len(words))
            chunk_words = words[start:end]
            chunk_text = " ".join(chunk_words).strip()
            if chunk_text:
                chunks.append({
                    "chunk_index": chunk_index,
                    "text": chunk_text,
                    "page": page,
                    "section": sec_name,
                })
                chunk_index += 1
            if end >= len(words):
                break
            start += (chunk_size - chunk_overlap)

    return chunks
