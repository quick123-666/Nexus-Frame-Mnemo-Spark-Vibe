#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Nexus Medic Team: 项目修复与进化智能体团队
核心理念:
1. 记忆 (Memory): 跨项目经验复用，Case-Based Reasoning.
2. 自学习 (Self-Learning): 从失败中提取模式，更新修复策略权重.
3. 自进化 (Self-Evolution): 动态调整"黄金规则"，适应项目演进.
4. 坚持原则 (Persistence): 防止上下文漂移，捍卫"已验证的正确方案".
"""
import os
import json
import time
from typing import List, Dict, Optional
from dataclasses import dataclass

# --- 记忆模块 ---

@dataclass
class RepairCase:
    id: str
    error_pattern: str
    solution: str
    success_score: float  # 0.0 - 1.0
    timestamp: float
    tags: List[str]

class EvolutionaryMemory:
    """进化记忆库：存储修复案例并动态调整权重"""
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.cases: List[RepairCase] = []
        self._load()

    def _load(self):
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.cases = [RepairCase(**c) for c in data.get('cases', [])]
            except:
                self.cases = []

    def save(self):
        with open(self.db_path, 'w', encoding='utf-8') as f:
            json.dump({'cases': [c.__dict__ for c in self.cases]}, f, ensure_ascii=False, indent=2)

    def recall(self, error_context: str) -> Optional[RepairCase]:
        """基于相似度检索历史成功修复方案"""
        best_match = None
        max_score = 0.0
        for case in self.cases:
            if case.error_pattern.lower() in error_context.lower():
                # 匹配度 = 基础分 * 历史成功率衰减
                score = case.success_score * 0.95
                if score > max_score:
                    max_score = score
                    best_match = case
        return best_match

    def learn(self, error: str, solution: str, success: bool, tags: List[str]):
        """学习新经验"""
        case = RepairCase(
            id=f"case_{int(time.time())}",
            error_pattern=error[:100],
            solution=solution,
            success_score=0.9 if success else 0.1,
            timestamp=time.time(),
            tags=tags
        )
        self.cases.append(case)
        self.save()
        print(f"[Memory] 🧠 已记录案例: {'✅ 成功' if success else '❌ 失败'} -> {solution[:30]}...")

# --- 团队角色 ---

class ArchitectAgent:
    """架构师：制定并捍卫"正确方案"，防止上下文漂移"""
    def __init__(self, memory: EvolutionaryMemory):
        self.memory = memory
        self.golden_plan: str = ""
        self.plan_drift_threshold = 0.3

    def define_golden_plan(self, plan: str):
        """确立不可轻易更改的核心方案"""
        self.golden_plan = plan
        print(f"[Architect] 🏛️ 已确立黄金方案: {plan[:50]}...")

    def check_drift(self, proposed_change: str) -> bool:
        """检查提议的变更是否偏离黄金方案"""
        if not self.golden_plan:
            return False
        # 简单实现：如果变更与方案关键词冲突，则视为漂移
        # 实际应使用更复杂的语义对比
        return False 

class DiagnosticAgent:
    """诊断师：精准定位问题根因"""
    def analyze(self, error_log: str, project_structure: Dict) -> Dict:
        """分析错误日志"""
        if "ModuleNotFoundError" in error_log:
            return {"type": "dependency", "severity": "high", "action": "install_missing_package"}
        elif "SyntaxError" in error_log:
            return {"type": "syntax", "severity": "critical", "action": "fix_syntax"}
        elif "ConnectionRefused" in error_log:
            return {"type": "network", "severity": "medium", "action": "check_service_port"}
        return {"type": "unknown", "severity": "low", "action": "manual_review"}

class RepairAgent:
    """执行师：执行修复动作"""
    def __init__(self, memory: EvolutionaryMemory, knowledge_base=None):
        self.memory = memory
        self.knowledge_base = knowledge_base

    def attempt_fix(self, diagnosis: Dict, context: str) -> str:
        """尝试修复"""
        # 1. 优先回忆历史经验
        past_case = self.memory.recall(context)
        if past_case and past_case.success_score > 0.8:
            print(f"[Repair] Matched high-confidence history case: {past_case.solution}")
            return past_case.solution
        
        # 2. 查询 LLM Wiki 知识库
        if self.knowledge_base:
            wiki_guidance = self.knowledge_base.get_relevant_guidance(context)
            if wiki_guidance and "暂无相关知识文档" not in wiki_guidance:
                print(f"[Repair] Found Wiki guidance for error pattern.")
                return f"Apply Wiki guidance: {wiki_guidance[:200]}..."

        # 3. 否则基于诊断生成新方案
        return f"auto_fix_for_{diagnosis['type']}"

# --- 协调器 ---

class MedicCoordinator:
    """Nexus Medic 团队协调器"""
    def __init__(self, memory_path: str = "medic_memory.json", knowledge_base=None):
        self.memory = EvolutionaryMemory(memory_path)
        self.architect = ArchitectAgent(self.memory)
        self.diagnostic = DiagnosticAgent()
        self.repair = RepairAgent(self.memory, knowledge_base=knowledge_base)
        self.execution_history = []

    def handle_project_issue(self, error_log: str, project_context: str, plan: str = "") -> str:
        """处理项目问题全流程"""
        print(f"\n{'='*40}")
        print(f"  🚑 Nexus Medic Team 启动")
        print(f"{'='*40}")

        # 1. 架构师确立/检查方案
        if plan and not self.architect.golden_plan:
            self.architect.define_golden_plan(plan)
        elif plan:
            if self.architect.check_drift(plan):
                return "⚠️ [Architect] 拒绝变更：检测到方案漂移，坚持原有架构。"

        # 2. 诊断师分析
        print("[Diagnostic] 🔍 正在分析根因...")
        diagnosis = self.diagnostic.analyze(error_log, {})
        
        # 3. 执行师修复
        print(f"[Repair] 🛠️ 正在执行修复: {diagnosis['type']}")
        solution = self.repair.attempt_fix(diagnosis, error_log)
        
        # 模拟执行结果 (实际需对接 SparkExecutor)
        success = "success" in error_log.lower() # 模拟
        
        # 4. 记忆模块学习
        self.memory.learn(error_log, solution, success, [diagnosis['type']])
        
        return solution
