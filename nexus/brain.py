#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NFM-SV Nexus: The Agent Brain (Phase 8 - Knowledge Enhanced)
"""
from frame import FrameEngine
from mnemo import MemoryBank, GlobalMnemo
from spark import SparkExecutor, GitOps
from vibe import VibeInterface
from llm.local_brain import LocalBrain, AIContext, AIDecision
from knowledge import KnowledgeBase
from typing import List, Optional
from pathlib import Path
import os

SYSTEM_PROMPT_TEMPLATE = """
You are Synth, the Vibe Coding Operating System Agent.
You follow the NFM-SV architecture (Nexus-Frame-Mnemo-Spark-Vibe).

# ACTIVE RULES (From Frame)
{rules}

# PROJECT CONTEXT (From Mnemo)
{context}

# INSTRUCTIONS
1. Analyze the user's request.
2. Check 'plan.md' in Mnemo for the current step.
3. Execute the step using Spark tools.
4. Update 'progress.md' in Mnemo after success.
"""

class NexusBrain:
    def __init__(self, engine: FrameEngine, memory: MemoryBank, spark: SparkExecutor, git: GitOps, vibe: VibeInterface, global_memory: GlobalMnemo, knowledge_base: KnowledgeBase = None):
        self.engine = engine
        self.memory = memory
        self.spark = spark
        self.git = git
        self.vibe = vibe
        self.global_memory = global_memory
        
        # 初始化知识库
        if knowledge_base is None:
            # 默认尝试加载 LLM Wiki
            wiki_path = Path(__file__).parent.parent.parent / "Mercury-Crab-Agent" / "wiki"
            index_file = Path(__file__).parent.parent / "knowledge_index.json"
            
            if wiki_path.exists():
                print(f"Loading Knowledge Base: {wiki_path}")
                knowledge_base = KnowledgeBase(wiki_path=str(wiki_path), index_file=str(index_file))
                knowledge_base.load()
            else:
                print("Warning: LLM Wiki not found, knowledge base disabled.")
                knowledge_base = None
        
        self.knowledge_base = knowledge_base
        self.local_brain = LocalBrain(knowledge_base=self.knowledge_base)

    def compose_prompt(self, context_tags: List[str]) -> str:
        """Dynamically compose the system prompt using Frame rules and Mnemo context."""
        active_rules = self.engine.resolve_rules(context_tags)
        rules_text = "\n".join([f"- [{r.category}] {r.content}" for r in active_rules])
        if not rules_text:
            rules_text = "- No specific rules loaded."

        memory_snapshot = self.memory.get_snapshot()
        context_text = "\n\n".join([f"## {k}\n{v}" for k, v in memory_snapshot.items()])

        return SYSTEM_PROMPT_TEMPLATE.format(rules=rules_text, context=context_text)

    def _build_ai_context(self, context_tags: List[str], error: Optional[str] = None, prev_cmd: Optional[str] = None) -> AIContext:
        """构建 AI 上下文"""
        active_rules = self.engine.resolve_rules(context_tags)
        rules_text = "\n".join([f"- [{r.category}] {r.content}" for r in active_rules])
        
        # 获取当前文件列表
        try:
            import os
            current_files = []
            for root, dirs, files in os.walk(self.memory.path):
                # 跳过隐藏目录和数据库文件
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                for f in files:
                    if not f.startswith('.') and not f.endswith('.db'):
                        current_files.append(os.path.join(root, f))
        except:
            current_files = []
        
        # 获取 Git 状态
        git_status_result = self.spark.run("git status --short")
        git_status = git_status_result.get("output", "") if git_status_result["status"] == "ok" else "Git 未初始化"
        
        return AIContext(
            plan=self.memory.read("plan.md"),
            progress=self.memory.read("progress.md"),
            rules=rules_text,
            current_files=current_files,
            git_status=git_status,
            error=error,
            previous_command=prev_cmd
        )

    def execute_with_human_loop(self, user_command: str, context_tags: List[str]) -> dict:
        """
        Phase 6: Execute with Local AI + Global Memory Integration.
        """
        # 1. 构建 AI 上下文 (传入用户命令)
        ai_ctx = self._build_ai_context(context_tags, prev_cmd=user_command)
        
        # 2. 让 LocalBrain 决定下一步
        decision = self.local_brain.decide_next_command(ai_ctx)
        
        print(f"[LocalBrain] {decision.reasoning}")
        print(f"   建议命令: {decision.command}")
        print(f"   置信度: {decision.confidence:.0%}")
        print(f"   知识库: {'[已使用]' if decision.knowledge_used else '[未使用]'}")
        print(f"   Wiki 代码模式: {'[已应用]' if decision.code_guidance else '[未应用]'}")
        
        # 显示代码指导
        if decision.code_guidance:
            print(f"\n[Wiki] 代码生成指导:")
            print(f"{decision.code_guidance[:600]}...\n")
        
        # 3. 如果需要人工输入
        if decision.command == "ASK_USER":
            print(f"\n[Context] 上下文摘要:")
            print(self.local_brain.format_context_for_ai(ai_ctx))
            
            user_input = self.vibe.request_input("请输入要执行的命令 (或 'abort'):")
            if user_input.lower() == "abort":
                return {"status": "aborted", "reason": "User aborted"}
            final_command = user_input
        else:
            # 使用 AI 建议的命令
            approval = self.vibe.request_approval(f"AI 建议: '{decision.command}'\n执行？(y/n/修改)")
            if approval.lower() == 'y':
                final_command = decision.command
            elif approval.lower() == 'n':
                return {"status": "aborted", "reason": "User rejected AI suggestion"}
            else:
                final_command = approval  # 用户修改的命令
        
        # 特殊处理：如果用户命令包含"无效"或"错误"，故意执行失败命令来测试错误恢复
        if "无效" in user_command or "错误" in user_command or "invalid" in user_command.lower():
            print("[Test Mode] Forcing failing command...")
            final_command = "xyz_nonexistent_command_123"
        
        # 4. 执行命令
        print(f"[Spark] 执行: {final_command}")
        result = self.spark.run(final_command)

        if result["status"] == "ok":
            print(f"[Spark] 成功.")
            self.git.add_all()
            self.git.commit(f"feat: {final_command}")
            self.memory.write("progress.md", self.memory.read("progress.md") + f"\n- [OK] 完成: {final_command}")
            return {"status": "ok", "output": result["output"]}
        else:
            # 5. 错误处理 - 使用 LocalBrain 分析
            print("[LocalBrain] 分析错误...")
            fix_decision = self.local_brain.fix_error(result["error"], ai_ctx)
            
            fix_cmd = None
            
            # 先查询全局经验库
            if not fix_decision.command or fix_decision.command == "ASK_USER":
                print("[Nexus] 搜索全局经验库...")
                solutions = self.global_memory.search_solutions(result["error"], context_tags)
                
                if solutions:
                    best_sol = solutions[0]
                    print(f"Found {best_sol['frequency']} historical matches!")
                    print(f"   建议方案: {best_sol['solution']}")
                    
                    auto_apply = self.vibe.request_approval("应用历史方案？(y/n)")
                    if auto_apply.lower() == 'y':
                        fix_cmd = best_sol['solution']
            
            # 如果 LocalBrain 有建议
            if not fix_cmd and fix_decision.command != "ASK_USER":
                print(f"[AI] 建议修复: {fix_decision.command}")
                apply_fix = self.vibe.request_approval("应用 AI 修复方案？(y/n)")
                if apply_fix.lower() == 'y':
                    fix_cmd = fix_decision.command
            
            # 如果都没有，请求人工修复
            if not fix_cmd:
                fix_cmd = self.vibe.request_fix(result["error"])
            
            if fix_cmd.lower() == "abort":
                return {"status": "aborted", "reason": "Fix aborted"}
            
            print(f"[Spark] 重试: {fix_cmd}")
            retry_res = self.spark.run(fix_cmd)
            
            if retry_res["status"] == "ok":
                print(f"[Spark] 修复成功.")
                self.git.add_all()
                self.git.commit(f"fix: {fix_cmd}")
                
                # 保存到全局经验库
                self.global_memory.add_experience(result["error"], fix_cmd, context_tags)
                print("[Global Mnemo] 经验已保存.")
                
                return {"status": "ok", "output": retry_res["output"]}
            else:
                return {"status": "error", "error": "Retry failed."}



