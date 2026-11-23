from pathlib import Path

from fastapi import UploadFile

from backend.app.utils.document_validator import (
    DocumentValidationError,
    FileTooLargeError,
)

CHUNK_SIZE = 1024 * 1024  # 1 MB


def safe_display_name(filename: str | None) -> str:
    """Original file name without any directory part (display only)."""
    return Path((filename or "").replace("\\", "/")).name or "document.pdf"


def save_pdf_upload(
    file: UploadFile,
    destination: Path,
    max_size_mb: int
) -> None:
    """
    Stream an uploaded PDF to `destination` while enforcing:
      * the file really is a PDF (magic bytes, not the client's MIME type)
      * the configured maximum size (checked while streaming, so an
        oversized upload is never fully written to disk)
    The partial file is removed if anything fails.
    """

    max_bytes = max_size_mb * 1024 * 1024

    head = file.file.read(1024)

    if b"%PDF-" not in head:
        raise DocumentValidationError("File is not a valid PDF.")

    file.file.seek(0)

    total = 0

    try:
        with destination.open("wb") as buffer:

            while chunk := file.file.read(CHUNK_SIZE):

                total += len(chunk)

                if total > max_bytes:
                    raise FileTooLargeError(
                        f"File exceeds the {max_size_mb} MB size limit."
                    )

                buffer.write(chunk)

    except Exception:
        destination.unlink(missing_ok=True)
        raise
