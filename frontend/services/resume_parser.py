from __future__ import annotations

from io import BytesIO

import docx
import fitz
from loguru import logger
from PyPDF2 import PdfReader


def extract_text(file_name: str, file_bytes: bytes) -> str:
    if file_name.endswith(".pdf"):
        return extract_pdf_text(file_bytes)
    if file_name.endswith(".docx"):
        return extract_docx_text(file_bytes)
    if file_name.endswith(".txt") or file_name.endswith(".md"):
        return file_bytes.decode("utf-8", errors="ignore")
    return ""


def extract_pdf_text(file_bytes: bytes) -> str:
    try:
        reader = PdfReader(BytesIO(file_bytes))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    except Exception:
        try:
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            return "\n".join(page.get_text() for page in doc)
        except Exception as exc:
            logger.error(f"Failed to parse PDF: {exc}")
            return ""


def extract_docx_text(file_bytes: bytes) -> str:
    document = docx.Document(BytesIO(file_bytes))
    return "\n".join(paragraph.text for paragraph in document.paragraphs)


def detect_experience_level(text: str) -> str:
    lowered = text.lower()
    if any(keyword in lowered for keyword in ["intern", "entry", "junior"]):
        return "Junior"
    if any(keyword in lowered for keyword in ["senior", "lead", "manager", "principal"]):
        return "Senior"
    return "Mid"
