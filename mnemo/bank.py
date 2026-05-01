#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NFM-SV Mnemo: Memory Bank Manager
"""
import os
from pathlib import Path

class MemoryBank:
    STANDARD_FILES = {
        "plan.md": "# Implementation Plan\n\n## Steps\n1. [ ] Step 1\n",
        "progress.md": "# Progress\n\n## Completed\n- \n",
        "architecture.md": "# Architecture\n\n## Overview\n\n",
        "tech.md": "# Tech Stack\n\n## Dependencies\n\n",
    }

    def __init__(self, bank_path: str):
        self.bank_path = Path(bank_path)
        self.bank_path.mkdir(parents=True, exist_ok=True)
        self._initialize_bank()

    def _initialize_bank(self):
        for filename, content in self.STANDARD_FILES.items():
            file_path = self.bank_path / filename
            if not file_path.exists():
                file_path.write_text(content, encoding="utf-8")

    def read(self, filename: str) -> str:
        file_path = self.bank_path / filename
        if file_path.exists():
            return file_path.read_text(encoding="utf-8")
        return ""

    def write(self, filename: str, content: str):
        file_path = self.bank_path / filename
        file_path.write_text(content, encoding="utf-8")

    def get_snapshot(self) -> dict:
        """Get a summary of all files for context injection."""
        snapshot = {}
        for filename in self.STANDARD_FILES.keys():
            content = self.read(filename)
            # Truncate if too long to save tokens
            snapshot[filename] = content[:2000] + "..." if len(content) > 2000 else content
        return snapshot
