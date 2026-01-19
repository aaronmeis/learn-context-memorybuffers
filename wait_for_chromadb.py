"""Wait for ChromaDB server to be ready."""
import time
import sys
import os
from urllib.parse import urlparse

# Get ChromaDB URL from environment or use default
chroma_url = os.getenv("CHROMA_SERVER_URL", "http://localhost:8000")
max_retries = 30
retry_delay = 2

def check_chromadb_ready(url: str) -> bool:
    """Check if ChromaDB server is ready."""
    try:
        import requests
        parsed = urlparse(url)
        health_url = f"{parsed.scheme}://{parsed.netloc}/api/v1/heartbeat"
        response = requests.get(health_url, timeout=2)
        return response.status_code == 200
    except Exception:
        return False

if __name__ == "__main__":
    print(f"Waiting for ChromaDB at {chroma_url}...")
    
    for i in range(max_retries):
        if check_chromadb_ready(chroma_url):
            print("ChromaDB is ready!")
            sys.exit(0)
        print(f"Attempt {i+1}/{max_retries}...")
        time.sleep(retry_delay)
    
    print(f"ChromaDB did not become ready after {max_retries * retry_delay} seconds")
    sys.exit(1)
