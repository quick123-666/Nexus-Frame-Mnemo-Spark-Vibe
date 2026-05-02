#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug Script: 使用 Medic Team 诊断 Agent 初始化失败
"""
import os
import sys
import codecs
import traceback

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.buffer, 'strict')

# Add project root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from nexus.medic_team import MedicCoordinator, DiagnosticAgent, RepairAgent

# 配置路径
PROJECT_ROOT = os.path.join(os.path.dirname(__file__), "..")
TEST_DIR = os.path.join(PROJECT_ROOT, "test_project_web")

def diagnose_init():
    medic = MedicCoordinator(memory_path=os.path.join(PROJECT_ROOT, "nexus_medic_memory.json"))
    diagnostic = DiagnosticAgent()
    
    print(f"{'='*50}")
    print("  🔍 [Diagnostic] 开始深度诊断...")
    print(f"{'='*50}")
    
    # 确保测试目录存在
    if not os.path.exists(TEST_DIR):
        os.makedirs(TEST_DIR)
        print(f"[Pre-check] 创建测试目录: {TEST_DIR}")

    print("\n🧪 正在尝试初始化 Agent (模拟 Server 环境)...")
    try:
        from frame import FrameEngine
        from mnemo import MemoryBank, GlobalMnemo
        from spark import SparkExecutor, GitOps
        from vibe import VibeInterface
        from nexus import NexusBrain
        
        db_path = os.path.join(TEST_DIR, "nfm_sv.db")
        print(f"  1. 初始化 FrameEngine (DB: {db_path})...")
        frame = FrameEngine(db_path=db_path)
        
        print(f"  2. 初始化 MemoryBank...")
        memory = MemoryBank(bank_path=os.path.join(TEST_DIR, "memory.db"))
        
        print(f"  3. 初始化 SparkExecutor...")
        spark = SparkExecutor(cwd=TEST_DIR, default_timeout=120)
        
        print(f"  4. 初始化 GitOps...")
        git = GitOps(cwd=TEST_DIR)
        
        print(f"  5. 初始化 VibeInterface...")
        vibe = VibeInterface(use_input=False)
        
        print(f"  6. 初始化 GlobalMnemo...")
        global_memory = GlobalMnemo(db_path=os.path.join(TEST_DIR, "global_mnemo.db"))
        
        print(f"  7. 初始化 NexusBrain...")
        brain = NexusBrain(
            engine=frame, memory=memory, spark=spark, git=git, 
            vibe=vibe, global_memory=global_memory, knowledge_base=None
        )
        
        print("\n✅ [Result] 初始化成功! 未发现阻塞性错误。")
        print("   💡 提示: 如果网页仍报错，可能是 WebSocket Session ID 不匹配。")
        
    except Exception as e:
        print(f"\n❌ [Result] 初始化失败!")
        print(f"   错误类型: {type(e).__name__}")
        print(f"   错误信息: {e}")
        print("\n🔍 [Diagnostic] 堆栈追踪:")
        traceback.print_exc()
        
        # 记录错误到 Medic Team
        medic.memory.learn(str(e), "Check imports and paths", False, ["init_fail"])

if __name__ == "__main__":
    diagnose_init()
