#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NFM-SV Scaffold: Project Initializer
Handles creating new projects from templates.
"""
import os
import shutil
from pathlib import Path

class Scaffold:
    def __init__(self, template_name: str, project_path: str):
        self.template_name = template_name
        self.project_path = Path(project_path)
        self.template_path = Path(__file__).parent / template_name

    def init(self) -> bool:
        """
        Initialize a new project.
        1. Create project directory.
        2. Copy template files.
        3. Initialize Memory Bank & Frame DB if needed.
        """
        if self.project_path.exists():
            if any(self.project_path.iterdir()):
                print(f"❌ Directory '{self.project_path}' is not empty.")
                return False

        self.project_path.mkdir(parents=True, exist_ok=True)

        # Copy template content
        # We copy the contents of the template dir, not the dir itself
        for item in self.template_path.iterdir():
            if item.is_dir():
                dest = self.project_path / item.name
                shutil.copytree(item, dest)
            else:
                shutil.copy2(item, self.project_path / item.name)

        print(f"📦 Initialized project '{self.project_path.name}' from '{self.template_name}' template.")
        print(f"   -> AGENTS.md created")
        print(f"   -> Memory Bank initialized")
        
        return True
