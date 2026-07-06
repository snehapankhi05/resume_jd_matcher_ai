from backend.app.rag.loader import load_pdf
from backend.app.rag.splitter import split_documents
from backend.app.rag.vectordb import create_vector_store


def process_document(file_path: str, collection_name: str):
    """
    Complete RAG pipeline.

    PDF
      ↓
    Load
      ↓
    Chunk
      ↓
    Embeddings
      ↓
    ChromaDB
    """

    documents = load_pdf(file_path)

    chunks = split_documents(documents)

    vector_store = create_vector_store(
        chunks,
        collection_name
    )

    return vector_store