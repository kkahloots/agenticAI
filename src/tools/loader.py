"""
File loaders for the RAG ingestion pipeline.
Supports: .txt, .md, .pdf, .docx, .eml
Returns list of {id, text, source, doc_type} dicts ready for ingest_documents().
"""
from __future__ import annotations

import hashlib
import os
from pathlib import Path

_EXT_TO_DOC_TYPE = {
    ".eml": "email",
    ".txt": "note",
    ".md":  "policy",
    ".pdf": "policy",
    ".docx": "policy",
}


def load_file(path: str | Path) -> list[dict]:
    p = Path(path)
    ext = p.suffix.lower()
    loader = _LOADERS.get(ext)
    if loader is None:
        return []
    try:
        chunks = loader(p)
    except Exception:
        return []
    doc_type = _infer_doc_type(p)
    return [
        {
            "id": _chunk_id(p, i),
            "text": chunk,
            "source": p.name,
            "doc_type": doc_type,
        }
        for i, chunk in enumerate(chunks)
        if chunk.strip()
    ]


def _infer_doc_type(p: Path) -> str:
    # folder name takes priority: data/docs/emails/ → email
    parent = p.parent.name.rstrip("s")  # emails→email, notes→note, policies→policy
    if parent in ("email", "note", "policy"):
        return parent
    return _EXT_TO_DOC_TYPE.get(p.suffix.lower(), "general")


def _chunk_id(p: Path, index: int) -> str:
    h = hashlib.md5(str(p.resolve()).encode()).hexdigest()[:8]
    return f"{p.stem}-{h}-{index}"


def _load_txt(p: Path) -> list[str]:
    return [p.read_text(encoding="utf-8")]


def _load_pdf(p: Path) -> list[str]:
    from pypdf import PdfReader
    reader = PdfReader(str(p))
    return [page.extract_text() for page in reader.pages if page.extract_text()]


def _load_docx(p: Path) -> list[str]:
    from docx import Document
    doc = Document(str(p))
    text = "\n".join(para.text for para in doc.paragraphs if para.text.strip())
    return [text]


def _load_eml(p: Path) -> list[str]:
    import email as email_lib
    msg = email_lib.message_from_bytes(p.read_bytes())
    parts = []
    subject = msg.get("Subject", "")
    sender  = msg.get("From", "")
    date    = msg.get("Date", "")
    header  = f"From: {sender}\nDate: {date}\nSubject: {subject}\n\n"
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                payload = part.get_payload(decode=True)
                if payload:
                    parts.append(header + payload.decode(errors="replace"))
    else:
        payload = msg.get_payload(decode=True)
        if payload:
            parts.append(header + payload.decode(errors="replace"))
    return parts or [header]


_LOADERS = {
    ".txt":  _load_txt,
    ".md":   _load_txt,
    ".pdf":  _load_pdf,
    ".docx": _load_docx,
    ".eml":  _load_eml,
}
