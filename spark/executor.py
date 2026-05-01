#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NFM-SV Spark: Shell Executor
Handles safe execution of commands with timeouts and environment controls.
"""
import subprocess
import os
from typing import Dict

class SparkExecutor:
    def __init__(self, cwd: str = None, default_timeout: int = 300):
        self.cwd = cwd or os.getcwd()
        self.default_timeout = default_timeout

    def run(self, command: str, timeout: int = None) -> Dict:
        """
        Execute a shell command.
        Supports special commands:
        - WRITE_FILE:<path>:<content> - Write content to file
        Returns: { status: "ok"|"error", output: str, error: str }
        """
        # 特殊处理：文件写入
        if command.startswith("WRITE_FILE:"):
            return self._write_file(command)
        
        try:
            # Secure environment: prevent inheriting sensitive vars if needed
            env = os.environ.copy()
            env["PYTHONIOENCODING"] = "utf-8"

            result = subprocess.run(
                command,
                shell=True,
                cwd=self.cwd,
                capture_output=True,
                text=True,
                timeout=timeout,
                env=env
            )

            if result.returncode == 0:
                return {"status": "ok", "output": result.stdout.strip(), "error": ""}
            else:
                return {
                    "status": "error",
                    "output": result.stdout.strip(),
                    "error": result.stderr.strip()
                }

        except subprocess.TimeoutExpired:
            return {"status": "error", "output": "", "error": f"Command timed out after {timeout}s"}
        except Exception as e:
            return {"status": "error", "output": "", "error": str(e)}

    def _write_file(self, command: str) -> Dict:
        """处理 WRITE_FILE:path:content 命令"""
        try:
            parts = command.split(":", 2)
            if len(parts) != 3:
                return {"status": "error", "output": "", "error": "格式错误: WRITE_FILE:path:content"}
            
            path = parts[1]
            content = parts[2]
            
            # 处理转义
            content = content.replace("\\n", "\n")
            content = content.replace('\\"', '"')
            content = content.replace("\\\\", "\\")
            
            from pathlib import Path
            full_path = Path(self.cwd) / path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content, encoding="utf-8")
            
            return {"status": "ok", "output": f"文件已写入: {path}", "error": ""}
        except Exception as e:
            return {"status": "error", "output": "", "error": str(e)}
