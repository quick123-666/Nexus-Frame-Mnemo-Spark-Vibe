#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mano-P Skill Wrapper for NFM-SV
Allows the Agent to use Mano-P for GUI automation.
"""
import os
import sys

# Ensure the project root is in the path so 'visual' package is found
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from visual.vla import run_task

def execute_mano_task(task_description: str, url: str = None, app: str = None) -> str:
    """
    Execute a GUI automation task using Mano-P (Cloud Mode).
    """
    print(f"[Mano-P] Starting task: {task_description}")
    try:
        # run_task returns 0 on success, 1 on failure
        # We run it synchronously. It will take over mouse/keyboard.
        result = run_task(task_description, url=url, app=app, minimize=True, max_steps=100)
        if result == 0:
            return "Task completed successfully."
        else:
            return "Task failed or was stopped."
    except Exception as e:
        return f"Mano-P execution error: {str(e)}"

if __name__ == "__main__":
    # Test run
    task = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Open Notepad and type 'Hello from Mano-P!'"
    print(execute_mano_task(task))
