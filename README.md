# Memory Buffer Comparison Application

> Compare FIFO, Priority, and Hybrid memory buffering strategies for LLM chatbots using Streamlit, Ollama, and local embeddings

A Streamlit application that demonstrates and compares three memory buffering strategies for LLM-powered chatbots:
1. **FIFO (First-In-First-Out)** - Sliding window of recent messages
2. **Priority-Based** - Semantic relevance scoring with intelligent retention
3. **Hybrid** - ConversationSummaryBuffer combining FIFO with LLM-generated summaries

## Quick Start

### Using Docker Compose (Recommended)

1. Make sure Docker Desktop is running
2. Start the application:
   ```bash
   docker-compose up
   ```
3. Open your browser to `http://localhost:8501`

The Docker setup will automatically:
- Pull and start Ollama with the `tinyllama` model (smallest model)
- Start the Streamlit application
- Set up all required dependencies

### Local Development

1. Install Ollama from https://ollama.ai
2. Pull the tinyllama model:
   ```bash
   ollama pull tinyllama
   ```
3. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Copy environment file:
   ```bash
   cp .env.example .env
   ```
6. Run the application:
   ```bash
   streamlit run web/app.py
   ```

## Features

- **Interactive Chat Interface**: Chat with the LLM using different memory strategies
- **Real-time Metrics**: View token usage, message counts, and performance metrics
- **Strategy Comparison**: Compare how different strategies handle context
- **Visual Memory State**: See what messages are retained in each strategy

## Memory Strategies

### FIFO Buffer
Maintains a sliding window of the most recent N message pairs. Simple and fast, but may lose important early context.

### Priority Buffer
Uses semantic similarity to retrieve the most relevant messages. Better at preserving important context even if it's not recent.

### Hybrid Buffer
Combines recent messages with LLM-generated summaries of older messages. Balances detail preservation with token efficiency.

## Configuration

Edit `.env` to customize:
- `LLM_MODEL`: Ollama model to use (default: `tinyllama`)
- `FIFO_WINDOW_SIZE`: Number of message pairs in FIFO buffer
- `PRIORITY_TOP_K`: Number of messages to retrieve in priority strategy
- `HYBRID_TOKEN_LIMIT`: Token limit before summarization triggers

## Architecture

- **Streamlit**: Web UI framework
- **Ollama**: Local LLM inference (using tinyllama)
- **LangChain**: Memory management abstractions
- **ChromaDB**: Vector store for semantic retrieval
- **Sentence Transformers**: Local embeddings
