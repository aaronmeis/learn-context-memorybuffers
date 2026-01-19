@echo off
REM Setup script for Windows

echo Setting up Memory Buffer Comparison Application...

REM Check if Ollama is installed
where ollama >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Ollama is not installed. Please install it from https://ollama.ai
    exit /b 1
)

REM Pull the tinyllama model
echo Pulling tinyllama model...
ollama pull tinyllama

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Create .env file if it doesn't exist
if not exist ".env" (
    echo Creating .env file...
    copy .env.example .env
)

REM Create data directories
if not exist "chroma_data" mkdir chroma_data
if not exist "data" mkdir data

echo Setup complete!
echo To run the application:
echo   1. Make sure Ollama is running: ollama serve
echo   2. Run: streamlit run web/app.py
