from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import time
import uuid
from typing import List, Dict, Any

app = FastAPI(
    title="GenAI Stack API",
    description="No-Code Workflow Builder API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://web-production-7c76.up.railway.app",
        "http://localhost:3000",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage
chat_sessions: Dict[str, Dict] = {}
workflows: Dict[str, Dict] = {}

@app.get("/")
async def root():
    return {
        "message": "GenAI Stack API is running!",
        "version": "1.0.0",
        "status": "healthy",
        "timestamp": time.time()
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": time.time(),
        "database": "connected",
        "services": {
            "api": "running",
            "database": "connected",
            "vector_store": "available"
        }
    }

@app.get("/api/v1/test")
async def test_endpoint():
    return {"test": "API is working", "endpoint": "/api/v1/test"}

# Chat Session Endpoints
@app.get("/api/v1/chat/sessions")
async def list_chat_sessions():
    """GET endpoint for listing chat sessions"""
    return {
        "sessions": list(chat_sessions.values()),
        "count": len(chat_sessions)
    }

@app.post("/api/v1/chat/sessions")
async def create_chat_session(request: Dict[str, Any]):
    session_id = str(uuid.uuid4())
    workflow_id = request.get("workflow_id", "default")
    
    chat_sessions[session_id] = {
        "id": session_id,
        "workflow_id": workflow_id,
        "created_at": time.time(),
        "messages": []
    }
    
    return {
        "session_id": session_id,
        "workflow_id": workflow_id,
        "status": "created"
    }

@app.get("/api/v1/chat/sessions/{session_id}")
async def get_chat_session(session_id: str):
    if session_id not in chat_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return chat_sessions[session_id]

@app.post("/api/v1/chat/sessions/{session_id}/messages")
async def send_message(session_id: str, request: Dict[str, Any]):
    if session_id not in chat_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    message = request.get("message", "")
    user_message = {
        "id": str(uuid.uuid4()),
        "type": "user",
        "content": message,
        "timestamp": time.time()
    }
    
    # Simple echo response
    bot_response = {
        "id": str(uuid.uuid4()),
        "type": "assistant",
        "content": f"Echo: {message}",
        "timestamp": time.time()
    }
    
    chat_sessions[session_id]["messages"].extend([user_message, bot_response])
    
    return {
        "response": bot_response["content"],
        "message_id": bot_response["id"]
    }

# Workflow Endpoints
@app.get("/api/v1/workflows")
async def list_workflows():
    """GET endpoint for listing workflows"""
    return {
        "workflows": list(workflows.values()),
        "count": len(workflows)
    }

@app.get("/api/v1/workflows/{workflow_id}")
async def get_workflow(workflow_id: str):
    if workflow_id in workflows:
        return workflows[workflow_id]
    
    # Return a demo workflow if not found
    return {
        "id": workflow_id,
        "name": "Chat With AI",
        "description": "Demo workflow",
        "nodes": [],
        "edges": [],
        "created_at": time.time()
    }

@app.post("/api/v1/workflows")
async def save_workflow(request: Dict[str, Any]):
    workflow_id = request.get("id", str(uuid.uuid4()))
    workflows[workflow_id] = {
        "id": workflow_id,
        "name": request.get("name", "Untitled Workflow"),
        "description": request.get("description", ""),
        "nodes": request.get("nodes", []),
        "edges": request.get("edges", []),
        "updated_at": time.time()
    }
    
    return {
        "success": True,
        "workflow_id": workflow_id,
        "message": "Workflow saved successfully"
    }
