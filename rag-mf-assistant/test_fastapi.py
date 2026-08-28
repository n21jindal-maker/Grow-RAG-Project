import os
import sys

# Ensure modules can be imported
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from api.main import app

def test_health():
    with TestClient(app) as client:
        response = client.get("/health")
        print("Health Check Response:", response.status_code, response.json())
        assert response.status_code == 200

def test_chat():
    with TestClient(app) as client:
        response = client.post("/chat", json={"query": "What is the exit load for HDFC Mid-Cap Opportunities Fund?"})
        print("Chat Response:", response.status_code, response.json())
        assert response.status_code == 200

if __name__ == "__main__":
    print("Running FastAPI tests...")
    test_health()
    print("Health check passed.")
    test_chat()
    print("Chat check passed.")
