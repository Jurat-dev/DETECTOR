"""intfloat/multilingual-e5-large embedding (1024 o'lcham). Kerak bo'lganda yuklanadi."""
from functools import lru_cache
from .config import settings


@lru_cache(maxsize=1)
def _model():
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(settings.embedding_model)


def embed_passages(texts: list[str]) -> list[list[float]]:
    return _model().encode([f"passage: {t}" for t in texts], normalize_embeddings=True,
                           batch_size=16, show_progress_bar=False).tolist()


def embed_query(q: str) -> list[float]:
    return _model().encode([f"query: {q}"], normalize_embeddings=True)[0].tolist()
