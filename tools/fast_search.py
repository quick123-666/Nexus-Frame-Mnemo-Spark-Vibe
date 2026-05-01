#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fast Project Search Tool (Three-Pronged Approach)
1. Git Traces: Scans .git/config for remote URLs matching the query.
2. Python Fast Scan: Uses os.scandir for high-performance traversal.
3. Targeted Scope: Scans only high-probability directories with depth limits.

Usage:
    python tools/fast_search.py "Open Design"
    python tools/fast_search.py "Nexus" --depth 3
"""

import os
import sys
import configparser
import argparse
from pathlib import Path

# Default high-probability search targets
TARGET_DIRS = [
    r"C:\Users\Administrator\Documents\GitHub",
    r"C:\Users\Administrator\Desktop",
    r"C:\Users\Administrator\Documents",
    r"C:\Users\Administrator\source",
]

class FastProjectSearcher:
    def __init__(self, query: str, depth: int = 2):
        self.query = query.lower()
        self.max_depth = depth
        self.found_paths = set()

    def run(self):
        print(f"🔍 Starting Fast Search for: '{self.query}'")
        print(f"📁 Target Depth: {self.max_depth}")
        print("-" * 60)

        # 1. Git Traces (Global & Local)
        self._check_git_traces()

        # 2. & 3. Fast Scan in Targeted Scope
        for target in TARGET_DIRS:
            if os.path.exists(target):
                self._fast_scan(target)

        # Results
        print("\n" + "=" * 60)
        if self.found_paths:
            print(f"✅ Found {len(self.found_paths)} results:")
            for path in sorted(self.found_paths):
                print(f"   📂 {path}")
        else:
            print("❌ No results found locally.")
            print("💡 Suggestion: Check other drives or search GitHub remotely.")
        print("=" * 60)

    def _fast_scan(self, start_path: str, current_depth: int = 0):
        """Fast scan using os.scandir"""
        try:
            with os.scandir(start_path) as it:
                for entry in it:
                    if entry.is_dir(follow_symlinks=False):
                        name_lower = entry.name.lower().replace("_", "-").replace(" ", "-")
                        
                        # Check folder name match
                        if self.query.replace(" ", "-") in name_lower:
                            self.found_paths.add(entry.path)
                        
                        # Recurse if depth allows
                        if current_depth < self.max_depth:
                            self._fast_scan(entry.path, current_depth + 1)
        except PermissionError:
            pass

    def _check_git_traces(self):
        """Check .gitconfig and local .git/config files for the query"""
        # 1. Global Git Config
        gitconfig = Path.home() / ".gitconfig"
        if gitconfig.exists():
            try:
                config = configparser.ConfigParser()
                # configparser might fail on some gitconfig formats, so manual read fallback
                with open(gitconfig, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read().lower()
                    if self.query in content:
                        self.found_paths.add(str(gitconfig) + " (Global Config Match)")
            except Exception:
                pass

        # 2. Scan for .git folders in target dirs (shallow) to check remote URL
        # This is a "smart" git trace check: look for .git folders and read config
        for target in TARGET_DIRS:
            if os.path.exists(target):
                self._scan_git_configs(target)

    def _scan_git_configs(self, start_path: str, current_depth: int = 0):
        """Recursively find .git/config and check remote URL"""
        try:
            with os.scandir(start_path) as it:
                for entry in it:
                    if entry.name == ".git" and entry.is_dir():
                        config_path = os.path.join(entry.path, "config")
                        if os.path.exists(config_path):
                            try:
                                with open(config_path, 'r', encoding='utf-8', errors='ignore') as f:
                                    content = f.read().lower()
                                    # Check if remote URL contains query (e.g. github.com/user/Open-Design)
                                    if self.query in content:
                                        # Extract repo path (parent of .git)
                                        repo_path = os.path.dirname(entry.path)
                                        self.found_paths.add(f"{repo_path} (via .git/config remote match)")
                            except: pass
                    
                    elif entry.is_dir(follow_symlinks=False):
                        if current_depth < self.max_depth:
                            # Optimization: skip node_modules, __pycache__, .venv
                            if entry.name not in ("node_modules", "__pycache__", ".venv", ".git"):
                                self._scan_git_configs(entry.path, current_depth + 1)
        except PermissionError:
            pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fast Project Search Tool")
    parser.add_argument("query", help="Search keyword")
    parser.add_argument("--depth", type=int, default=2, help="Max scan depth (default: 2)")
    
    args = parser.parse_args()
    
    searcher = FastProjectSearcher(query=args.query, depth=args.depth)
    searcher.run()
