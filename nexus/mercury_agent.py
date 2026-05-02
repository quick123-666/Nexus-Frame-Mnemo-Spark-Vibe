#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mercury Crab Agent Core: 独立于 OpenClaw 的记忆与进化引擎
基于 NFM-SV 架构实现 Mercury-Crab-Agent 的核心设计 (v2 方案)
"""
import os
import re
import json
import time
import glob
from typing import List, Dict, Optional
from datetime import datetime

class MercuryMemory:
    """管理 Mercury 格式的 HOT/WARM/COLD 记忆层"""
    def __init__(self, root_path: str):
        self.root_path = root_path
        self.memory_md_path = os.path.join(root_path, "MEMORY.md")
        self.memory_dir = os.path.join(root_path, "memory")
        self.self_improving_dir = os.path.join(os.path.dirname(root_path), "self-improving")
        os.makedirs(self.memory_dir, exist_ok=True)
        os.makedirs(self.self_improving_dir, exist_ok=True)

    def log_daily(self, message: str):
        """写入每日记忆日志"""
        today = datetime.now().strftime("%Y-%m-%d")
        daily_path = os.path.join(self.memory_dir, f"{today}.md")
        with open(daily_path, "a", encoding="utf-8") as f:
            f.write(f"- [{datetime.now().strftime('%H:%M')}] {message}\n")

    def load_recent_memory(self, days: int = 2) -> str:
        """加载最近 N 天的记忆作为上下文"""
        context = ""
        for i in range(days):
            d = datetime.now()
            from datetime import timedelta
            target = d - timedelta(days=i)
            path = os.path.join(self.memory_dir, f"{target.strftime('%Y-%m-%d')}.md")
            if os.path.exists(path):
                context += f"## {target.strftime('%Y-%m-%d')}\n"
                with open(path, "r", encoding="utf-8") as f:
                    context += f.read() + "\n\n"
        return context

    def get_corrections(self) -> List[str]:
        """获取最近的纠正记录"""
        corrections_path = os.path.join(self.self_improving_dir, "corrections.md")
        if not os.path.exists(corrections_path):
            return []
        with open(corrections_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        # 简单解析: 提取以 "- " 开头的行
        return [line.strip() for line in lines if line.strip().startswith("- ")]

    def add_correction(self, error: str, fix: str):
        """添加新的纠正记录"""
        corrections_path = os.path.join(self.self_improving_dir, "corrections.md")
        entry = f"- [{datetime.now().strftime('%Y-%m-%d')}] 错误: {error[:50]}... | 修复: {fix[:50]}...\n"
        with open(corrections_path, "a", encoding="utf-8") as f:
            f.write(entry)

    def update_memory_md(self, new_rules: List[str]):
        """更新长期记忆 MEMORY.md"""
        current = ""
        if os.path.exists(self.memory_md_path):
            with open(self.memory_md_path, "r", encoding="utf-8") as f:
                current = f.read()
        
        # 简单的去重追加逻辑
        with open(self.memory_md_path, "w", encoding="utf-8") as f:
            f.write(current)
            f.write(f"\n## Auto-Improved Rules ({datetime.now().strftime('%Y-%m-%d')})\n")
            for rule in new_rules:
                if rule not in current:
                    f.write(f"- {rule}\n")

class MercuryHeartbeat:
    """心跳调度器：解析 HEARTBEAT.md 和 heartbeat-state.json"""
    def __init__(self, memory: MercuryMemory):
        self.memory = memory
        self.state_path = os.path.join(memory.memory_dir, "heartbeat-state.json")
        self._load_state()

    def _load_state(self):
        if os.path.exists(self.state_path):
            with open(self.state_path, "r", encoding="utf-8") as f:
                self.state = json.load(f)
        else:
            self.state = {"lastChecks": {}}
    
    def _save_state(self):
        self.state["lastChecks"]["lastHeartbeat"] = time.time()
        with open(self.state_path, "w", encoding="utf-8") as f:
            json.dump(self.state, f, ensure_ascii=False, indent=2)

    def check_and_run(self, task_name: str, interval_hours: int) -> bool:
        """检查是否到了执行该任务的时间"""
        last_time = self.state["lastChecks"].get(task_name, 0)
        if time.time() - last_time > (interval_hours * 3600):
            self.state["lastChecks"][task_name] = time.time()
            self._save_state()
            return True
        return False

    def get_pending_tasks(self) -> List[str]:
        """根据 HEARTBEAT.md 定义的策略返回待执行任务"""
        tasks = []
        # Task 1: Memory Snapshot (Every time - simulated here as 'maintain')
        tasks.append("maintain_memory")
        
        # Task 4: Self-Improving Scan (Every 6h)
        if self.check_and_run("self_improve", 6):
            tasks.append("scan_corrections")
            
        # Task 7: Knowledge Sync (Every 4h)
        if self.check_and_run("knowledge_sync", 4):
            tasks.append("sync_knowledge")
            
        return tasks

class MercuryCrabAgent:
    """独立运行的 Mercury Agent 核心"""
    def __init__(self, project_path: str):
        self.project_path = project_path
        self.memory = MercuryMemory(project_path)
        self.heartbeat = MercuryHeartbeat(self.memory)

    def run_heartbeat_cycle(self):
        """执行一次心跳循环"""
        print("[Mercury] 💓 Heartbeat triggered...")
        tasks = self.heartbeat.get_pending_tasks()
        for task in tasks:
            try:
                if task == "maintain_memory":
                    self.task_maintain_memory()
                elif task == "scan_corrections":
                    self.task_scan_corrections()
                elif task == "sync_knowledge":
                    self.task_sync_knowledge()
            except Exception as e:
                print(f"[Mercury] Task '{task}' failed: {e}")

    def task_maintain_memory(self):
        """Task 1 & 5: Memory Maintenance & Snapshot"""
        print("  -> Maintaining memory...")
        # 简单逻辑：读取昨天的日志，追加到 MEMORY.md (实际应由 LLM 总结，这里做基础归档)
        # 这里主要是确保 daily log 存在
        self.memory.log_daily("System Heartbeat Check: OK.")

    def task_scan_corrections(self):
        """Task 4: Self-Improving Scan"""
        print("  -> Scanning corrections for patterns...")
        corrections = self.memory.get_corrections()
        # 简单模式识别：如果同一个错误出现多次，提取规则
        # 这里使用简单的关键词计数
        from collections import Counter
        # 提取错误关键词 (假设格式: "- [date] 错误: xxx...")
        # 简化处理：仅记录日志，实际应用可接入 LocalBrain 进行分析
        if len(corrections) > 5:
            self.memory.log_daily(f"Found {len(corrections)} corrections. Review suggested.")

    def task_sync_knowledge(self):
        """Task 7: Knowledge Sync"""
        print("  -> Syncing knowledge status...")
        # 更新 heartbeat-state 中的同步时间，实际同步需要 Wiki 模块支持
        pass

    def record_error(self, error: str, fix: str):
        """供 NFM-SV Medic Team 调用的接口：记录错误到 Mercury"""
        self.memory.add_correction(error, fix)
        self.memory.log_daily(f"Medic Team reported error: {error[:50]}...")
        print(f"[Mercury] Recorded correction from Medic Team.")
