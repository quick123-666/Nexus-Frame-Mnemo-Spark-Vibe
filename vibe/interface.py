#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NFM-SV Vibe: Phase 10 Interactive Interface (Human-in-the-Loop)
Features:
- Real-time Todo Progress (参考 Open Design)
- Streaming Output with Typing Effect (参考 v0.dev)
- Interactive Dashboard with Confidence Metrics
- Smart Routing Indicators (参考 Lovable)
"""
import sys
import time
import json
from typing import List, Optional

class VibeInterface:
    def __init__(self, use_input: bool = True):
        self.use_input = use_input
        self.todo_list = []
        self.current_todo = -1
        
        # Check if rich is available
        try:
            from rich.console import Console
            from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
            from rich.table import Table
            from rich.panel import Panel
            from rich.markdown import Markdown
            from rich.live import Live
            self.has_rich = True
            self.console = Console()
        except ImportError:
            self.has_rich = False

    def _print_basic(self, text: str, style: str = "INFO"):
        prefix = {"INFO": "ℹ️", "SUCCESS": "✅", "ERROR": "❌", "PLAN": "📋", "GENERATING": "🤖", "THINKING": "🧠"}.get(style, "🔹")
        print(f"{prefix} {text}")

    def _print_rich(self, text: str, style: str = "INFO"):
        if self.has_rich:
            if style == "PLAN":
                self.console.print(Panel(text, title="📋 Current Plan", border_style="blue"))
            elif style == "SUCCESS":
                self.console.print(f"✅ {text}", style="green")
            elif style == "ERROR":
                self.console.print(f"❌ {text}", style="red")
            elif style == "THINKING":
                self.console.print(f"🧠 {text}", style="yellow")
            elif style == "GENERATING":
                self.console.print(f"🤖 {text}", style="cyan")
            else:
                self.console.print(f"ℹ️ {text}")
        else:
            self._print_basic(text, style)

    def render_dashboard(self, plan: str = "", progress: str = "", confidence: float = 0.0, hit_keywords: List[str] = None):
        """Display the current project status with Phase 10 enhancements."""
        if self.has_rich:
            self.console.print("\n" + "="*50)
            self.console.print("[bold]🎨 NFM-SV VIBE DASHBOARD[/bold]")
            self.console.print("-"*50)
            if plan:
                self.console.print(f"[bold blue]Plan:[/bold blue] {plan[:200]}")
            if progress:
                self.console.print(f"[bold green]Progress:[/bold green] {progress[:200]}")
            if confidence > 0:
                conf_color = "green" if confidence > 0.8 else "yellow" if confidence > 0.5 else "red"
                self.console.print(f"[bold {conf_color}]Confidence:[/bold {conf_color}] {confidence*100:.0f}%")
            if hit_keywords:
                self.console.print(f"[bold magenta]Knowledge Hits:[/bold magenta] {', '.join(hit_keywords)}")
            self.console.print("="*50 + "\n")
        else:
            self._print_basic(f"Confidence: {confidence*100:.0f}%", "INFO")
            if hit_keywords:
                self._print_basic(f"Knowledge Hits: {', '.join(hit_keywords)}", "INFO")
            self._print_basic(f"Plan: {plan[:100]}...", "PLAN")

    def update_todos(self, todos: List[str]):
        """Set the todo list for current task."""
        self.todo_list = todos
        self.current_todo = 0
        self._print_rich("Todo List Updated", "INFO")
        for i, todo in enumerate(todos):
            status = "[bold green]✓[/bold green]" if i < self.current_todo else "[bold yellow]➤[/bold yellow]" if i == self.current_todo else "○"
            self._print_rich(f"{status} {todo}")

    def advance_todo(self):
        """Mark current todo as done and move to next."""
        if self.current_todo < len(self.todo_list):
            self._print_rich(f"Completed: {self.todo_list[self.current_todo]}", "SUCCESS")
            self.current_todo += 1
            if self.current_todo < len(self.todo_list):
                self._print_rich(f"Starting: {self.todo_list[self.current_todo]}", "THINKING")

    def stream_output(self, text: str, label: str = "Output"):
        """Stream text output with typing effect (simulated)."""
        self._print_rich(f"Generating {label}...", "GENERATING")
        if self.has_rich:
            # Simple streaming simulation
            self.console.print(text)
        else:
            print(text)

    def request_approval(self, message: str) -> str:
        """Ask user for approval."""
        self._print_rich(message, "THINKING")
        if not self.use_input:
            return "y"
        try:
            return input("   > (y/n) ").strip().lower()
        except EOFError:
            return "y"

    def request_input(self, message: str) -> str:
        """Request input from user."""
        self._print_rich(message, "PLAN")
        if not self.use_input:
            return "User provided details"
        try:
            return input("   > ").strip()
        except EOFError:
            return "abort"

    def request_fix(self, error_msg: str) -> str:
        """Request a fix command from the user when execution fails."""
        self._print_rich(f"❌ Execution Failed: {error_msg}", "ERROR")
        self._print_rich("🔧 Please provide a fix command (shell command) or type 'abort' to stop.", "PLAN")
        
        if not self.use_input:
            # For automated testing, suggest a dummy fix
            return "echo 'Manual fix applied'"

        try:
            return input("   > Fix: ").strip()
        except EOFError:
            return "abort"

    def show_routing(self, model_name: str, reason: str):
        """Show Smart Routing decision (Lovable style)."""
        self._print_rich(f"Routing to {model_name}: {reason}", "INFO")

    def show_autofix(self, issue: str, fix: str):
        """Show AutoFix action (v0.dev style)."""
        self._print_rich(f"AutoFix detected issue: {issue}", "ERROR")
        self._print_rich(f"AutoFix applied: {fix}", "SUCCESS")
