# Memory Buffer Comparison Application

> Compare FIFO, Priority, and Hybrid memory buffering strategies for LLM chatbots using Streamlit, Ollama, and local embeddings

A Streamlit application that demonstrates and compares three memory buffering strategies for LLM-powered chatbots:
1. **FIFO (First-In-First-Out)** - Sliding window of recent messages
2. **Priority-Based** - Semantic relevance scoring with intelligent retention
3. **Hybrid** - ConversationSummaryBuffer combining FIFO with LLM-generated summaries

## Prerequisites

- **Python 3.10+** (3.11 or 3.12 recommended)
- **Ollama** installed and running ([Download](https://ollama.ai))
- **Docker Desktop** (optional, for Docker setup)

## Quick Start

### Using Docker Compose (Recommended)

1. **Make sure Docker Desktop is running**

2. **Start the application**:
   ```bash
   docker-compose up
   ```

3. **Wait for initial setup** (first time only):
   - Docker will pull the Ollama image
   - Ollama will download the `tinyllama` model (~1.1GB)
   - This may take 5-10 minutes on first run

4. **Open your browser** to `http://localhost:8501`

The Docker setup will automatically:
- Pull and start Ollama with the `tinyllama` model (smallest model)
- Start ChromaDB server in a container for vector storage
- Start the Streamlit application
- Set up all required dependencies
- Wait for Ollama and ChromaDB to be ready before starting the app

### Local Development

1. **Install Ollama** from https://ollama.ai and ensure it's running:
   ```bash
   ollama serve
   ```

2. **Pull the tinyllama model**:
   ```bash
   ollama pull tinyllama
   ```

3. **Set up Python environment**:
   
   **Option A: Use setup script (recommended)**
   ```bash
   # Windows
   setup.bat
   
   # Linux/Mac
   chmod +x setup.sh
   ./setup.sh
   ```
   
   **Option B: Manual setup**
   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Copy environment file
   cp .env.example .env  # On Windows: copy .env.example .env
   
   # Create data directories
   mkdir chroma_data data
   ```

4. **Run the application**:
   ```bash
   streamlit run web/app.py
   ```

5. **Open your browser** to `http://localhost:8501`

**Important**: 
- Make sure Ollama is running (`ollama serve`) before starting the Streamlit app, otherwise you'll get connection errors.
- For local development, ChromaDB will use local file storage. To use a ChromaDB server, set `CHROMA_SERVER_URL=http://localhost:8000` in your `.env` file and run ChromaDB separately (or use Docker Compose).

## Features

- **Interactive Chat Interface**: Chat with the LLM using different memory strategies
- **Real-time Metrics**: View token usage, message counts, and performance metrics
- **Strategy Comparison**: Compare how different strategies handle context
- **Visual Memory State**: See what messages are retained in each strategy
- **Comprehensive Help System**: Modern, indexed HTML help documentation generated from source code

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
- **ChromaDB**: Vector store for semantic retrieval (runs in Docker container, falls back to in-memory if unavailable)
- **Sentence Transformers**: Local embeddings (optional, ChromaDB can use default embeddings)

## Troubleshooting

### Ollama Connection Issues
- Ensure Ollama is running: `ollama serve`
- Check if model is available: `ollama list`
- Verify Ollama is accessible: `curl http://localhost:11434/api/tags` (or visit in browser)

### Docker Issues
- Ensure Docker Desktop is running
- Check Docker logs: `docker-compose logs ollama` or `docker-compose logs chromadb`
- Try rebuilding: `docker-compose up --build`
- ChromaDB runs on port 8000 - ensure it's not in use

### Port Conflicts
- If port 8501 is in use, change it in `docker-compose.yml` or use: `streamlit run web/app.py --server.port 8502`
- If port 11434 is in use, Ollama is already running locally
- If port 8000 is in use, ChromaDB is already running locally (change in docker-compose.yml)

### Memory/Import Errors
- On Windows ARM64, some dependencies (like sentence-transformers) may not install. The app will fall back to ChromaDB's default embeddings.
- If ChromaDB fails, Priority memory will use a simplified in-memory approach.

For more detailed troubleshooting, see [QUICKSTART.md](QUICKSTART.md).

## Documentation

### Help System

The project includes a comprehensive help documentation system that extracts documentation from `@help` tags embedded in the source code.

**View Help Documentation:**
- Run `open_help.bat` (Windows) or `open_help.sh` (Linux/Mac) to open in your browser
- Or manually open `docs/help/index.html` in your browser

**Generate Help Documentation:**
```bash
# Windows
build_help.bat

# Linux/Mac
chmod +x build_help.sh
./build_help.sh

# Or directly with Python
python scripts/build_help.py
```

**Help Tag Format:**
```python
"""
@help.category Memory Strategies
@help.title FIFO Memory Strategy
@help.description Description of the feature
@help.example
    code example here
"""
```

For complete documentation on the help system, see [HELP_SYSTEM.md](HELP_SYSTEM.md).

### Additional Documentation

- [QUICKSTART.md](QUICKSTART.md) - Quick start guide
- [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - Project overview
- [HELP_SYSTEM.md](HELP_SYSTEM.md) - Help system documentation
- [docs/HELP_README.md](docs/HELP_README.md) - Help system quick reference
