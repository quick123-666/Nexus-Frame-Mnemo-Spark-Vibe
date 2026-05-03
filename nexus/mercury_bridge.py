#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mercury Bridge: 将 Mercury-Crab-Agent 的能力暴露给 NFM-SV 系统
连接 Mercury 的记忆层 (HOT/WARM/COLD) 与 NFM-SV 的 NexusBrain/Medic Team
"""
import os
import json
import re
from typing import Dict, List, Optional
from datetime import datetime

from nexus.mercury_agent import MercuryMemory, MercuryHeartbeat, MercuryCrabAgent


class MercuryBridge:
    """
    桥接 Mercury-Crab-Agent 与 NFM-SV 核心系统
    
    功能:
    1. 读取 Mercury 记忆层 (HOT: MEMORY.md, WARM: recent daily logs, COLD: old archives)
    2. 提供技能列表 (skills/) 供 LocalBrain 参考
    3. 同步纠正记录 (self-improving/) 到 Medic Team
    4. 提供 Mercury 状态给 Web UI
    """
    
    def __init__(self, mercury_project_path: str):
        self.project_path = mercury_project_path
        self.crab = MercuryCrabAgent(mercury_project_path)
        self.memory: MercuryMemory = self.crab.memory
        self.heartbeat: MercuryHeartbeat = self.crab.heartbeat
        
        # 技能缓存
        self._skills_cache: Optional[List[Dict]] = None
        
    # --- Memory Layer Access ---
    
    def get_hot_memory(self) -> str:
        """读取 HOT 记忆层 (MEMORY.md - 长期规则与核心知识)"""
        path = self.memory.memory_md_path
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        return ""
    
    def get_warm_memory(self, days: int = 3) -> str:
        """读取 WARM 记忆层 (最近 N 天的日志)"""
        return self.memory.load_recent_memory(days=days)
    
    def get_cold_memory_summary(self) -> Dict:
        """获取 COLD 记忆层概览 (历史归档统计)"""
        memory_dir = self.memory.memory_dir
        if not os.path.exists(memory_dir):
            return {"total_days": 0, "earliest": None, "latest": None, "total_entries": 0}
        
        files = [f for f in os.listdir(memory_dir) if f.endswith(".md") and f != "MEMORY.md"]
        dates = []
        total_entries = 0
        
        for fname in files:
            # 文件名格式: YYYY-MM-DD.md
            match = re.match(r"(\d{4}-\d{2}-\d{2})\.md", fname)
            if match:
                dates.append(match.group(1))
                fpath = os.path.join(memory_dir, fname)
                with open(fpath, "r", encoding="utf-8") as f:
                    total_entries += sum(1 for line in f if line.strip().startswith("- "))
        
        dates.sort()
        return {
            "total_days": len(dates),
            "earliest": dates[0] if dates else None,
            "latest": dates[-1] if dates else None,
            "total_entries": total_entries,
        }
    
    def get_full_memory_context(self, hot: bool = True, warm: bool = True, warm_days: int = 2, cold: bool = False) -> str:
        """组合多层记忆为完整上下文，供 LocalBrain 使用"""
        parts = []
        
        if hot:
            hot_mem = self.get_hot_memory()
            if hot_mem:
                parts.append("# HOT Memory (长期规则)\n" + hot_mem)
        
        if warm:
            warm_mem = self.get_warm_memory(days=warm_days)
            if warm_mem:
                parts.append("# WARM Memory (近期活动)\n" + warm_mem)
        
        if cold:
            cold_summary = self.get_cold_memory_summary()
            parts.append(f"# COLD Memory (归档概览)\n- 总天数: {cold_summary['total_days']}\n- 总条目: {cold_summary['total_entries']}")
        
        return "\n\n".join(parts)
    
    # --- Skills Access ---
    
    def list_skills(self) -> List[Dict]:
        """扫描 skills/ 目录，返回可用技能列表"""
        if self._skills_cache is not None:
            return self._skills_cache
        
        skills_dir = os.path.join(self.project_path, "skills")
        if not os.path.exists(skills_dir):
            self._skills_cache = []
            return []
        
        skills = []
        for fname in os.listdir(skills_dir):
            if fname.endswith(".skill"):
                skill_path = os.path.join(skills_dir, fname)
                skill_info = self._parse_skill_file(skill_path)
                skills.append(skill_info)
        
        self._skills_cache = skills
        return skills
    
    def _parse_skill_file(self, path: str) -> Dict:
        """解析 .skill 文件，提取名称和描述"""
        name = os.path.splitext(os.path.basename(path))[0]
        description = ""
        
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
            # 尝试提取前几行作为描述
            lines = content.strip().split("\n")
            for line in lines[:10]:
                if line.strip() and not line.strip().startswith("#") and not line.strip().startswith("-"):
                    description = line.strip()[:200]
                    break
        
        return {
            "name": name,
            "file": os.path.basename(path),
            "description": description,
            "path": path,
        }
    
    def get_skill_content(self, skill_name: str) -> Optional[str]:
        """获取指定技能的完整内容"""
        skill_path = os.path.join(self.project_path, "skills", f"{skill_name}.skill")
        if os.path.exists(skill_path):
            with open(skill_path, "r", encoding="utf-8") as f:
                return f.read()
        return None
    
    # --- Self-Improving / Corrections ---
    
    def get_corrections(self, limit: int = 20) -> List[str]:
        """获取最近的纠正记录"""
        all_corrections = self.memory.get_corrections()
        return all_corrections[-limit:] if len(all_corrections) > limit else all_corrections
    
    def record_correction(self, error: str, fix: str):
        """记录新的纠正 (与 MercuryCrabAgent.record_error 兼容)"""
        self.crab.record_error(error, fix)
        # 同时写入 Medic Team 格式
        self.memory.add_correction(error, fix)
    
    # --- Heartbeat / Status ---
    
    def get_status(self) -> Dict:
        """获取 Mercury Agent 的完整状态，供 Web UI 展示"""
        hot_size = 0
        if os.path.exists(self.memory.memory_md_path):
            hot_size = os.path.getsize(self.memory.memory_md_path)
        
        cold_summary = self.get_cold_memory_summary()
        skills = self.list_skills()
        corrections = self.get_corrections(limit=5)
        
        return {
            "hot_memory_size": hot_size,
            "warm_days": cold_summary["total_days"],
            "cold_entries": cold_summary["total_entries"],
            "skills_count": len(skills),
            "skills": [s["name"] for s in skills[:10]],
            "recent_corrections": corrections,
            "project_path": self.project_path,
            "last_heartbeat": self.heartbeat.state.get("lastChecks", {}).get("lastHeartbeat", 0),
        }
    
    def run_heartbeat(self):
        """手动触发心跳循环"""
        self.crab.run_heartbeat_cycle()
    
    # --- Integration with LocalBrain ---
    
    def enrich_context(self, base_context: str, query: str = "") -> str:
        """
        将 Mercury 记忆注入到 LocalBrain 的上下文中
        根据查询关键词智能选择相关记忆
        """
        enriched = base_context
        
        # 检查查询是否涉及规则/策略
        if any(kw in query.lower() for kw in ["规则", "rule", "策略", "policy", "纠正", "correction"]):
            hot = self.get_hot_memory()
            if hot:
                enriched += "\n\n## Mercury 长期规则\n" + hot[:2000]
            
            corrections = self.get_corrections(limit=10)
            if corrections:
                enriched += "\n\n## Mercury 纠正记录\n" + "\n".join(corrections)
        
        # 检查查询是否涉及近期活动
        if any(kw in query.lower() for kw in ["近期", "recent", "昨天", "yesterday", "日志", "log"]):
            warm = self.get_warm_memory(days=2)
            if warm:
                enriched += "\n\n## Mercury 近期活动\n" + warm[:2000]
        
        # 检查查询是否涉及技能
        if any(kw in query.lower() for kw in ["技能", "skill", "能力", "capability"]):
            skills = self.list_skills()
            if skills:
                skills_text = "\n".join([f"- {s['name']}: {s['description']}" for s in skills])
                enriched += f"\n\n## Mercury 可用技能\n{skills_text}"
        
        return enriched
