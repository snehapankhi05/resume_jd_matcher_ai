from rank_bm25 import BM25Okapi


class BM25Retriever:
    """Keyword retriever with the same from_documents / invoke shape as before."""

    def __init__(self, documents, k: int):
        self.documents = list(documents)
        self.k = k
        tokenized = [doc.page_content.lower().split() for doc in self.documents]
        self._bm25 = BM25Okapi(tokenized) if tokenized else None

    @classmethod
    def from_documents(cls, documents, k: int = 4):
        return cls(documents, k)

    def invoke(self, query: str):
        if not self.documents or self._bm25 is None:
            return []

        scores = self._bm25.get_scores(query.lower().split())
        order = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
        return [self.documents[i] for i in order[: self.k]]
