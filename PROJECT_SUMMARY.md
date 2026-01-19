# Project Summary

## What Was Built

A complete, production-ready Streamlit application that demonstrates and compares three memory buffering strategies for LLM-powered chatbots:

1. **FIFO (First-In-First-Out)** - Sliding window buffer
2. **Priority-Based** - Semantic relevance retrieval
3. **Hybrid** - Summary buffer with recent messages

## Key Features

✅ **Full Implementation** of all three memory strategies  
✅ **Streamlit Web UI** with interactive chat interface  
✅ **Real-time Metrics** tracking and visualization  
✅ **Strategy Comparison** dashboard  
✅ **Memory State Inspection** for debugging  
✅ **Docker Compose** setup for easy deployment  
✅ **Ollama Integration** using the smallest model (tinyllama)  
✅ **Local Embeddings** using Sentence Transformers  
✅ **Vector Store** using ChromaDB for semantic search  

## Project Structure

```
code_example2/
├── src/                    # Source code
│   ├── config/            # Configuration management
│   ├── memory/            # Memory implementations
│   │   ├── base.py       # Abstract base class
│   │   ├── fifo_memory.py
│   │   ├── priority_memory.py
│   │   └── hybrid_memory.py
│   ├── llm/              # LLM provider abstraction
│   └── utils/            # Utilities (token counting)
├── web/
│   └── app.py            # Streamlit application
├── requirements.txt      # Python dependencies
├── Dockerfile            # Docker image definition
├── docker-compose.yml    # Multi-container setup
├── wait_for_ollama.py    # Health check script
├── setup.sh/.bat         # Local setup scripts
└── README.md             # Documentation
```

## Technology Stack

- **Frontend**: Streamlit
- **LLM**: Ollama (tinyllama model)
- **Memory**: LangChain memory abstractions
- **Embeddings**: Sentence Transformers (all-MiniLM-L6-v2)
- **Vector Store**: ChromaDB
- **Containerization**: Docker & Docker Compose

## How to Run

### Docker (Recommended)
```bash
docker-compose up
```
Then open http://localhost:8501

### Local
```bash
ollama pull tinyllama
pip install -r requirements.txt
streamlit run web/app.py
```

## Memory Strategy Details

### FIFO Memory
- **Implementation**: `ConversationBufferWindowMemory` from LangChain
- **Behavior**: Maintains last N message pairs, evicts oldest
- **Use Case**: Short conversations, predictable memory usage
- **Performance**: O(1) add/retrieve operations

### Priority Memory
- **Implementation**: Custom with ChromaDB vector store
- **Behavior**: Semantic similarity search + recency weighting
- **Use Case**: Long conversations, important context preservation
- **Performance**: O(k) retrieval from vector store

### Hybrid Memory
- **Implementation**: `ConversationSummaryBufferMemory` from LangChain
- **Behavior**: Recent messages + LLM-generated summaries
- **Use Case**: Balanced detail preservation and token efficiency
- **Performance**: O(1) + summarization overhead when triggered

## Configuration

All settings are in `.env` file:
- `LLM_MODEL`: tinyllama (smallest model)
- `FIFO_WINDOW_SIZE`: 5 message pairs
- `PRIORITY_TOP_K`: 5 messages
- `HYBRID_TOKEN_LIMIT`: 500 tokens
- `CONTEXT_WINDOW_BUDGET`: 4000 tokens

## Testing the Differences

Try this conversation to see strategy differences:

1. "My budget is $50,000"
2. "Deadline is March 2025"
3. "Team has 5 developers"
4. "Using Python and React"
5. "Any timeline concerns?"
6. "What was the budget?" ← Tests memory!

FIFO may have evicted the budget, but Priority and Hybrid should remember it.

## Next Steps

- Add Redis for session persistence (optional)
- Add SQLite for conversation archiving (optional)
- Add unit tests
- Add performance benchmarks
- Deploy to cloud (optional)
