#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Nexus-Frame-Mnemo-Spark-Vibe: Phase 10 Vibe Interface Prototype
Demonstrates:
- Real-time Todo Progress (Open Design style)
- Knowledge-driven Dashboard (Confidence & Hits)
- Smart Routing & AutoFix indicators (Lovable/v0.dev style)
"""
import os
import sys
import shutil
import io

# Fix Windows console encoding
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from frame import FrameEngine, RuleNode
from mnemo import MemoryBank, GlobalMnemo
from spark import SparkExecutor, GitOps
from vibe import VibeInterface
from nexus import NexusBrain
from knowledge import KnowledgeBase
from knowledge.code_patterns import generate_code_guidance

def main():
    print("🚀 Nexus-Frame-Mnemo-Spark-Vibe: Phase 10 (Vibe Interface) Test")
    
    test_dir = os.path.join(os.path.dirname(__file__), "test_project_phase10")
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir, ignore_errors=True)
    os.makedirs(test_dir)

    # Initialize Knowledge Base
    kb = KnowledgeBase(wiki_path=os.path.join(os.path.dirname(__file__), "wiki"))
    kb.load()

    print("🛠️ Initializing Subsystems...")
    
    global_db = os.path.join(os.path.dirname(__file__), "global_mnemo_phase10.db")
    if os.path.exists(global_db):
        try: os.remove(global_db)
        except: pass
    
    global_memory = GlobalMnemo(global_db)
    frame = FrameEngine(os.path.join(test_dir, "rules.db"))
    frame.add_rule(RuleNode(id="base", category="general", content="Be precise and concise.", weight=10, triggers=["general"]))
    
    mnemo = MemoryBank(os.path.join(test_dir, "memory-bank"))
    mnemo.write("plan.md", "# Implementation Plan\n1. Analyze Request\n2. Search Knowledge\n3. Generate Code\n4. Verify Output")
    mnemo.write("progress.md", "# Progress\n- Ready")

    spark = SparkExecutor(cwd=test_dir)
    git = GitOps(cwd=test_dir)
    git.init()

    vibe = VibeInterface(use_input=False) 

    nexus = NexusBrain(frame, mnemo, spark, git, vibe, global_memory, kb)

    # Phase 10 Scenario: Complex Task with Vibe Dashboard
    print("\n📥 Scenario: Complex Task (Phase 10 Vibe Test)")
    task = "Create a FastAPI server with a health check endpoint"
    
    # 1. Analyze & Search via LocalBrain
    vibe._print_rich("Analyzing task...", "THINKING")
    vibe.show_routing("Local Brain (Pattern Matcher)", "Task matches known patterns")
    
    ai_ctx = nexus._build_ai_context(["general"], prev_cmd=task)
    decision = nexus.local_brain.decide_next_command(ai_ctx)
    
    print(f"🧠 [Decision] {decision.reasoning}")
    print(f"   Confidence: {decision.confidence:.0%}")
    print(f"   Knowledge Used: {'Yes' if decision.knowledge_used else 'No'}")

    if decision.confidence > 0.5:
        vibe.render_dashboard(
            plan=mnemo.read("plan.md"),
            progress="Starting Code Generation...",
            confidence=decision.confidence,
            hit_keywords=["fastapi", "python", "api"] if decision.knowledge_used else []
        )
        
        # 2. Todo Progress
        vibe.update_todos([
            "Searching Knowledge Base",
            "Generating FastAPI Template",
            "Writing Health Check Logic",
            "Linting & AutoFix",
            "Committing to Git"
        ])
        
        # 3. Execute & Stream
        vibe.advance_todo() # Searching
        vibe.advance_todo() # Generating
        
        # Use Wiki patterns to generate guidance
        guidance = generate_code_guidance("python api file")
        vibe.stream_output(guidance, "FastAPI Server Guidance")
        
        vibe.advance_todo() # Writing
        vibe.advance_todo() # Linting & AutoFix
        vibe.show_autofix("Missing import 'FastAPI'", "Added 'from fastapi import FastAPI'")
        
        vibe.advance_todo() # Committing
        git.add_all()
        git.commit("feat: add fastapi server with health check (Phase 10)")
        
        vibe._print_rich("Task completed successfully!", "SUCCESS")
    else:
        vibe._print_rich(f"Low confidence ({decision.confidence:.0%}). Falling back to standard mode.", "ERROR")
        nexus.execute_with_human_loop(task, ["general"])

    shutil.rmtree(test_dir, ignore_errors=True)
    try: os.remove(global_db)
    except: pass
    print("\n✅ Phase 10 Vibe Interface Test Complete.")

if __name__ == "__main__":
    main()
