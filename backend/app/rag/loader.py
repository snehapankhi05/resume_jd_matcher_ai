from pypdf import PdfReader
from langchain_core.documents import Document


def load_pdf(file_path: str):
    """
    Load PDF and return LangChain Document objects.
    """

    reader = PdfReader(file_path)

    documents = []

    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text()

        if text:
            documents.append(
                Document(
                    page_content=text,
                    metadata={
                        "page": page_number,
                        "source": file_path
                    }
                )
            )

    return documents