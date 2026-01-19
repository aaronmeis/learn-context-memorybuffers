"""
Base memory interface.

@help.category Memory System
@help.title Base Memory Interface
@help.description Abstract base class and data models for memory buffer implementations.
Defines the interface that all memory strategies (FIFO, Priority, Hybrid) must implement.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class Message(BaseModel):
    """
    Represents a single conversation message.
    
    @help.title Message Model
    @help.description Data model for individual conversation messages with metadata.
    Stores role, content, timestamp, token count, and optional priority scoring.
    @help.example
        msg = Message(
            role="user",
            content="What is the budget?",
            token_count=5
        )
    """
    role: str  # "user" or "assistant"
    # @help.description Message role: either "user" for human input or "assistant" for LLM responses
    content: str
    # @help.description The actual text content of the message
    timestamp: datetime = field(default_factory=datetime.utcnow)
    # @help.description Timestamp when message was created. Used for recency calculations.
    token_count: int = 0
    # @help.description Number of tokens in the message. Calculated using token counter utility.
    priority_score: float = 0.0
    # @help.description Relevance score (0.0-1.0) used by Priority strategy for ranking messages.
    metadata: dict = field(default_factory=dict)
    # @help.description Optional metadata dictionary for storing additional message information.


class MemoryMetrics(BaseModel):
    """
    Tracks memory performance metrics.
    
    @help.title Memory Metrics Model
    @help.description Comprehensive metrics tracking for memory buffer performance.
    Includes message counts, token usage, latency, and eviction statistics.
    """
    total_messages_processed: int = 0
    # @help.description Total number of messages added to memory since initialization
    messages_in_context: int = 0
    # @help.description Current number of messages in active context window
    messages_evicted: int = 0
    # @help.description Total messages removed from memory (FIFO eviction or summarization)
    total_tokens_used: int = 0
    # @help.description Sum of tokens from all messages currently in context
    context_token_budget: int = 4000
    # @help.description Maximum token budget allocated for context window
    token_utilization_pct: float = 0.0
    # @help.description Percentage of token budget currently used (0-100)
    retrieval_latency_ms: float = 0.0
    # @help.description Time in milliseconds to retrieve context (for performance monitoring)
    summarization_count: int = 0
    # @help.description Number of summarization operations performed (Hybrid strategy only)


class BaseMemory(ABC):
    """
    Abstract base class for memory implementations.
    
    @help.title Base Memory Class
    @help.description Abstract interface defining the contract for all memory strategies.
    Subclasses must implement add_message, get_context, get_formatted_history, and clear methods.
    @help.example
        class CustomMemory(BaseMemory):
            def add_message(self, message: Message) -> None:
                # Implementation here
                pass
            
            def get_context(self, query: Optional[str] = None) -> list[Message]:
                # Implementation here
                return []
            
            def get_formatted_history(self, query: Optional[str] = None) -> str:
                # Implementation here
                return ""
            
            def clear(self) -> None:
                # Implementation here
                pass
    """
    
    def __init__(self, token_budget: int = 4000):
        # @help.description Initialize memory with token budget. Used for metrics tracking.
        self.token_budget = token_budget
        self.metrics = MemoryMetrics(context_token_budget=token_budget)
    
    @abstractmethod
    def add_message(self, message: Message) -> None:
        """
        Add a new message to memory.
        
        @help.title Add Message Method
        @help.description Adds a message to the memory buffer. Implementation varies by strategy:
        - FIFO: Adds to sliding window, evicts oldest if full
        - Priority: Stores with embedding for semantic search
        - Hybrid: Adds to recent buffer, triggers summarization if needed
        """
        pass
    
    @abstractmethod
    def get_context(self, query: Optional[str] = None) -> list[Message]:
        """
        Retrieve messages for context window.
        
        @help.title Get Context Method
        @help.description Returns list of messages to include in LLM context.
        Query parameter used by Priority strategy for semantic similarity search.
        """
        pass
    
    @abstractmethod
    def get_formatted_history(self, query: Optional[str] = None) -> str:
        """
        Get formatted conversation history for LLM prompt.
        
        @help.title Get Formatted History Method
        @help.description Returns formatted string ready for LLM prompt construction.
        Format: "Human: {content}\nAssistant: {content}\n..."
        Hybrid strategy includes summary prefix for older messages.
        """
        pass
    
    @abstractmethod
    def clear(self) -> None:
        """
        Clear all memory.
        
        @help.title Clear Method
        @help.description Resets memory buffer and metrics to initial state.
        Useful for starting new conversations or testing.
        """
        pass
    
    def get_metrics(self) -> MemoryMetrics:
        """
        Return current metrics.
        
        @help.title Get Metrics Method
        @help.description Returns current performance metrics for monitoring and comparison.
        """
        return self.metrics
