#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NFM-SV Vibe: Human-in-the-Loop (HITL) Interface
Provides TUI for approval, planning review, and error recovery.
"""
import sys

class VibeInterface:
    def __init__(self, use_input: bool = True):
        self.use_input = use_input

    def print_separator(self):
        print("\n" + "=" * 60 + "\n")

    def render_dashboard(self, plan: str, progress: str):
        """Display the current project status."""
        self.print_separator()
        print("🎨 VIBE DASHBOARD")
        print("-" * 30)
        print("📋 CURRENT PLAN:")
        print(plan[:300] + "..." if len(plan) > 300 else plan)
        print("-" * 30)
        print("🚀 PROGRESS:")
        print(progress[:300] + "..." if len(progress) > 300 else progress)
        self.print_separator()

    def request_approval(self, message: str) -> str:
        """Ask user for approval (y/n) or a specific command."""
        print(f"👤 {message}")
        if not self.use_input:
            print(f"   [Mock Response]: y")
            return "y"
        
        try:
            return input("   > ").strip()
        except EOFError:
            return "y"

    def request_fix(self, error_msg: str) -> str:
        """Ask user to provide a fix for the error."""
        self.print_separator()
        print("❌ EXECUTION FAILED")
        print(f"Error: {error_msg}")
        print("🔧 How should we fix this? (Enter shell command or 'abort')")
        
        if not self.use_input:
            print(f"   [Mock Response]: echo 'Manual Fix'")
            return "echo 'Manual Fix'"

        try:
            return input("   > ").strip()
        except EOFError:
            return "abort"

    def request_input(self, message: str) -> str:
        """Request arbitrary input from user."""
        print(f"👤 {message}")
        
        if not self.use_input:
            print(f"   [Mock Response]: echo 'User Input'")
            return "echo 'User Input'"
        
        try:
            return input("   > ").strip()
        except EOFError:
            return "abort"
