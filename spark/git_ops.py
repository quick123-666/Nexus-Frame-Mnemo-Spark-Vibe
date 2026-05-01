#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NFM-SV Spark: Git Operations
Manages version control, tagging, and rollback.
"""
from .executor import SparkExecutor

class GitOps:
    def __init__(self, cwd: str):
        self.executor = SparkExecutor(cwd)

    def init(self) -> dict:
        return self.executor.run("git init")

    def add_all(self) -> dict:
        return self.executor.run("git add .")

    def commit(self, message: str) -> dict:
        # Config user for git if not set globally (for testing in isolated envs)
        self.executor.run('git config user.email "synth@nfm-sv.ai"')
        self.executor.run('git config user.name "Synth Agent"')
        res = self.executor.run(f'git commit -m "{message}"')
        return res

    def tag(self, tag_name: str) -> dict:
        return self.executor.run(f"git tag {tag_name}")

    def status(self) -> dict:
        return self.executor.run("git status --short")

    def reset(self, target: str = "HEAD") -> dict:
        """Hard reset to target."""
        return self.executor.run(f"git reset --hard {target}")
