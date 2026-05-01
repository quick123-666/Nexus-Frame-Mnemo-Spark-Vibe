#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Nexus-Frame-Mnemo-Spark-Vibe: Main Entry Point (Phase 6 - Local AI)
"""
import os
import sys
import shutil

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from frame import FrameEngine, RuleNode
from mnemo import MemoryBank, GlobalMnemo
from spark import SparkExecutor, GitOps
from vibe import VibeInterface
from nexus import NexusBrain

def main():
    print("🚀 Nexus-Frame-Mnemo-Spark-Vibe: Phase 6 (Local AI) Test")
    
    # Setup isolated test directory
    test_dir = os.path.join(os.path.dirname(__file__), "test_project")
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir, ignore_errors=True)
    os.makedirs(test_dir)

    # 1. Initialize Subsystems
    print("🛠️ Initializing System...")
    
    # Global Mnemo DB path
    global_db = os.path.join(os.path.dirname(__file__), "global_mnemo.db")
    if os.path.exists(global_db):
        try:
            os.remove(global_db)
        except:
            pass
        
    global_memory = GlobalMnemo(global_db)

    frame = FrameEngine(os.path.join(test_dir, "rules.db"))
    frame.add_rule(RuleNode(id="base", category="general", content="Be precise.", weight=10, triggers=["general"]))
    frame.add_rule(RuleNode(id="git_rule", category="git", content="Commit after every change.", weight=100, triggers=["git"]))
    
    mnemo = MemoryBank(os.path.join(test_dir, "memory-bank"))
    mnemo.write("plan.md", "# Implementation Plan\n\n## Steps\n1. 创建测试文件\n2. 运行测试\n")
    mnemo.write("progress.md", "# Progress\n\n## Completed\n- \n")

    spark = SparkExecutor(cwd=test_dir)
    git = GitOps(cwd=test_dir)
    git.init()

    # Use Mock Mode for automated testing
    vibe = VibeInterface(use_input=False) 
    
    nexus = NexusBrain(frame, mnemo, spark, git, vibe, global_memory)

    # 2. Test Scenario 1: AI suggests command -> Execute
    print("\n📥 Scenario 1: AI Suggestion -> Execute")
    res1 = nexus.execute_with_human_loop("创建测试", ["general", "git"])
    print(f"-> Outcome: {res1['status']}")

    # 3. Test Scenario 2: Error -> Global Memory saves fix
    print("\n📥 Scenario 2: Error -> Fix -> Save to Global")
    res2 = nexus.execute_with_human_loop("invalid_command", ["general"])
    print(f"-> Outcome: {res2['status']}")

    # Cleanup
    shutil.rmtree(test_dir, ignore_errors=True)
    # 清理全局数据库 (延迟删除避免占用)
    print("\n✅ Phase 6 Test Complete.")

if __name__ == "__main__":
    main()
