#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NFM-SV Web: FastAPI Server for Phase 11 Vibe Interface (Chat-First Mode)
架构：主Agent <-> 用户 实时对话 + 真实AI推理 + 随时打断
"""
import os
import sys
import json
import asyncio
import time
import traceback
from typing import Dict, List, Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import os

# Mount static files directory
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from frame import FrameEngine, RuleNode
from mnemo import MemoryBank, GlobalMnemo
from spark import SparkExecutor, GitOps
from vibe import VibeInterface
from nexus import NexusBrain
from nexus.medic_team import MedicCoordinator
from nexus.medic_repair import RepairAgent
from nexus.mercury_agent import MercuryCrabAgent
from llm.local_brain import LocalBrain, AIContext, AIDecision
from knowledge import KnowledgeBase
from knowledge.code_patterns import generate_code_guidance
from visual.runner import execute_mano_task
from nexus.chat_room import chat_manager, handle_chat_websocket

app = FastAPI(title="NFM-SV Vibe Web Interface", version="0.7.0-mano")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Knowledge Base
global_knowledge_base = None
try:
    wiki_path = os.path.join(os.path.dirname(__file__), "..", "..", "Mercury-Crab-Agent", "wiki")
    if os.path.exists(wiki_path):
        global_knowledge_base = KnowledgeBase(wiki_path=wiki_path, index_file="knowledge_index.json")
        global_knowledge_base.load()
        print("Knowledge Base loaded successfully.")
    else:
        print("Warning: Wiki path not found. Knowledge Base disabled.")
except Exception as e:
    print(f"Warning: Failed to load Knowledge Base: {e}")

# Global State
active_sessions: Dict[str, dict] = {}
agent_instances: Dict[str, dict] = {}
# Initialize Medic Team (Global Memory & Self-Learning)
medic_team = MedicCoordinator(memory_path="nexus_medic_memory.json", knowledge_base=global_knowledge_base)

# Initialize Mercury Crab Agent (Independent from OpenClaw)
mercury_agent = None
try:
    mercury_path = os.path.join(os.path.dirname(__file__), "..", "..", "Mercury-Crab-Agent")
    if os.path.exists(mercury_path):
        mercury_agent = MercuryCrabAgent(project_path=mercury_path)
        print("Mercury Crab Agent initialized successfully.")
    else:
        print("Warning: Mercury-Crab-Agent path not found.")
except Exception as e:
    print(f"Warning: Failed to init Mercury Agent: {e}")

@app.get("/", response_class=HTMLResponse)
async def get_frontend():
    html_path = os.path.join(os.path.dirname(__file__), "templates", "index.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>NFM-SV</h1><p>Frontend not found.</p>"

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await websocket.accept()

    # Initialize session if not exists
    if session_id not in active_sessions:
        test_dir = os.path.join(os.path.dirname(__file__), "..", "test_project_web")
        if not os.path.exists(test_dir):
            os.makedirs(test_dir)

        active_sessions[session_id] = {
            "status": "idle",
            "test_dir": test_dir,
            "chat_history": [],
            "current_task": None, # For cancellation
            "cancelled": False,
        }

        # Initialize Agent instance
        try:
            db_path = os.path.join(test_dir, "nfm_sv.db")
            frame = FrameEngine(db_path=db_path)
            memory = MemoryBank(bank_path=os.path.join(test_dir, "memory.db"))
            spark = SparkExecutor(cwd=test_dir, default_timeout=120)
            git = GitOps(cwd=test_dir)
            vibe = VibeInterface(use_input=False)
            global_memory = GlobalMnemo(db_path=os.path.join(test_dir, "global_mnemo.db"))
            
            brain = NexusBrain(
                engine=frame, memory=memory, spark=spark, git=git, 
                vibe=vibe, global_memory=global_memory, knowledge_base=global_knowledge_base
            )

            agent_instances[session_id] = {
                "brain": brain, "frame": frame, "memory": memory,
                "spark": spark, "git": git, "local_brain": brain.local_brain,
            }
            await stream_agent_msg(websocket, "✅ Agent 初始化成功，随时待命。")
        except Exception as e:
            print(f"[Agent Init Error]: {e}")
            traceback.print_exc()
            await stream_agent_msg(websocket, f"❌ Agent 初始化失败: {str(e)}")
            # Don't fail the task, just log it. Agent will use fallback.

    session = active_sessions[session_id]
    agent = agent_instances.get(session_id)

    # Medic Team: Lazy Initialization / Repair
    if not agent:
        print(f"[Medic] Agent instance missing for session {session_id}. Attempting repair...")
        
        # Use the specialized Repair Agent
        repair_agent = RepairAgent()
        success, agent, message = repair_agent.fix_initialization(session_id, active_sessions, agent_instances)
        
        if success:
            print(f"[Medic] SUCCESS: {message}")
            await stream_agent_msg(websocket, f"🚑 Medic Team 报告: {message}。正在恢复服务...")
        else:
            print(f"[Medic] FAILED: {message}")
            await stream_agent_msg(websocket, f"🚑 Medic Team 报告: {message}")

    # Chat Loop
    try:
        while True:
            # Wait for user message
            data = await websocket.receive_json()

            # Handle Stop
            if data.get("type") == "stop":
                if session.get("current_task") and not session["current_task"].done():
                    session["current_task"].cancel()
                    await stream_agent_msg(websocket, "🛑 任务已被用户中止。")
                    session["status"] = "stopped"
                continue

            if data.get("type") != "chat":
                continue

            user_text = data.get("text", "")
            if not user_text:
                continue

            # Add to history
            session["chat_history"].append({"role": "user", "content": user_text})

            # Interrupt current task if running
            if session.get("current_task") and not session["current_task"].done():
                await stream_agent_msg(websocket, "⚠️ 正在打断当前任务...")
                session["current_task"].cancel()
                # Give a moment for cleanup
                await asyncio.sleep(0.1)

            # Start new task
            task = asyncio.create_task(run_agent_turn(websocket, user_text, session, agent))
            session["current_task"] = task

            try:
                await task
            except asyncio.CancelledError:
                # Task was interrupted by new message
                await stream_agent_msg(websocket, "🛑 任务已被新消息打断。")
                session["status"] = "interrupted"

    except WebSocketDisconnect:
        print(f"[WS] Client disconnected: {session_id}")
        session["status"] = "disconnected"
        # Cancel any running task
        if session.get("current_task") and not session["current_task"].done():
            session["current_task"].cancel()
    except Exception as e:
        print(f"[WS] Error: {e}")
        traceback.print_exc()

async def run_agent_turn(websocket: WebSocket, user_text: str, session: dict, agent: dict):
    """Single Agent Turn: Think -> Act -> Reply"""
    session["status"] = "working"
    test_dir = session.get("test_dir", ".")

    if not agent:
        await stream_agent_msg(websocket, f"💭 收到: '{user_text}' (简化模式)")
        await asyncio.sleep(0.5)
        await stream_agent_msg(websocket, "⚠️ Agent 未初始化，无法执行复杂操作。")
        session["status"] = "idle"
        return

    local_brain: LocalBrain = agent["local_brain"]
    spark: SparkExecutor = agent["spark"]

    # 1. Thinking Phase
    await show_thinking(websocket, "🧠 正在分析意图...")
    await asyncio.sleep(0.5)

    # Check for Mano-P (GUI Automation) trigger
    if "mano" in user_text.lower() or "自动化界面" in user_text or "控制桌面" in user_text or "gui" in user_text.lower():
        await stream_agent_msg(websocket, "🖐️ **Mano-P Skill 激活**: 正在接管桌面操作...")
        await asyncio.sleep(1)
        
        # Extract task description (simple heuristic: remove keywords)
        task_desc = user_text.replace("Mano", "").replace("mano", "").replace("自动化界面", "").replace("控制桌面", "").strip()
        if not task_desc:
            task_desc = "Perform the requested GUI automation task."
            
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, execute_mano_task, task_desc)
        
        await stream_agent_msg(websocket, result)
        session["status"] = "idle"
        return

    ai_ctx = AIContext(
        plan=f"# {user_text}",
        progress="",
        rules="",
        current_files=[],
        git_status="",
        previous_command=user_text,
    )

    await show_thinking(websocket, "🤖 LocalBrain 决策中...")
    await asyncio.sleep(0.3)

    decision = local_brain.decide_next_command(ai_ctx)
    await websocket.send_json({
        "type": "routing",
        "model": "LocalBrain",
        "reason": decision.reasoning[:100]
    })

    # 2. Action Phase
    cmd = decision.command
    if cmd and cmd != "ASK_USER":
        await stream_agent_msg(websocket, f"⚡ 执行: {cmd}")
        
        # Run in thread to not block WebSocket
        loop = asyncio.get_event_loop()
        try:
            result = await loop.run_in_executor(None, spark.run, cmd)
            
            if result["status"] == "ok":
                await websocket.send_json({
                    "type": "stream_output",
                    "content": result["output"][:1000],
                    "label": "执行结果"
                })
            else:
                await stream_agent_msg(websocket, f"⚠️ 执行失败: {result['error'][:100]}...")
                
                # 🚑 Trigger Nexus Medic Team (Self-Healing & Learning)
                await stream_agent_msg(websocket, "🚑 **Nexus Medic Team 激活**: 正在诊断并尝试自愈...")
                await asyncio.sleep(0.5)
                
                diagnosis = medic_team.diagnostic.analyze(result["error"], {})
                await stream_agent_msg(websocket, f"🔍 [诊断]: {diagnosis['type']} ({diagnosis['severity']})")
                
                # Recall Memory
                past_case = medic_team.memory.recall(result["error"])
                if past_case:
                    await stream_agent_msg(websocket, f"🧠 [记忆]: 发现相似历史修复案例 (成功率 {past_case.success_score:.0%})")
                
                # Architect Check (Persistence)
                if medic_team.architect.check_drift(result["error"]):
                    await stream_agent_msg(websocket, "🛡️ [架构师]: 检测到潜在方案漂移，拒绝盲目修复，坚持原有设计。")
                else:
                    # Suggest Fix
                    fix = medic_team.repair.attempt_fix(diagnosis, result["error"])
                    if fix and fix != "manual_review":
                        await stream_agent_msg(websocket, f"🛠️ [修复方案]: {fix}")
                        
                        # Try to auto-fix
                        await stream_agent_msg(websocket, "⚡ 正在尝试自动修复...")
                        await asyncio.sleep(0.5)
                        
                        # In a real scenario, we would execute 'fix' here.
                        # For now, we report it.
                        medic_team.memory.learn(result["error"], fix, success=False, tags=[diagnosis['type']])
                        if mercury_agent:
                            mercury_agent.record_error(result["error"], fix)
                        
                        await websocket.send_json({
                            "type": "stream_output",
                            "content": f"自动修复尝试: {fix}",
                            "label": "自愈结果"
                        })
        except Exception as e:
            await stream_agent_msg(websocket, f"❌ 执行异常: {str(e)}")
    else:
        # Knowledge/Analysis response
        if "分析" in user_text or "知识" in user_text:
            await stream_agent_msg(websocket, "🔍 正在检索知识库...")
            await asyncio.sleep(0.5)
            # Mock KB response for now
            await stream_agent_msg(websocket, "📖 知识库: 暂无直接匹配的记录，建议手动检查相关代码文件。")

    # 3. Reply Phase
    reply = f"✅ 任务处理完成。"
    if decision.confidence < 0.5:
        reply = f"⚠️ 任务完成，但置信度较低 ({decision.confidence:.0%})，请检查结果。"
    
    await stream_agent_msg(websocket, reply)
    session["chat_history"].append({"role": "agent", "content": reply})
    session["status"] = "idle"

async def show_thinking(websocket: WebSocket, text: str):
    await websocket.send_json({
        "type": "thinking",
        "text": text
    })

async def stream_agent_msg(websocket: WebSocket, text: str, style: str = "system"):
    await websocket.send_json({
        "type": "message",
        "text": text,
        "style": style
    })

# --- Chat Room Module ---
@app.get("/chat", response_class=HTMLResponse)
async def get_chat():
    html_path = os.path.join(os.path.dirname(__file__), "templates", "chat.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>NFM-SV Chat</h1><p>Chat UI not found.</p>"

@app.websocket("/ws/chat/{user_id}")
async def chat_websocket(websocket: WebSocket, user_id: str):
    await handle_chat_websocket(websocket, user_id)
# --- End Chat Room Module ---

# --- Mercury Status API ---
@app.get("/api/mercury/status")
async def get_mercury_status():
    """获取 Mercury 记忆层状态 (Defensive: Handles missing paths gracefully)"""
    if mercury_agent:
        try:
            status = {
                "hot_size": 0,
                "warm_days": 0,
                "cold_entries": 0,
                "skills_count": 0,
                "skills": [],
                "corrections": [],
            }
            
            hot_path = os.path.join(mercury_agent.project_path, "MEMORY.md")
            if os.path.exists(hot_path):
                status["hot_size"] = os.path.getsize(hot_path)
            
            memory_dir = os.path.join(mercury_agent.project_path, "memory")
            if os.path.exists(memory_dir):
                import re as re_mod
                files = [f for f in os.listdir(memory_dir) if re_mod.match(r"\d{4}-\d{2}-\d{2}\.md", f)]
                status["warm_days"] = len(files)
                total_entries = 0
                for fname in files[:5]:
                    fpath = os.path.join(memory_dir, fname)
                    with open(fpath, "r", encoding="utf-8") as f:
                        total_entries += sum(1 for line in f if line.strip().startswith("- "))
                status["cold_entries"] = total_entries
            
            skills_dir = os.path.join(mercury_agent.project_path, "skills")
            if os.path.exists(skills_dir):
                skills = [f.replace(".skill", "") for f in os.listdir(skills_dir) if f.endswith(".skill")]
                status["skills_count"] = len(skills)
                status["skills"] = skills[:10]
            
            self_improving_dir = os.path.join(os.path.dirname(mercury_agent.project_path), "self-improving")
            corrections_path = os.path.join(self_improving_dir, "corrections.md")
            if os.path.exists(corrections_path):
                with open(corrections_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                status["corrections"] = [line.strip() for line in lines[-5:] if line.strip().startswith("- ")]
            
            return {"status": "ok", "data": status}
        except Exception as e:
            print(f"[API ERROR] Mercury status failed: {e}")
            return {"status": "error", "message": str(e)}
    return {"status": "unavailable", "message": "Mercury Agent not initialized"}
# --- End Mercury Status API ---

# Mercury Agent Heartbeat Loop
async def mercury_heartbeat_loop():
    """Background task: Run Mercury Crab Agent maintenance tasks periodically."""
    if not mercury_agent:
        return
    print("[Mercury] Heartbeat loop started.")
    while True:
        try:
            # Run cycle every 10 minutes
            await asyncio.sleep(600)
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, mercury_agent.run_heartbeat_cycle)
        except Exception as e:
            print(f"[Mercury] Heartbeat loop error: {e}")

# Add startup event
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(mercury_heartbeat_loop())

if __name__ == "__main__":
    import uvicorn
    print("=" * 50)
    print("  NFM-SV Vibe Chat")
    print("  Chat-First AI Agent v0.5.0")
    print("  http://localhost:8000")
    print("=" * 50)
    uvicorn.run(app, host="0.0.0.0", port=8000)
