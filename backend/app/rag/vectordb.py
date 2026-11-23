import json
import threading
from functools import lru_cache
from pathlib import Path

import numpy as np
from langchain_core.documents import Document

from backend.app.core.config import settings
from backend.app.rag.embeddings import get_embedding_model


def _cosine(matrix: np.ndarray, query: np.ndarray) -> np.ndarray:
    query_norm = np.linalg.norm(query) or 1.0
    row_norms = np.linalg.norm(matrix, axis=1)
    row_norms[row_norms == 0] = 1.0
    return (matrix @ query) / (row_norms * query_norm)


class _VectorRetriever:
    def __init__(self, store, k: int, session_id: str):
        self.store = store
        self.k = k
        self.session_id = session_id

    def invoke(self, query: str):
        return self.store.similarity_search(query, self.k, self.session_id)


class LocalVectorStore:
    """
    Session-scoped chunk store.

    Chroma pulled in a large native stack that does not fit a 512 MB free
    instance. This store keeps the same calls the rest of the app already
    makes: add, delete by session, fetch, and top-k vector search.
    """

    def __init__(self, collection_name: str):
        self.collection_name = collection_name
        self.path = Path(settings.CHROMA_DB_PATH) / f"{collection_name}.json"
        self._lock = threading.Lock()
        self.rows = self._load()

    def _load(self) -> list[dict]:
        if not self.path.exists():
            return []
        return json.loads(self.path.read_text(encoding="utf-8"))

    def _save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self.rows), encoding="utf-8")

    def as_retriever(self, search_kwargs=None):
        search_kwargs = search_kwargs or {}
        session_id = (search_kwargs.get("filter") or {}).get("session_id")
        return _VectorRetriever(self, search_kwargs.get("k", 4), session_id)

    def delete(self, where: dict):
        session_id = where.get("session_id")
        with self._lock:
            self.rows = [
                row for row in self.rows
                if row["metadata"].get("session_id") != session_id
            ]
            self._save()

    def add_documents(self, documents, ids):
        texts = [doc.page_content for doc in documents]
        vectors = get_embedding_model().embed_documents(texts)
        with self._lock:
            for doc_id, doc, vector in zip(ids, documents, vectors):
                self.rows.append({
                    "id": doc_id,
                    "text": doc.page_content,
                    "metadata": dict(doc.metadata or {}),
                    "embedding": vector,
                })
            self._save()

    def get(self, where=None, limit=None, include=None):
        session_id = (where or {}).get("session_id")
        rows = [
            row for row in self.rows
            if session_id is None or row["metadata"].get("session_id") == session_id
        ]
        if limit:
            rows = rows[:limit]

        include = include or []
        data = {"ids": [row["id"] for row in rows]}
        if "documents" in include:
            data["documents"] = [row["text"] for row in rows]
        if "metadatas" in include:
            data["metadatas"] = [row["metadata"] for row in rows]
        return data

    def similarity_search(self, query: str, k: int, session_id: str):
        rows = [
            row for row in self.rows
            if row["metadata"].get("session_id") == session_id and row.get("embedding")
        ]
        if not rows or k <= 0:
            return []

        query_vector = np.array(get_embedding_model().embed_query(query), dtype=np.float32)
        matrix = np.array([row["embedding"] for row in rows], dtype=np.float32)
        scores = _cosine(matrix, query_vector)
        best = np.argsort(scores)[::-1][:k]
        return [
            Document(page_content=rows[i]["text"], metadata=rows[i]["metadata"])
            for i in best
        ]


@lru_cache(maxsize=None)
def get_vector_store(collection_name: str) -> LocalVectorStore:
    return LocalVectorStore(collection_name)


def create_vector_store(documents, collection_name: str, session_id: str):
    """Replace any earlier chunks for this session, then store the new ones."""
    vector_store = get_vector_store(collection_name)
    vector_store.delete(where={"session_id": session_id})
    ids = [f"{session_id}-{index}" for index in range(len(documents))]
    vector_store.add_documents(documents=documents, ids=ids)
    return vector_store


def session_has_documents(collection_name: str, session_id: str) -> bool:
    data = get_vector_store(collection_name).get(
        where={"session_id": session_id},
        limit=1,
        include=[],
    )
    return bool(data["ids"])


def get_session_documents(collection_name: str, session_id: str):
    data = get_vector_store(collection_name).get(
        where={"session_id": session_id},
        include=["documents", "metadatas"],
    )
    documents = [
        Document(page_content=text, metadata=metadata or {})
        for text, metadata in zip(data.get("documents") or [], data.get("metadatas") or [])
    ]
    documents.sort(
        key=lambda doc: (
            doc.metadata.get("page", 0),
            doc.metadata.get("start_index", 0),
        )
    )
    return documents
