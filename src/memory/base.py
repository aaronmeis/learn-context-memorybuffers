"""Base memory interface."""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class Message(BaseModel):
    """Represents a single conversation message."""
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    token_count: int = 0
    priority_score: float = 0.0
    metadata: dict = field(default_factory=dict)


class MemoryMetrics(BaseModel):
    """Tracks memory performance metrics."""
    total_messages_processed: int = 0
    messages_in_context: int = 0
    messages_evicted: int = 0
    total_tokens_used: int = 0
    context_token_budget: int = 4000
    token_utilization_pct: float = 0.0
    retrieval_latency_ms: float = 0.0
    summarization_count: int = 0


class BaseMemory(ABC):
    """Abstract base class for memory implementations."""
    
    def __init__(self, token_budget: int = 4000):
        self.token_budget = token_budget
        self.metrics = MemoryMetrics(context_token_budget=token_budget)
    
    @abstractmethod
    def add_message(self, message: Message) -> None:
        """Add a new message to memory."""
        pass
    
    @abstractmethod
    def get_context(self, query: Optional[str] = None) -> list[Message]:
        """Retrieve messages for context window."""
        pass
    
    @abstractmethod
    def get_formatted_history(self, query: Optional[str] = None) -> str:
        """Get formatted conversation history for LLM prompt."""
        pass
    
    @abstractmethod
    def clear(self) -> None:
        """Clear all memory."""
        pass
    
    def get_metrics(self) -> MemoryMetrics:
        """Return current metrics."""
        return self.metrics
