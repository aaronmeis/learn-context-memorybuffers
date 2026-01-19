"""Hybrid memory implementation."""
from typing import Optional
import time

from .base import BaseMemory, Message, MemoryMetrics
from ..llm.provider import get_llm
from ..utils.token_counter import count_tokens


class HybridMemory(BaseMemory):
    """
    Hybrid memory combining FIFO buffer with LLM-generated summaries.
    
    Maintains recent messages verbatim up to a token threshold,
    then summarizes older messages to preserve context while
    managing token consumption.
    """
    
    def __init__(
        self,
        max_token_limit: int = 500,
        token_budget: int = 4000,
        summarize_threshold: float = 0.8  # Trigger at 80% of limit
    ):
        super().__init__(token_budget)
        self.max_token_limit = max_token_limit
        self.summarize_threshold = summarize_threshold
        
        # Recent messages buffer
        self.recent_buffer: list[Message] = []
        
        # Running summary of older messages
        self.summary: str = ""
        self.summary_token_count: int = 0
        
        # LLM for summarization
        self.llm = get_llm()
        
        # Track all messages for metrics
        self.all_messages: list[Message] = []
    
    def add_message(self, message: Message) -> None:
        """Add message, triggering summarization if needed."""
        start_time = time.perf_counter()
        
        # Count tokens
        message.token_count = count_tokens(message.content)
        
        # Add to recent buffer
        self.recent_buffer.append(message)
        self.all_messages.append(message)
        
        # Check if summarization needed
        current_tokens = sum(m.token_count for m in self.recent_buffer)
        if current_tokens > self.max_token_limit * self.summarize_threshold:
            self._trigger_summarization()
        
        # Update metrics
        self.metrics.total_messages_processed += 1
        self._update_metrics()
        self.metrics.retrieval_latency_ms = (time.perf_counter() - start_time) * 1000
    
    def _trigger_summarization(self) -> None:
        """Summarize oldest messages in buffer."""
        if len(self.recent_buffer) < 4:
            return
        
        # Take oldest half of buffer for summarization
        split_point = len(self.recent_buffer) // 2
        to_summarize = self.recent_buffer[:split_point]
        self.recent_buffer = self.recent_buffer[split_point:]
        
        # Format messages for summarization
        messages_text = "\n".join([
            f"{'Human' if m.role == 'user' else 'Assistant'}: {m.content}"
            for m in to_summarize
        ])
        
        # Generate summary
        summary_prompt = f"""Summarize the following conversation excerpt, 
preserving key facts, decisions, and context that may be relevant for future turns.
Be concise but complete.

Conversation:
{messages_text}

Summary:"""
        
        try:
            response = self.llm.invoke(summary_prompt)
            new_summary = response.content if hasattr(response, 'content') else str(response)
            
            # Merge with existing summary
            if self.summary:
                merge_prompt = f"""Merge these two conversation summaries into one coherent summary.
Preserve the most important information from both.

Previous summary: {self.summary}

New summary: {new_summary}

Merged summary:"""
                merge_response = self.llm.invoke(merge_prompt)
                self.summary = merge_response.content if hasattr(merge_response, 'content') else str(merge_response)
            else:
                self.summary = new_summary
            
            self.summary_token_count = count_tokens(self.summary)
            self.metrics.summarization_count += 1
            self.metrics.messages_evicted += len(to_summarize)
        except Exception as e:
            # If summarization fails, keep messages in buffer
            self.recent_buffer = to_summarize + self.recent_buffer
            print(f"Summarization failed: {e}")
    
    def get_context(self, query: Optional[str] = None) -> list[Message]:
        """Return recent messages (summary accessible separately)."""
        return self.recent_buffer
    
    def get_formatted_history(self, query: Optional[str] = None) -> str:
        """Format summary + recent messages for LLM prompt."""
        parts = []
        
        if self.summary:
            parts.append(f"[Previous conversation summary: {self.summary}]")
            parts.append("")
        
        for msg in self.recent_buffer:
            prefix = "Human" if msg.role == "user" else "Assistant"
            parts.append(f"{prefix}: {msg.content}")
        
        return "\n".join(parts)
    
    def clear(self) -> None:
        """Clear all memory."""
        self.recent_buffer.clear()
        self.all_messages.clear()
        self.summary = ""
        self.summary_token_count = 0
        self.metrics = MemoryMetrics(context_token_budget=self.token_budget)
    
    def _update_metrics(self) -> None:
        """Update memory metrics."""
        self.metrics.messages_in_context = len(self.recent_buffer)
        buffer_tokens = sum(m.token_count for m in self.recent_buffer)
        self.metrics.total_tokens_used = buffer_tokens + self.summary_token_count
        self.metrics.token_utilization_pct = (
            self.metrics.total_tokens_used / self.token_budget * 100
            if self.token_budget > 0
            else 0.0
        )
