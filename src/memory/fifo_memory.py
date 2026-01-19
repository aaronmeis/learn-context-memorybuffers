"""
FIFO memory implementation.

@help.category Memory Strategies
@help.title FIFO Memory Strategy
@help.description First-In-First-Out sliding window memory buffer. 
Maintains only the most recent N message pairs, automatically evicting oldest messages.
Simple, fast, and predictable memory usage. Best for short conversations.
"""
from collections import deque
from typing import Optional
import time

from .base import BaseMemory, Message, MemoryMetrics
from ..utils.token_counter import count_tokens


class FIFOMemory(BaseMemory):
    """
    First-In-First-Out memory buffer with sliding window.
    
    @help.title FIFO Memory Class
    @help.description Maintains only the k most recent message pairs, evicting
    oldest messages when the window is exceeded. Uses Python deque for O(1) operations.
    @help.example
        memory = FIFOMemory(window_size=5, token_budget=4000)
        memory.add_message(Message(role="user", content="Hello"))
        context = memory.get_context()  # Returns recent messages
    @help.performance O(1) add and retrieve operations. Very fast and memory-efficient.
    @help.use_case Best for short conversations where recent context is most important.
    """
    
    def __init__(
        self, 
        window_size: int = 5,
        token_budget: int = 4000,
        return_messages: bool = True
    ):
        super().__init__(token_budget)
        self.window_size = window_size
        self.buffer: deque[Message] = deque(maxlen=window_size * 2)
    
    def add_message(self, message: Message) -> None:
        """Add message to sliding window buffer."""
        start_time = time.perf_counter()
        
        # Count tokens
        message.token_count = count_tokens(message.content)
        
        # Check if we need to evict (deque with maxlen handles this automatically)
        if len(self.buffer) >= self.window_size * 2:
            evicted = self.buffer.popleft()
            self.metrics.messages_evicted += 1
        
        self.buffer.append(message)
        self.metrics.total_messages_processed += 1
        
        # Update metrics
        self._update_metrics()
        self.metrics.retrieval_latency_ms = (time.perf_counter() - start_time) * 1000
    
    def get_context(self, query: Optional[str] = None) -> list[Message]:
        """Return all messages in current window (query ignored for FIFO)."""
        return list(self.buffer)
    
    def get_formatted_history(self, query: Optional[str] = None) -> str:
        """Format messages for LLM prompt."""
        lines = []
        for msg in self.buffer:
            prefix = "Human" if msg.role == "user" else "Assistant"
            lines.append(f"{prefix}: {msg.content}")
        return "\n".join(lines)
    
    def clear(self) -> None:
        """Clear the buffer."""
        self.buffer.clear()
        self.metrics = MemoryMetrics(context_token_budget=self.token_budget)
    
    def _update_metrics(self) -> None:
        """Update memory metrics."""
        self.metrics.messages_in_context = len(self.buffer)
        self.metrics.total_tokens_used = sum(m.token_count for m in self.buffer)
        self.metrics.token_utilization_pct = (
            self.metrics.total_tokens_used / self.token_budget * 100
            if self.token_budget > 0
            else 0.0
        )
