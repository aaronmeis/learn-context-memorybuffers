# Quick Start Guide

## Option 1: Docker Compose (Easiest)

1. **Prerequisites**: Docker Desktop must be running

2. **Start the application**:
   ```bash
   docker-compose up
   ```

3. **Wait for setup** (first time only):
   - Docker will pull the Ollama image
   - Ollama will download the `tinyllama` model (~1.1GB)
   - This may take 5-10 minutes on first run

4. **Access the app**:
   - Open your browser to `http://localhost:8501`
   - The app will wait for Ollama to be ready automatically

5. **Stop the application**:
   ```bash
   docker-compose down
   ```

## Option 2: Local Development

1. **Install Ollama**:
   - Download from https://ollama.ai
   - Install and start Ollama

2. **Pull the model**:
   ```bash
   ollama pull tinyllama
   ```

3. **Set up Python environment**:
   ```bash
   # Windows
   setup.bat
   
   # Linux/Mac
   chmod +x setup.sh
   ./setup.sh
   ```

4. **Run the application**:
   ```bash
   streamlit run web/app.py
   ```

5. **Access the app**:
   - Open your browser to `http://localhost:8501`

## Troubleshooting

### Ollama connection issues
- Make sure Ollama is running: `ollama serve`
- Check if the model is available: `ollama list`
- Verify Ollama is accessible: `curl http://localhost:11434/api/tags`

### Docker issues
- Ensure Docker Desktop is running
- Check Docker logs: `docker-compose logs ollama`
- Try rebuilding: `docker-compose up --build`

### Port conflicts
- If port 8501 is in use, change it in `docker-compose.yml`
- If port 11434 is in use, Ollama is already running locally

## First Use Tips

1. **Start with FIFO strategy** - Simplest to understand
2. **Try a multi-turn conversation** - Ask follow-up questions to see memory differences
3. **Compare strategies** - Use the "Comparison" tab to see metrics
4. **Inspect memory state** - Use the "Memory State" tab to see what each strategy remembers

## Example Conversation

Try this to see the differences:

1. "My budget for the project is $50,000."
2. "We need to complete it by March 2025."
3. "The team consists of 5 developers."
4. "We're using Python and React."
5. "Any concerns about the timeline?"
6. "What was the budget we discussed?" ← This tests memory!

The Priority and Hybrid strategies should remember the budget, while FIFO might have evicted it.

## Documentation & Help

### View Help Documentation

The project includes comprehensive HTML help documentation:

**Quick Access:**
```bash
# Windows
open_help.bat

# Linux/Mac
chmod +x open_help.sh
./open_help.sh
```

Or manually open `docs/help/index.html` in your browser.

**Features:**
- Full-text search across all topics
- Category-based navigation
- Code examples and usage guides
- Performance notes and best practices

### Generate Help Documentation

To rebuild the help documentation from source code:

```bash
# Windows
build_help.bat

# Linux/Mac
chmod +x build_help.sh
./build_help.sh

# Or directly
python scripts/build_help.py
```

For complete documentation on the help system, see [HELP_SYSTEM.md](HELP_SYSTEM.md).