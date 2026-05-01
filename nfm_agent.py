#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NFM-SV System Agent: The Ultimate Controller
独立 Agent 模块，统一管理 Nexus-Frame-Mnemo-Spark-Vibe 系统
"""
import os
import sys
from pathlib import Path

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from frame import FrameEngine, RuleNode, RuleEdge
from mnemo import MemoryBank, GlobalMnemo
from spark import SparkExecutor, GitOps
from vibe import VibeInterface
from typing import List, Dict, Optional, Callable
import json

class NFMSystemAgent:
    """
    Nexus-Frame-Mnemo-Spark-Vibe 系统总控 Agent
    
    职责:
    1. 管理系统生命周期 (初始化、运行、清理)
    2. 协调所有子模块 (Frame, Mnemo, Spark, Vibe)
    3. 提供统一的对外接口
    4. 管理上下文和状态
    """
    
    def __init__(self, project_path: str = None, config: Dict = None):
        self.project_path = Path(project_path or os.getcwd())
        self.config = config or {}
        
        # 子模块句柄
        self.frame: Optional[FrameEngine] = None
        self.memory: Optional[MemoryBank] = None
        self.global_memory: Optional[GlobalMnemo] = None
        self.spark: Optional[SparkExecutor] = None
        self.git: Optional[GitOps] = None
        self.vibe: Optional[VibeInterface] = None
        
        # 状态追踪
        self.is_initialized = False
        self.current_context_tags: List[str] = []
        self.execution_history: List[Dict] = []
        
        # 钩子函数
        self.on_step_start: Optional[Callable] = None
        self.on_step_complete: Optional[Callable] = None
        self.on_error: Optional[Callable] = None

    def initialize(self, template_type: str = None) -> bool:
        """
        初始化整个系统
        
        Args:
            template_type: 模板类型 (web, python, etc.) 或 None (使用当前目录)
        """
        print(f"🚀 NFM System Agent 初始化...")
        print(f"   📁 项目路径: {self.project_path}")
        
        try:
            # 1. 初始化 Frame (规则引擎)
            frame_db = self.project_path / "frame" / "rules.db"
            frame_db.parent.mkdir(parents=True, exist_ok=True)
            self.frame = FrameEngine(str(frame_db))
            
            # 加载默认规则
            self._load_default_rules()
            
            # 2. 初始化 Mnemo (记忆库)
            memory_path = self.project_path / "memory-bank"
            self.memory = MemoryBank(str(memory_path))
            
            # 3. 初始化 Global Mnemo (全局经验库)
            global_db = self.project_path / "global_mnemo.db"
            self.global_memory = GlobalMnemo(str(global_db))
            
            # 4. 初始化 Spark (执行引擎)
            self.spark = SparkExecutor(cwd=str(self.project_path))
            self.git = GitOps(cwd=str(self.project_path))
            
            # 5. 初始化 Git (如果尚未初始化)
            git_check = self.spark.run("git rev-parse --git-dir")
            if git_check["status"] != "ok":
                print("   📦 初始化 Git 仓库...")
                self.git.init()
            
            # 6. 初始化 Vibe (交互界面)
            use_input = self.config.get("interactive", True)
            self.vibe = VibeInterface(use_input=use_input)
            
            self.is_initialized = True
            print("✅ NFM System Agent 初始化完成!")
            return True
            
        except Exception as e:
            print(f"❌ 初始化失败: {e}")
            self.is_initialized = False
            return False

    def _load_default_rules(self):
        """加载默认规则集"""
        default_rules = [
            RuleNode(id="base_commit", category="git", 
                    content="Commit after every meaningful change.", 
                    weight=100, triggers=["git", "python", "web"]),
            RuleNode(id="base_test", category="quality", 
                    content="Run tests before committing.", 
                    weight=90, triggers=["python", "web"]),
        ]
        
        for rule in default_rules:
            self.frame.add_rule(rule)

    def execute_command(self, command: str, context_tags: List[str] = None) -> Dict:
        """
        执行命令的完整生命周期
        
        Args:
            command: 要执行的命令
            context_tags: 上下文标签
            
        Returns:
            执行结果
        """
        if not self.is_initialized:
            raise RuntimeError("系统未初始化。请先调用 initialize()")
        
        self.current_context_tags = context_tags or []
        
        # 1. 触发开始钩子
        if self.on_step_start:
            self.on_step_start(command, self.current_context_tags)
        
        # 2. 解析 Frame 规则
        active_rules = self.frame.resolve_rules(self.current_context_tags)
        rule_context = "\n".join([f"- [{r.category}] {r.content}" for r in active_rules])
        
        # 3. 加载 Memory Bank 状态
        plan = self.memory.read("plan.md")
        progress = self.memory.read("progress.md")
        
        # 4. 展示 Dashboard
        self.vibe.render_dashboard(plan, progress)
        
        # 5. 请求人类批准
        approval = self.vibe.request_approval(f"执行命令: '{command}'\n继续？(y/n)")
        if approval.lower() != 'y':
            return {"status": "aborted", "reason": "用户拒绝"}
        
        # 6. 执行命令
        print(f"⚡ [Spark] 执行: {command}")
        result = self.spark.run(command)
        
        if result["status"] == "ok":
            # 成功路径
            print(f"✅ [Spark] 成功")
            
            # Git 提交
            self.git.add_all()
            self.git.commit(f"feat: {command}")
            
            # 更新进度
            new_progress = progress + f"\n- ✅ 完成: {command}"
            self.memory.write("progress.md", new_progress)
            
            # 触发完成钩子
            if self.on_step_complete:
                self.on_step_complete(command, result)
            
            # 记录历史
            self.execution_history.append({
                "command": command,
                "status": "ok",
                "context": self.current_context_tags
            })
            
            return {"status": "ok", "output": result["output"]}
        
        else:
            # 错误路径
            print(f"❌ [Spark] 失败: {result['error']}")
            
            # 查询全局经验库
            print("🧠 [Nexus] 搜索历史解决方案...")
            solutions = self.global_memory.search_solutions(result["error"], self.current_context_tags)
            
            fix_cmd = None
            if solutions:
                best = solutions[0]
                print(f"💡 找到 {best['frequency']} 个历史匹配!")
                print(f"   建议方案: {best['solution']}")
                
                apply = self.vibe.request_approval("应用历史方案？(y/n)")
                if apply.lower() == 'y':
                    fix_cmd = best['solution']
            
            if not fix_cmd:
                fix_cmd = self.vibe.request_fix(result["error"])
            
            if fix_cmd.lower() == "abort":
                return {"status": "aborted", "reason": "修复中止"}
            
            # 重试
            print(f"🔧 [Spark] 重试: {fix_cmd}")
            retry = self.spark.run(fix_cmd)
            
            if retry["status"] == "ok":
                print(f"✅ [Spark] 修复成功")
                
                self.git.add_all()
                self.git.commit(f"fix: {fix_cmd}")
                
                # 保存到全局经验库
                self.global_memory.add_experience(result["error"], fix_cmd, self.current_context_tags)
                print("🧠 [Global] 经验已保存")
                
                self.execution_history.append({
                    "command": command,
                    "fix": fix_cmd,
                    "status": "ok",
                    "context": self.current_context_tags
                })
                
                return {"status": "ok", "output": retry["output"]}
            else:
                # 触发错误钩子
                if self.on_error:
                    self.on_error(command, result)
                
                return {"status": "error", "error": retry["error"]}

    def get_system_status(self) -> Dict:
        """获取系统当前状态"""
        return {
            "is_initialized": self.is_initialized,
            "project_path": str(self.project_path),
            "current_context": self.current_context_tags,
            "execution_count": len(self.execution_history),
            "memory_bank_files": list((self.project_path / "memory-bank").glob("*.md")) if self.is_initialized else []
        }

    def reset_context(self):
        """重置上下文 (Commit & Clear)"""
        print("🔄 重置上下文...")
        self.current_context_tags = []
        # 可以在这里添加清除 LLM 对话历史的逻辑

    def __repr__(self):
        return f"<NFMSystemAgent path={self.project_path}, initialized={self.is_initialized}>"
