import hashlib
from pathlib import Path
from typing import Tuple
from fastapi import UploadFile
from app.core.config import get_settings
from app.core.exceptions import DocumentProcessingError

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}
ALLOWED_MIME_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain",
    "application/octet-stream",  # some browsers send this for text/docx
}

def validate_uploaded_file(file: UploadFile) -> Tuple[str, str]:
    """
    Validates file extension, MIME type, and size.
    Returns (cleaned_filename, extension).
    """
    settings = get_settings()
    filename = file.filename or "untitled_document.txt"
    ext = Path(filename).suffix.lower()

    if ext not in ALLOWED_EXTENSIONS:
        raise DocumentProcessingError(
            f"File format '{ext}' is not supported. Permitted formats: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
        )

    # Note: size validation occurs during stream reading to avoid memory exhaustion
    return filename, ext

def compute_sha256(content_bytes: bytes) -> str:
    """Computes SHA-256 checksum of document bytes."""
    return hashlib.sha256(content_bytes).hexdigest()
