"""Token counting utilities."""
try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False


def count_tokens(text: str, model: str = "gpt-3.5-turbo") -> int:
    """
    Count tokens in text using tiktoken or fallback approximation.
    
    Args:
        text: Text to count tokens for
        model: Model name for encoding (default works for most cases)
    
    Returns:
        Number of tokens
    """
    if TIKTOKEN_AVAILABLE:
        try:
            encoding = tiktoken.encoding_for_model(model)
            return len(encoding.encode(text))
        except Exception:
            # Fallback: approximate 4 characters per token
            return len(text) // 4
    else:
        # Fallback: approximate 4 characters per token (standard for English)
        return len(text) // 4
