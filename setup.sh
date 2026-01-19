#!/bin/bash
# Setup script for local development

echo "Setting up Memory Buffer Comparison Application..."

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "Ollama is not installed. Please install it from https://ollama.ai"
    exit 1
fi

# Pull the tinyllama model
echo "Pulling tinyllama model..."
ollama pull tinyllama

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cp .env.example .env
fi

# Create data directories
mkdir -p chroma_data
mkdir -p data

echo "Setup complete!"
echo "To run the application:"
echo "  1. Make sure Ollama is running: ollama serve"
echo "  2. Run: streamlit run web/app.py"
