import os
import sys
import traceback
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

# Add parent directory to sys.path so we can import from the main project
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

from main import MutualFundAssistant

app = FastAPI(
    title="Mutual Fund Facts Assistant API",
    description="API for HDFC Mutual Fund RAG Assistant",
    version="1.0.0"
)

# Configure CORS
frontend_url = os.getenv("FRONTEND_URL", "*")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_url] if frontend_url != "*" else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the assistant at startup
assistant = None

@app.on_event("startup")
async def startup_event():
    global assistant
    print("Initializing Mutual Fund Assistant...")
    assistant = MutualFundAssistant()
    print("Mutual Fund Assistant initialized successfully.")

# Pydantic models
class ChatRequest(BaseModel):
    query: str

class ChatResponse(BaseModel):
    answer: str
    source_url: Optional[str] = None
    last_updated: Optional[str] = None
    query_type: str

@app.get("/health")
def health_check():
    return {"status": "healthy", "assistant_initialized": assistant is not None}

@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest):
    if assistant is None:
        raise HTTPException(status_code=503, detail="Assistant is not initialized yet.")
    
    try:
        response_data = assistant.process_query_json(request.query)
        return ChatResponse(
            answer=response_data.get("answer", ""),
            source_url=response_data.get("source_url"),
            last_updated=response_data.get("last_updated"),
            query_type=response_data.get("query_type", "factual")
        )
    except Exception as e:
        print(f"Error processing query: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal server error while processing query.")

@app.post("/chat/stream")
def chat_stream_endpoint(request: ChatRequest):
    if assistant is None:
        raise HTTPException(status_code=503, detail="Assistant is not initialized yet.")
    
    return StreamingResponse(
        assistant.process_query_stream(request.query),
        media_type="text/event-stream"
    )

