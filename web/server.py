#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NFM-SV Web: FastAPI Server for Phase 11 Vibe Interface
Features:
- WebSocket streaming for real-time output
- REST API for task management
- Static file serving for frontend
"""
import os
import sys
import json
import asyncio
from typing import Dict, List, Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from frame import FrameEngine, RuleNode
from mnemo import MemoryBank, GlobalMnemo
from spark import SparkExecutor, GitOps
from vibe import VibeInterface
from nexus import NexusBrain
from knowledge import KnowledgeBase
from knowledge.code_patterns import generate_code_guidance

app = FastAPI(title="NFM-SV Vibe Web Interface", version="0.1.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state (in production, use database)
active_sessions: Dict[str, dict] = {}

# Models
class TaskRequest(BaseModel):
    task: str
    context_tags: List[str] = ["general"]

class ChatMessage(BaseModel):
    role: str
    content: str

@app.get("/", response_class=HTMLResponse)
async def get_frontend():
    """Serve the main frontend"""
    html_path = os.path.join(os.path.dirname(__file__), "templates", "index.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>NFM-SV Web Interface</h1><p>Frontend not found.</p>"

@app.post("/api/task")
async def create_task(request: TaskRequest):
    """Start a new task execution"""
    session_id = f"session_{len(active_sessions) + 1}"
    
    # Initialize session (simplified for demo)
    test_dir = os.path.join(os.path.dirname(__file__), "..", "test_project_web")
    if not os.path.exists(test_dir):
        os.makedirs(test_dir)
        
    active_sessions[session_id] = {
        "status": "initialized",
        "task": request.task,
        "context_tags": request.context_tags,
        "test_dir": test_dir,
        "todos": [],
        "current_todo": -1,
    }
    
    return {"session_id": session_id, "status": "initialized"}

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time streaming"""
    await websocket.accept()
    
    if session_id not in active_sessions:
        await websocket.close(code=1008, reason="Session not found")
        return
    
    session = active_sessions[session_id]
    
    try:
        # Send initial dashboard
        await websocket.send_json({
            "type": "dashboard",
            "plan": "# Implementation Plan\n1. Analyze Request\n2. Search Knowledge\n3. Generate Code\n4. Verify Output",
            "progress": "Ready",
            "confidence": 0.0,
            "hit_keywords": []
        })
        
        # Simulate task execution with streaming
        await simulate_task_execution(websocket, session)
        
    except WebSocketDisconnect:
        print(f"Client disconnected: {session_id}")
    except Exception as e:
        await websocket.send_json({"type": "error", "message": str(e)})

async def simulate_task_execution(websocket: WebSocket, session: dict):
    """Simulate the NFM-SV execution pipeline with streaming"""
    # 1. Analyze
    await stream_message(websocket, "🧠 Analyzing task...", "THINKING")
    await asyncio.sleep(0.5)
    
    await websocket.send_json({
        "type": "routing",
        "model": "Local Brain (Pattern Matcher)",
        "reason": "Task matches known patterns"
    })
    await asyncio.sleep(0.3)
    
    # 2. Update todos
    todos = [
        "Searching Knowledge Base",
        "Generating Template",
        "Writing Logic",
        "Linting & AutoFix",
        "Committing to Git"
    ]
    await websocket.send_json({
        "type": "todos_update",
        "todos": todos
    })
    await asyncio.sleep(0.3)
    
    # 3. Stream progress
    for i, todo in enumerate(todos):
        await websocket.send_json({
            "type": "todo_advance",
            "index": i,
            "todo": todo
        })
        await asyncio.sleep(0.8)
        
        if i == 1:
            # Generate code guidance
            guidance = generate_code_guidance("python api file")
            await websocket.send_json({
                "type": "stream_output",
                "content": guidance,
                "label": "Code Guidance"
            })
        elif i == 3:
            # AutoFix example
            await websocket.send_json({
                "type": "autofix",
                "issue": "Missing import 'FastAPI'",
                "fix": "Added 'from fastapi import FastAPI'"
            })
    
    # 4. Update dashboard
    await websocket.send_json({
        "type": "dashboard",
        "plan": session.get("task", ""),
        "progress": "Completed successfully!",
        "confidence": 0.95,
        "hit_keywords": ["python", "api", "fastapi"]
    })
    
    await websocket.send_json({
        "type": "complete",
        "message": "Task completed successfully!"
    })

async def stream_message(websocket: WebSocket, text: str, style: str = "INFO"):
    """Send a streaming message"""
    await websocket.send_json({
        "type": "message",
        "text": text,
        "style": style
    })

if __name__ == "__main__":
    import uvicorn
    print("Starting NFM-SV Web Interface on http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
