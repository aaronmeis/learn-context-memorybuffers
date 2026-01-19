"""Embedding model wrapper."""
from ..config.settings import get_settings

# Try to import sentence-transformers
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False


_embedding_model = None


def get_embedding_model():
    """Get embedding model instance (singleton)."""
    global _embedding_model
    
    if _embedding_model is None:
        settings = get_settings()
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            _embedding_model = SentenceTransformer(settings.embedding_model)
        else:
            # Return None - ChromaDB will use its default embeddings
            # This allows the app to work without sentence-transformers
            _embedding_model = None
    
    return _embedding_model
