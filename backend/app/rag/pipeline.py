from backend.app.rag.loader import load_pdf
from backend.app.rag.splitter import split_documents
from backend.app.rag.vectordb import create_vector_store
from backend.app.utils.document_validator import validate_pdf

def process_document(
    file_path=file_path,
    collection_name="resume_collection",
    session_id=session_id
):
    validate_pdf(file_path)

    documents = load_pdf(file_path)

    chunks = split_documents(documents)

    vector_store = create_vector_store(
        chunks,
        collection_name
    )

    return {
        "pages": len(documents),
        "chunks": len(chunks),
        "collection_name": collection_name
    }