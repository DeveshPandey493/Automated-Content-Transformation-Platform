import re
import unicodedata
from typing import Dict, Any, List, Tuple
import fitz  # PyMuPDF
import docx
from app.core.exceptions import DocumentProcessingError

def normalize_text(text: str) -> str:
    """Normalizes Unicode, replaces excessive whitespace, and preserves sentence breaks."""
    if not text:
        return ""
    text = unicodedata.normalize("NFKC", text)
    # Replace carriage returns and excessive empty lines
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()

def count_words(text: str) -> int:
    return len(re.findall(r"\b\w+\b", text))

def extract_from_pdf(content_bytes: bytes) -> Tuple[str, int, Dict[str, Any], List[Dict[str, Any]]]:
    """
    Extracts structured text and per-page content from PDF bytes.
    Returns (cleaned_text, total_pages, metadata, page_records).
    """
    try:
        doc = fitz.open(stream=content_bytes, filetype="pdf")
    except Exception as e:
        raise DocumentProcessingError(f"Failed to parse PDF document: {e}")

    total_pages = len(doc)
    page_records = []
    full_text_parts = []

    for page_idx in range(total_pages):
        page = doc.load_page(page_idx)
        page_text = page.get_text("text")
        cleaned_page = normalize_text(page_text)
        if cleaned_page:
            page_records.append({
                "page_number": page_idx + 1,
                "text": cleaned_page,
                "word_count": count_words(cleaned_page),
            })
            full_text_parts.append(cleaned_page)

    full_cleaned_text = "\n\n".join(full_text_parts)
    meta = {
        "format": "pdf",
        "title": doc.metadata.get("title") or "",
        "author": doc.metadata.get("author") or "",
        "creation_date": doc.metadata.get("creationDate") or "",
    }
    doc.close()
    return full_cleaned_text, total_pages, meta, page_records

def extract_from_docx(content_bytes: bytes) -> Tuple[str, int, Dict[str, Any], List[Dict[str, Any]]]:
    """
    Extracts structured text from DOCX bytes, identifying headings and paragraphs.
    Returns (cleaned_text, estimated_pages, metadata, section_records).
    """
    import io
    try:
        doc = docx.Document(io.BytesIO(content_bytes))
    except Exception as e:
        raise DocumentProcessingError(f"Failed to parse DOCX document: {e}")

    sections = []
    current_heading = "General"
    full_text_parts = []

    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue
        
        # Check if style is heading
        if para.style and para.style.name and para.style.name.startswith("Heading"):
            current_heading = text
        else:
            cleaned = normalize_text(text)
            if cleaned:
                sections.append({
                    "section_heading": current_heading,
                    "text": cleaned,
                    "word_count": count_words(cleaned),
                })
                full_text_parts.append(cleaned)

    full_cleaned_text = "\n\n".join(full_text_parts)
    total_words = count_words(full_cleaned_text)
    # Estimate pages (approx 450 words per page)
    estimated_pages = max(1, (total_words + 449) // 450)

    meta = {
        "format": "docx",
        "paragraphs_count": len(doc.paragraphs),
    }
    return full_cleaned_text, estimated_pages, meta, sections

def extract_from_txt(content_bytes: bytes) -> Tuple[str, int, Dict[str, Any], List[Dict[str, Any]]]:
    """
    Extracts clean text from raw TXT bytes.
    """
    try:
        # Try UTF-8 first, fallback to latin-1
        try:
            raw_text = content_bytes.decode("utf-8")
        except UnicodeDecodeError:
            raw_text = content_bytes.decode("latin-1")
    except Exception as e:
        raise DocumentProcessingError(f"Failed to decode text file: {e}")

    cleaned = normalize_text(raw_text)
    total_words = count_words(cleaned)
    estimated_pages = max(1, (total_words + 449) // 450)

    meta = {"format": "txt"}
    return cleaned, estimated_pages, meta, [{"text": cleaned, "word_count": total_words}]
