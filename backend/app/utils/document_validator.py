from pathlib import Path

from pypdf import PdfReader


class DocumentValidationError(Exception):
    """Custom exception for document validation."""
    pass


def validate_pdf(file_path: str, max_pages: int = 20):

    path = Path(file_path)

    if not path.exists():
        raise DocumentValidationError("Uploaded file not found.")

    try:
        reader = PdfReader(file_path)
    except Exception:
        raise DocumentValidationError(
            "Invalid or corrupted PDF."
        )

    if len(reader.pages) == 0:
        raise DocumentValidationError(
            "Uploaded PDF has no pages."
        )

    if len(reader.pages) > max_pages:
        raise DocumentValidationError(
            f"PDF exceeds maximum page limit ({max_pages})."
        )

    extracted_text = ""

    for page in reader.pages:
        text = page.extract_text()

        if text:
            extracted_text += text

    if not extracted_text.strip():
        raise DocumentValidationError(
            "No readable text found. Please upload a text-based PDF."
        )

    if len(extracted_text.split()) < 30:
        raise DocumentValidationError(
            "Document contains too little text for analysis."
        )

    return extracted_text