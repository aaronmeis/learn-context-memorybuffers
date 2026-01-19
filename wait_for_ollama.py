"""Wait for Ollama to be ready."""
import time
import requests
import sys
from src.config.settings import get_settings


def wait_for_ollama(max_attempts=30, delay=2):
    """Wait for Ollama API to be available."""
    settings = get_settings()
    base_url = settings.ollama_base_url
    
    for attempt in range(max_attempts):
        try:
            # Try to connect to Ollama
            response = requests.get(f"{base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                print("✓ Ollama is ready!")
                return True
        except Exception as e:
            if attempt < max_attempts - 1:
                print(f"Waiting for Ollama... (attempt {attempt + 1}/{max_attempts})")
                time.sleep(delay)
            else:
                print(f"✗ Ollama failed to start: {e}")
                return False
    
    return False


if __name__ == "__main__":
    success = wait_for_ollama()
    sys.exit(0 if success else 1)
