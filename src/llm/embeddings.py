"""
Embedding model wrapper.

@help.category LLM Integration
@help.title Embedding Model
@help.description Wrapper for text embedding models used in semantic search.
Uses Sentence Transformers for local embeddings, with GPU acceleration when available.
Falls back gracefully if dependencies are missing.
"""
from ..config.settings import get_settings

# Try to import sentence-transformers
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

# Try to detect GPU availability
try:
    import torch
    CUDA_AVAILABLE = torch.cuda.is_available()
    DEVICE = "cuda" if CUDA_AVAILABLE else "cpu"
except ImportError:
    CUDA_AVAILABLE = False
    DEVICE = "cpu"


_embedding_model = None


def get_embedding_model():
    """
    Get embedding model instance (singleton).
    
    @help.title Get Embedding Model Function
    @help.description Returns singleton embedding model instance. Loads Sentence Transformers
    model and moves to GPU if available. Falls back to None if dependencies missing (ChromaDB
    will use its default embeddings).
    @help.example
        embeddings = get_embedding_model()
        if embeddings:
            vector = embeddings.encode("Hello world")
    @help.performance GPU acceleration available if CUDA is detected.
    """
    global _embedding_model
    
    if _embedding_model is None:
        settings = get_settings()
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            # Load model and move to GPU if available
            _embedding_model = SentenceTransformer(settings.embedding_model)
            if CUDA_AVAILABLE:
                _embedding_model = _embedding_model.to(DEVICE)
                print(f"[OK] Embeddings loaded on GPU: {torch.cuda.get_device_name(0)}")
            else:
                print("[WARNING] Embeddings using CPU (GPU not available)")
        else:
            # Return None - ChromaDB will use its default embeddings
            # This allows the app to work without sentence-transformers
            _embedding_model = None
    
    return _embedding_model
