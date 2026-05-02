#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Medic Team Repair Agent: Specialized in fixing Agent Initialization failures
"""
import os
import sys
import traceback
import asyncio

class RepairAgent:
    def __init__(self):
        self.name = "Repair Agent"

    def fix_initialization(self, session_id: str, active_sessions: dict, agent_instances: dict):
        """
        Attempt to repair/initialize a missing Agent instance.
        Returns: (success: bool, agent: dict or None, message: str)
        """
        session = active_sessions.get(session_id)
        if not session:
            return False, None, "Session not found"

        test_dir = session.get("test_dir")
        
        # 1. Ensure Directory exists
        if not test_dir or not os.path.exists(test_dir):
            test_dir = os.path.join(os.path.dirname(__file__), "..", "test_project_web")
            session["test_dir"] = test_dir
            try:
                os.makedirs(test_dir, exist_ok=True)
            except Exception as e:
                return False, None, f"Failed to create directory: {e}"

        # 2. Attempt Component Initialization
        try:
            # Ensure sys.path is correct
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
            if project_root not in sys.path:
                sys.path.insert(0, project_root)

            from frame import FrameEngine
            from mnemo import MemoryBank, GlobalMnemo
            from spark import SparkExecutor, GitOps
            from vibe import VibeInterface
            from nexus import NexusBrain

            # Init Components
            frame = FrameEngine(db_path=os.path.join(test_dir, "nfm_sv.db"))
            memory = MemoryBank(bank_path=os.path.join(test_dir, "memory.db"))
            spark = SparkExecutor(cwd=test_dir, default_timeout=120)
            git = GitOps(cwd=test_dir)
            vibe = VibeInterface(use_input=False)
            global_memory = GlobalMnemo(db_path=os.path.join(test_dir, "global_mnemo.db"))
            
            # Init Brain
            brain = NexusBrain(
                engine=frame, memory=memory, spark=spark, git=git, 
                vibe=vibe, global_memory=global_memory, knowledge_base=None
            )

            # Create Agent Instance
            agent = {
                "brain": brain, "frame": frame, "memory": memory,
                "spark": spark, "git": git, "local_brain": brain.local_brain,
            }

            # Store in Global State
            agent_instances[session_id] = agent
            return True, agent, "Agent 修复成功！"

        except Exception as e:
            error_trace = traceback.format_exc()
            print(f"[Repair Agent] Init failed: {e}")
            print(error_trace)
            return False, None, f"修复失败: {str(e)}"
