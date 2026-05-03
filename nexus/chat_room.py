#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NFM-SV Chat Room Module (Multi-Layer Memory Integrated)
集成 Mnemo 经验记忆 和 Knowledge 知识库 的实时聊天室。
"""
import asyncio
import json
import time
import os
import sys
import sqlite3
import yaml
import httpx
from typing import Dict, List
from fastapi import WebSocket, WebSocketDisconnect

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections[user_id] = websocket
        print(f"[Chat] {user_id} joined.")

    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
            print(f"[Chat] {user_id} disconnected.")

    async def broadcast(self, message: str):
        for connection in self.active_connections.values():
            await connection.send_text(message)

chat_manager = ConnectionManager()

# --- 1. Persistent Chat History (Local Storage) ---
DB_PATH = os.path.join(os.path.dirname(__file__), "chat_history.db")

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL,
                user_id TEXT,
                role TEXT,
                content TEXT
            )
        """)
        conn.commit()

def save_message(user_id: str, role: str, content: str):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute(
                "INSERT INTO messages (timestamp, user_id, role, content) VALUES (?, ?, ?, ?)",
                (time.time(), user_id, role, content)
            )
    except Exception as e:
        print(f"[Chat DB] Error: {e}")

init_db()

# --- 2. Load Configuration & AI Setup ---
try:
    config_path = os.path.join(os.path.dirname(__file__), "..", "config.yaml")
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    LLM_CONFIG = config.get("llm", {})
    API_URL = f"{LLM_CONFIG.get('base_url', '')}/chat/completions"
    API_KEY = LLM_CONFIG.get('api_key', '')
    MODEL = LLM_CONFIG.get('model', 'MiniMax-M2.5')
    AI_ENABLED = bool(API_KEY and API_URL)
except Exception as e:
    print(f"[Chat] Failed to load config: {e}")
    AI_ENABLED = False

# --- 3. Memory Integration Logic (Real Mnemo Integration) ---
# 引入 NFM-SV 的核心记忆模块
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from mnemo.global_exp import GlobalMnemo

# 初始化全局记忆库
mnemo_db_path = os.path.join(os.path.dirname(__file__), "..", "test_project_web", "global_mnemo.db")
global_mnemo = GlobalMnemo(mnemo_db_path)

def get_mnemo_context(query: str) -> str:
    """
    调用 Mnemo 检索历史经验。
    这是 NFM-SV "多层记忆" 架构的关键体现：基于案例的推理 (Case-Based Reasoning)。
    """
    try:
        # 检索相似错误和解决方案
        solutions = global_mnemo.search_solutions(query)
        if solutions:
            context = "\n\n[🧠 Mnemo Memory Recall]:\n"
            for sol in solutions[:2]: # 只取最相关的两个经验
                context += f"- 历史案例 (相似度: {sol['match_score']}): 曾遇到 '{sol['pattern']}', 解决方案: '{sol['solution']}'\n"
            return context
        return ""
    except Exception as e:
        return f"\n[Mnemo Error: {str(e)}]"

SYSTEM_PROMPT = """
你是 **NFM-SV** (Nexus-Frame-Mnemo-Spark-Vibe)，一个运行在用户本地的高级自主 AI Agent 框架。

【你的多层记忆架构】：
1. **Mnemo (经验记忆)**：你拥有跨项目经验，能从历史错误中学习。
2. **Mercury (长期记忆)**：你维护着项目的长期演进日志。
3. **Knowledge (知识库)**：你拥有本地 PBL 和 Awesome 资源索引。

【你的当前状态】：
你正在通过 **Nexus Chat** 模块与用户对话。在回答问题时，请优先检索你的**记忆库**（Mnemo），如果发现以前解决过类似问题，请直接引用过去的解决方案。

【态度】：
你是资深的技术合伙人，自信、高效。强调你拥有完整的记忆上下文。
"""

async def get_ai_response(user_prompt: str) -> str:
    """AI 回复：结合记忆库 + 知识库"""
    if not AI_ENABLED:
        return "⚠️ AI 模块未配置。"
    
    # 1. 获取记忆上下文 (Mnemo Experience)
    memory_context = get_mnemo_context(user_prompt)
    
    # 2. 构建完整 Prompt
    full_prompt = f"{user_prompt}\n\n{memory_context}" if memory_context else user_prompt

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": full_prompt}
        ],
        "max_tokens": 1024
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            res = await client.post(API_URL, json=payload, headers=headers)
            if res.status_code == 200:
                data = res.json()
                return data.get("choices", [{}])[0].get("message", {}).get("content", "无回复")
            else:
                return f"❌ API 错误 ({res.status_code})"
    except Exception as e:
        return f"❌ 请求失败: {str(e)}"

async def handle_chat_websocket(websocket: WebSocket, user_id: str):
    await chat_manager.connect(websocket, user_id)
    
    welcome_msg = f"👋 {user_id} 加入了聊天室"
    await chat_manager.broadcast(json.dumps({
        "type": "system", "user": "System", "message": welcome_msg, "timestamp": time.time()
    }))
    save_message("System", "system", welcome_msg)
    
    try:
        while True:
            data = await websocket.receive_text()
            msg_data = json.loads(data)
            msg_text = msg_data.get('message', '')
            save_message(user_id, "user", msg_text)
            
            if msg_text.startswith('/ai') or msg_text.startswith('/nfm') or msg_text.startswith('@bot'):
                prompt = msg_text.split(' ', 1)[1] if ' ' in msg_text else msg_text
                
                # AI 正在思考
                await chat_manager.broadcast(json.dumps({
                    "type": "system", "user": "NFM-SV Bot", 
                    "message": f"🧠 正在检索记忆库并思考: {prompt}...", "timestamp": time.time()
                }))

                ai_reply = await get_ai_response(prompt)
                
                await chat_manager.broadcast(json.dumps({
                    "type": "bot", "user": "NFM-SV Bot", "message": ai_reply, "timestamp": time.time()
                }))
                save_message("NFM-SV Bot", "bot", ai_reply)
            else:
                await chat_manager.broadcast(json.dumps({
                    "type": "message", "user": user_id, "message": msg_text, "timestamp": time.time()
                }))
                
    except WebSocketDisconnect:
        chat_manager.disconnect(user_id)
        leave_msg = f"👋 {user_id} 离开了"
        await chat_manager.broadcast(json.dumps({
            "type": "system", "user": "System", "message": leave_msg, "timestamp": time.time()
        }))
        save_message("System", "system", leave_msg)
