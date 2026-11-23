from functools import lru_cache

from backend.app.core.config import settings


class MiniLMEmbedder:
    """
    Same MiniLM model as before, loaded with ONNX instead of PyTorch.

    The free Render instance has 512 MB of RAM. The PyTorch build of this
    model does not fit there. fastembed runs the ONNX weights, which are
    the same all-MiniLM-L6-v2 vectors with a much smaller install.
    """

    def __init__(self, model_name: str):
        from fastembed import TextEmbedding

        self.model = TextEmbedding(model_name=model_name)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        return [vector.tolist() for vector in self.model.embed(texts)]

    def embed_query(self, text: str) -> list[float]:
        return self.embed_documents([text])[0]


@lru_cache(maxsize=1)
def get_embedding_model() -> MiniLMEmbedder:
    """Load the embedding model once and reuse it."""
    return MiniLMEmbedder(settings.EMBEDDING_MODEL)
