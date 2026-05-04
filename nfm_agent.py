#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NFM-SV System Agent: The Ultimate Controller
独立 Agent 模块，统一管理 Nexus-Frame-Mnemo-Spark-Vibe 系统

Upgraded: Now uses hybrid search (BM25 + Vector + RRF)
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
    2. 协调所有子模块 (Frame, Mnemo, Spark, Vibe, Mercury)
    3. 提供统一的对外接口
    4. 管理上下文和状态
    5. 集成 Mercury-Crab-Agent 记忆与进化引擎
    6. 【新增】混合搜索记忆系统 (BM25 + 向量 + RRF)
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
        
        # Mercury 记忆层
        self.mercury_bridge = None
        
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
        print(f"[Init] NFM System Agent 初始化...")
        print(f"   [Dir] 项目路径: {self.project_path}")
        
        try:
            # 1. 初始化 Frame (规则引擎)
            frame_db = self.project_path / "frame" / "rules.db"
            frame_db.parent.mkdir(parents=True, exist_ok=True)
            self.frame = FrameEngine(str(frame_db))
            
            # 加载默认规则
            self._load_default_rules()
            
            # 2. 初始化 Mnemo (记忆库) - 升级版支持混合搜索
            memory_path = self.project_path / "memory-bank"
            self.memory = MemoryBank(str(memory_path))
            print(f"   [Memory] MemoryBank 已升级: FTS5 BM25 + 向量搜索")
            
            # 3. 初始化 Global Mnemo (全局经验库) - 升级版支持混合搜索
            global_db = self.project_path / "global_mnemo.db"
            self.global_memory = GlobalMnemo(str(global_db))
            print(f"   [Global] GlobalMnemo 已升级: 混合搜索 (BM25 + 向量)")
            
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
            
            # 7. 初始化 Mercury 记忆与进化引擎
            self._initialize_mercury()
            
            self.is_initialized = True
            print("[PASS] NFM System Agent 初始化完成!")
            self._print_memory_capabilities()
            return True
            
        except Exception as e:
            print(f"[FAIL] 初始化失败: {e}")
            self.is_initialized = False
            return False

    def _print_memory_capabilities(self):
        """打印记忆系统能力"""
        print("\n[Memory] 记忆系统能力:")
        print("   [OK] FTS5 BM25 关键词搜索")
        print("   [OK] 向量语义搜索 (fastembed)")
        print("   [OK] RRF 混合搜索融合")
        print("   [OK] 重要性评分 (自动计算)")
        print("   [OK] 记忆分层 (core/learned/episodic/working/procedural)")
        print("   [OK] 自动过期 (TTL)")
        print("   [OK] 记忆整合 (去重)")
        if self.memory and self.memory.embedder:
            print(f"   [OK] 嵌入模型: {self.memory.embedding_model}")
        else:
            print("   ⚠️  嵌入模型未加载 (仅 BM25 可用)")

    def _load_default_rules(self):
        """加载默认规则集"""
        default_rules = [
            RuleNode(id="base_commit", category="git", 
                    content="Commit after every meaningful change.", 
                    weight=100, triggers=["git", "python", "web"]),
            RuleNode(id="base_test", category="quality", 
                    content="Run tests before committing.", 
                    weight=90, triggers=["python", "web"]),
            RuleNode(id="memory_save", category="memory",
                    content="Save important findings to memory bank after each task.",
                    weight=85, triggers=["python", "web", "git"]),
        ]
        
        for rule in default_rules:
            self.frame.add_rule(rule)

    def _initialize_mercury(self):
        """初始化 Mercury-Crab-Agent 记忆与进化引擎"""
        try:
            from nexus.mercury_bridge import MercuryBridge
            
            # 查找 Mercury-Crab-Agent 项目路径
            possible_paths = [
                self.project_path.parent / "Mercury-Crab-Agent",
                Path(os.path.expanduser("~")) / "Documents" / "GitHub" / "Mercury-Crab-Agent",
                Path(os.path.expanduser("~")) / "GitHub" / "Mercury-Crab-Agent",
            ]
            
            mercury_path = None
            for path in possible_paths:
                if path.exists() and (path / "MEMORY.md").exists():
                    mercury_path = str(path)
                    break
            
            if mercury_path:
                self.mercury_bridge = MercuryBridge(mercury_path)
                print(f"   [Mercury] Mercury Bridge 已连接: {mercury_path}")
                status = self.mercury_bridge.get_status()
                print(f"      HOT: {status['hot_memory_size']} bytes | "
                      f"WARM: {status['warm_days']} days | "
                      f"Skills: {status['skills_count']}")
            else:
                print("   ⚠️ Mercury-Crab-Agent 未找到，记忆层已禁用")
                
        except Exception as e:
            print(f"   ⚠️ Mercury 初始化跳过: {e}")
            self.mercury_bridge = None

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
        
        # 3. 加载 Memory Bank 状态 (向后兼容)
        plan = self.memory.read("plan.md")
        progress = self.memory.read("progress.md")
        
        # 3.5 注入 Mercury 记忆层上下文 (如果可用)
        mercury_context = ""
        if self.mercury_bridge:
            mercury_context = self.mercury_bridge.enrich_context("", command)
            if mercury_context:
                plan = (plan or "") + "\n\n## Mercury 记忆注入\n" + mercury_context[:1500]
        
        # 4. 展示 Dashboard
        self.vibe.render_dashboard(plan, progress)
        
        # 5. 请求人类批准
        approval = self.vibe.request_approval(f"执行命令: '{command}'\n继续？(y/n)")
        if approval.lower() != 'y':
            return {"status": "aborted", "reason": "用户拒绝"}
        
        # 6. 执行命令
        print(f"[Spark] [Spark] 执行: {command}")
        result = self.spark.run(command)
        
        if result["status"] == "ok":
            # 成功路径
            print(f"[PASS] [Spark] 成功")
            
            # 记录到 Mercury 日志
            if self.mercury_bridge:
                self.mercury_bridge.memory.log_daily(f"命令执行成功: {command}")
            
            # 【新增】保存到 Mnemo 记忆库
            self._save_to_memory(command, result, "success")
            
            # Git 提交
            self.git.add_all()
            self.git.commit(f"feat: {command}")
            
            # 更新进度
            new_progress = progress + f"\n- [PASS] 完成: {command}"
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
            print(f"[FAIL] [Spark] 失败: {result['error']}")
            
            # 记录错误到 Mercury 记忆层
            if self.mercury_bridge:
                self.mercury_bridge.record_correction(
                    error=result.get("error", "")[:100],
                    fix="pending"
                )
            
            # 【新增】保存失败经验到 Mnemo
            self._save_to_memory(command, result, "failure")
            
            # 查询全局经验库 (使用混合搜索)
            print("[Memory] [GlobalMnemo] 搜索历史解决方案 (混合搜索)...")
            solutions = self.global_memory.search_solutions(result["error"], self.current_context_tags)
            
            fix_cmd = None
            if solutions:
                best = solutions[0]
                print(f"[Idea] 找到 {len(solutions)} 个历史匹配!")
                print(f"   方案: {best['solution']}")
                print(f"   匹配分数: {best.get('score', 0):.4f}")
                print(f"   历史频率: {best.get('frequency', 0)}")
                
                apply = self.vibe.request_approval("应用历史方案？(y/n)")
                if apply.lower() == 'y':
                    fix_cmd = best['solution']
            
            if not fix_cmd:
                fix_cmd = self.vibe.request_fix(result["error"])
            
            if fix_cmd.lower() == "abort":
                return {"status": "aborted", "reason": "修复中止"}
            
            # 重试
            print(f"[Fix] [Spark] 重试: {fix_cmd}")
            retry = self.spark.run(fix_cmd)
            
            if retry["status"] == "ok":
                print(f"[PASS] [Spark] 修复成功")
                
                self.git.add_all()
                self.git.commit(f"fix: {fix_cmd}")
                
                # 保存到全局经验库 (混合搜索已启用)
                self.global_memory.add_experience(result["error"], fix_cmd, self.current_context_tags)
                self.global_memory.record_success(result["error"])
                print("[Memory] [Global] 经验已保存 (FTS5 + 向量索引)")
                
                # 更新进度
                new_progress = self.memory.read("progress.md") + f"\n- [PASS] 修复: {command} -> {fix_cmd}"
                self.memory.write("progress.md", new_progress)
                
                self.execution_history.append({
                    "command": command,
                    "fix": fix_cmd,
                    "status": "ok",
                    "context": self.current_context_tags
                })
                
                return {"status": "ok", "output": retry["output"]}
            else:
                # 记录失败
                self.global_memory.record_failure(result["error"])
                
                # 触发错误钩子
                if self.on_error:
                    self.on_error(command, result)
                
                return {"status": "error", "error": retry["error"]}

    def _save_to_memory(self, command: str, result: Dict, outcome: str):
        """保存执行结果到记忆库"""
        try:
            # 构造记忆内容
            content_lines = [
                f"Command: {command}",
                f"Outcome: {outcome}",
                f"Context: {', '.join(self.current_context_tags)}",
            ]
            
            if outcome == "success":
                content_lines.append(f"Output: {result.get('output', '')[:500]}")
            else:
                content_lines.append(f"Error: {result.get('error', '')[:500]}")
            
            content = "\n".join(content_lines)
            
            # 选择 tier
            tier = "episodic" if outcome == "success" else "learned"
            
            # 添加到记忆库 (自动生成嵌入向量)
            memory_id = self.memory.add(
                content=content,
                tier=tier,
                metadata={
                    "command": command,
                    "outcome": outcome,
                    "tags": self.current_context_tags
                },
                importance=0.7 if outcome == "success" else 0.9  # 失败经验更重要
            )
            
            print(f"   💾 已保存到记忆库: {memory_id[:8]}...")
            
        except Exception as e:
            print(f"   ⚠️ 保存记忆失败: {e}")

    # ========== 新增: 记忆管理 API ==========
    
    def search_memory(self, query: str, limit: int = 5, 
                     tier_filter: List[str] = None) -> List[Dict]:
        """
        搜索记忆库 (混合搜索)
        
        Args:
            query: 搜索查询
            limit: 返回结果数量
            tier_filter: 限定搜索的记忆层级
        
        Returns:
            记忆列表，按 RRF 分数排序
        """
        if not self.memory:
            return []
        
        return self.memory.search_hybrid(query, limit=limit, tier_filter=tier_filter)
    
    def add_memory(self, content: str, tier: str = "learned", 
                   metadata: Dict = None, importance: float = None) -> str:
        """
        手动添加记忆
        
        Args:
            content: 记忆内容
            tier: 记忆层级 (core/learned/episodic/working/procedural)
            metadata: 元数据
            importance: 重要性 (0.0-1.0)，自动计算如果为 None
        
        Returns:
            记忆 ID
        """
        if not self.memory:
            raise RuntimeError("MemoryBank 未初始化")
        
        return self.memory.add(content, tier=tier, metadata=metadata, importance=importance)
    
    def get_memories_by_tier(self, tier: str, limit: int = 50) -> List[Dict]:
        """按层级获取记忆"""
        if not self.memory:
            return []
        
        return self.memory.get_by_tier(tier, limit=limit)
    
    def consolidate_memories(self, threshold: float = 0.9) -> int:
        """
        整合重复记忆 (去重)
        
        Returns:
            合并的记忆数量
        """
        if not self.memory:
            return 0
        
        return self.memory.consolidate(similarity_threshold=threshold)

    def get_system_status(self) -> Dict:
        """获取系统当前状态"""
        status = {
            "is_initialized": self.is_initialized,
            "project_path": str(self.project_path),
            "current_context": self.current_context_tags,
            "execution_count": len(self.execution_history),
            "memory_bank_files": list((self.project_path / "memory-bank").glob("*.md")) if self.is_initialized else [],
        }
        
        # 添加 Mercury 状态
        if self.mercury_bridge:
            status["mercury"] = self.mercury_bridge.get_status()
        else:
            status["mercury"] = None
        
        # 添加记忆系统状态
        if self.memory:
            status["memory_db"] = str(self.memory.db_path)
            status["embedding_model"] = self.memory.embedding_model if self.memory.embedder else None
        
        if self.global_memory:
            status["global_db"] = str(self.global_memory.db_path)
            status["global_stats"] = self.global_memory.get_stats()
        
        return status

    def reset_context(self):
        """重置上下文 (Commit & Clear)"""
        print("[Reset] 重置上下文...")
        self.current_context_tags = []
        # 可以在这里添加清除 LLM 对话历史的逻辑

    def __repr__(self):
        return f"<NFMSystemAgent path={self.project_path}, initialized={self.is_initialized}>"
