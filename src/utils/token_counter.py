"""
Token counting utilities.

@help.category Utilities
@help.title Token Counter
@help.description Utility for counting tokens in text. Uses tiktoken for accurate counting,
falls back to character-based approximation if tiktoken is unavailable.
"""
try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False


def count_tokens(text: str, model: str = "gpt-3.5-turbo") -> int:
    """
    Count tokens in text using tiktoken or fallback approximation.
    
    @help.title Count Tokens Function
    @help.description Counts tokens in text using tiktoken library for accuracy.
    Falls back to 4-characters-per-token approximation if tiktoken unavailable.
    @help.example
        count = count_tokens("Hello, world!")
        print(count)  # Output: ~3 tokens
    @help.performance Fast with tiktoken, very fast with approximation fallback.
    
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
