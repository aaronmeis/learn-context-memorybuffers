"""
Priority-based memory implementation.

@help.category Memory Strategies
@help.title Priority Memory Strategy
@help.description Semantic relevance-based memory buffer using vector similarity search.
Retrieves most relevant messages based on query similarity, combining semantic and recency scores.
Best for long conversations where important context may be older.
"""
from typing import Optional
import time

from .base import BaseMemory, Message, MemoryMetrics
from ..llm.embeddings import get_embedding_model
from ..utils.token_counter import count_tokens

# Try to import numpy
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

# Try to import ChromaDB, but fallback to in-memory if not available
try:
    from langchain_chroma import Chroma
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False

# Try to import ChromaDB client for server connection
try:
    import chromadb
    CHROMADB_CLIENT_AVAILABLE = True
except ImportError:
    CHROMADB_CLIENT_AVAILABLE = False


class PriorityMemory(BaseMemory):
    """
    Priority-based memory buffer with semantic retrieval.
    
    @help.title Priority Memory Class
    @help.description Assigns relevance scores to messages and selectively retains
    high-priority content. Uses vector similarity for retrieval via ChromaDB or in-memory embeddings.
    @help.example
        memory = PriorityMemory(
            top_k=5,
            token_budget=4000,
            persist_directory="./chroma_data"
        )
        memory.add_message(Message(role="user", content="Budget is $50k"))
        # Later, query retrieves relevant messages
        context = memory.get_context(query="What was the budget?")
    @help.performance O(k) retrieval from vector store. Slower than FIFO but more intelligent.
    @help.use_case Best for long conversations where important information may be older.
    @help.requirements ChromaDB (optional, falls back to in-memory) and sentence-transformers.
    """
    
    def __init__(
        self,
        top_k: int = 5,
        token_budget: int = 4000,
        recency_weight: float = 0.3,
        semantic_weight: float = 0.7,
        persist_directory: str = "./chroma_data",
        chroma_server_url: Optional[str] = None
    ):
        super().__init__(token_budget)
        self.top_k = top_k
        self.recency_weight = recency_weight
        self.semantic_weight = semantic_weight
        
        # All messages storage
        self.all_messages: list[Message] = []
        
        # Embedding model (may be None if using ChromaDB defaults)
        try:
            self.embeddings = get_embedding_model()
        except ImportError:
            self.embeddings = None
        
        # Vector store for semantic retrieval (use in-memory if ChromaDB unavailable)
        self.use_chromadb = CHROMADB_AVAILABLE
        if self.use_chromadb:
            try:
                # Connect to ChromaDB server if URL provided, otherwise use local persistence
                if chroma_server_url:
                    # Connect to ChromaDB server
                    if CHROMADB_CLIENT_AVAILABLE:
                        # Parse URL to extract host and port
                        from urllib.parse import urlparse
                        parsed = urlparse(chroma_server_url)
                        host = parsed.hostname or "localhost"
                        port = parsed.port or 8000
                        
                        chroma_client = chromadb.HttpClient(host=host, port=port)
                        self.vector_store = Chroma(
                            collection_name="conversation_memory",
                            embedding_function=self.embeddings,
                            client=chroma_client
                        )
                    else:
                        # Fallback: try using chroma_server_url parameter directly
                        self.vector_store = Chroma(
                            collection_name="conversation_memory",
                            embedding_function=self.embeddings,
                            chroma_server_url=chroma_server_url
                        )
                else:
                    # Local ChromaDB with persistence
                    self.vector_store = Chroma(
                        collection_name="conversation_memory",
                        embedding_function=self.embeddings,
                        persist_directory=persist_directory
                    )
            except Exception as e:
                # Fallback to in-memory if ChromaDB fails
                print(f"ChromaDB initialization failed: {e}, using in-memory fallback")
                self.use_chromadb = False
        
        if not self.use_chromadb:
            # In-memory storage for embeddings
            self.message_embeddings: list[np.ndarray] = []
            self.vector_store = None
            # For TF-IDF fallback, we need to fit the vectorizer
            from ..llm.embeddings import SENTENCE_TRANSFORMERS_AVAILABLE
            if not SENTENCE_TRANSFORMERS_AVAILABLE:
                self._fitted_vectorizer = False
        
        self._message_counter = 0
    
    def add_message(self, message: Message) -> None:
        """Add message with embedding for semantic retrieval."""
        start_time = time.perf_counter()
        
        # Count tokens
        message.token_count = count_tokens(message.content)
        
        # Store in full history
        self.all_messages.append(message)
        self._message_counter += 1
        
        # Add to vector store
        if self.use_chromadb and self.vector_store:
            from langchain_core.documents import Document
            doc = Document(
                page_content=message.content,
                metadata={
                    "role": message.role,
                    "timestamp": message.timestamp.isoformat(),
                    "message_index": self._message_counter,
                    "token_count": message.token_count
                }
            )
            self.vector_store.add_documents([doc])
        else:
            # Store embedding in memory
            from ..llm.embeddings import SENTENCE_TRANSFORMERS_AVAILABLE
            if SENTENCE_TRANSFORMERS_AVAILABLE:
                embedding = self.embeddings.encode(message.content)
                self.message_embeddings.append(np.array(embedding))
            else:
                # For TF-IDF, we'll compute embeddings on-demand
                self.message_embeddings.append(None)  # Placeholder
        
        # Update metrics
        self.metrics.total_messages_processed += 1
        self.metrics.retrieval_latency_ms = (time.perf_counter() - start_time) * 1000
        
        # Update context metrics (for comparison tab)
        # This ensures metrics are updated even when this strategy isn't active
        self._update_metrics()
    
    def get_context(self, query: Optional[str] = None) -> list[Message]:
        """Retrieve most relevant messages based on semantic similarity."""
        start_time = time.perf_counter()
        
        if not query or len(self.all_messages) <= self.top_k:
            # Return recent messages if no query or small history
            return self.all_messages[-self.top_k:]
        
        # Semantic search
        if self.use_chromadb and self.vector_store:
            docs = self.vector_store.similarity_search_with_score(
                query, 
                k=min(self.top_k * 2, len(self.all_messages))
            )
            
            # Score combination: semantic + recency
            scored_messages = []
            max_index = len(self.all_messages)
            
            for doc, semantic_score in docs:
                msg_index = doc.metadata.get("message_index", 0)
                recency_score = msg_index / max_index if max_index > 0 else 0.0
                
                # Lower distance = higher score, so invert semantic_score
                combined_score = (
                    self.semantic_weight * (1 - semantic_score) +
                    self.recency_weight * recency_score
                )
                
                # Find original message
                for msg in self.all_messages:
                    if msg.content == doc.page_content:
                        msg.priority_score = combined_score
                        scored_messages.append((combined_score, msg))
                        break
        else:
            # In-memory similarity search using sentence transformers
            from ..llm.embeddings import SENTENCE_TRANSFORMERS_AVAILABLE
            scored_messages = []
            max_index = len(self.all_messages)
            
            if SENTENCE_TRANSFORMERS_AVAILABLE and NUMPY_AVAILABLE:
                # Use sentence transformers embeddings
                query_embedding = np.array(self.embeddings.encode(query))
                for i, (msg, msg_embedding) in enumerate(zip(self.all_messages, self.message_embeddings)):
                    if msg_embedding is None:
                        continue
                    # Cosine similarity
                    similarity = np.dot(query_embedding, msg_embedding) / (
                        np.linalg.norm(query_embedding) * np.linalg.norm(msg_embedding) + 1e-10
                    )
                    semantic_score = 1 - similarity
                    
                    recency_score = (i + 1) / max_index if max_index > 0 else 0.0
                    
                    combined_score = (
                        self.semantic_weight * (1 - semantic_score) +
                        self.recency_weight * recency_score
                    )
                    
                    msg.priority_score = combined_score
                    scored_messages.append((combined_score, msg))
            else:
                # Fallback: just use recency if embeddings not available
                for i, msg in enumerate(self.all_messages):
                    recency_score = (i + 1) / max_index if max_index > 0 else 0.0
                    combined_score = recency_score  # Only recency, no semantic
                    msg.priority_score = combined_score
                    scored_messages.append((combined_score, msg))
        
        # Sort by score and take top k
        scored_messages.sort(key=lambda x: x[0], reverse=True)
        selected = [msg for _, msg in scored_messages[:self.top_k]]
        
        # Sort by timestamp for coherent ordering
        selected.sort(key=lambda m: m.timestamp)
        
        # Update metrics
        self.metrics.messages_in_context = len(selected)
        self.metrics.messages_evicted = len(self.all_messages) - len(selected)
        self.metrics.total_tokens_used = sum(m.token_count for m in selected)
        self.metrics.token_utilization_pct = (
            self.metrics.total_tokens_used / self.token_budget * 100
            if self.token_budget > 0
            else 0.0
        )
        self.metrics.retrieval_latency_ms = (time.perf_counter() - start_time) * 1000
        
        return selected
    
    def get_formatted_history(self, query: Optional[str] = None) -> str:
        """Format retrieved messages for LLM prompt."""
        messages = self.get_context(query)
        lines = []
        for msg in messages:
            prefix = "Human" if msg.role == "user" else "Assistant"
            lines.append(f"{prefix}: {msg.content}")
        return "\n".join(lines)
    
    def _update_metrics(self) -> None:
        """Update metrics based on current state."""
        # Calculate what the context would be (recent messages if small, or top_k if larger)
        if len(self.all_messages) <= self.top_k:
            context_messages = self.all_messages
        else:
            # Use recent messages as a proxy (actual context depends on query)
            context_messages = self.all_messages[-self.top_k:]
        
        self.metrics.messages_in_context = len(context_messages)
        self.metrics.messages_evicted = max(0, len(self.all_messages) - len(context_messages))
        self.metrics.total_tokens_used = sum(m.token_count for m in context_messages)
        self.metrics.token_utilization_pct = (
            self.metrics.total_tokens_used / self.token_budget * 100
            if self.token_budget > 0
            else 0.0
        )
    
    def clear(self) -> None:
        """Clear all memory."""
        self.all_messages.clear()
        if self.use_chromadb and self.vector_store:
            try:
                self.vector_store.delete_collection()
            except Exception:
                pass  # Collection might not exist
        else:
            self.message_embeddings.clear()
        self._message_counter = 0
        self.metrics = MemoryMetrics(context_token_budget=self.token_budget)
