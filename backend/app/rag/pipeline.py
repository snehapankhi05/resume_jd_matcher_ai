from backend.app.rag.loader import load_pdf
from backend.app.rag.splitter import split_documents
from backend.app.rag.vectordb import create_vector_store
from backend.app.utils.document_validator import validate_pdf


def process_document(
    file_path: str,
    collection_name: str,
    session_id: str
):
    """
    Complete document processing pipeline.
    """

    # Validate PDF
    validate_pdf(file_path)

    # Load PDF
    documents = load_pdf(file_path)

    # Split into chunks
    chunks = split_documents(documents)

    # Store session_id in metadata
    for chunk in chunks:
        chunk.metadata["session_id"] = session_id

    # Store embeddings
    create_vector_store(
        documents=chunks,
        collection_name=collection_name,
        session_id=session_id
    )

    return {
        "pages": len(documents),
        "chunks": len(chunks),
        "collection_name": collection_name
    }