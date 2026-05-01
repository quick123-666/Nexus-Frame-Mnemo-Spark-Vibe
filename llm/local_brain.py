#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
本地 AI 推理模块 - 结合知识库增强决策 (Phase 9: 知识驱动代码生成)
"""
from typing import List, Dict, Optional
from dataclasses import dataclass
import re
from knowledge.code_patterns import get_pattern_for_task, generate_code_guidance, CODE_QUALITY_RULES

@dataclass
class AIContext:
    plan: str
    progress: str
    rules: str
    current_files: List[str]
    git_status: str
    error: Optional[str] = None
    previous_command: Optional[str] = None
    knowledge_guidance: Optional[str] = None

@dataclass
class AIDecision:
    command: str
    reasoning: str
    confidence: float  # 0.0 - 1.0
    requires_approval: bool
    knowledge_used: bool = False
    code_guidance: Optional[str] = None

class LocalBrain:
    """
    本地 AI 推理引擎 (Phase 9: 知识驱动代码生成)
    
    使用模式匹配和规则模板来生成命令
    集成 LLM Wiki 知识库提升决策质量
    使用 Wiki 代码模式生成高质量代码
    """
    
    def __init__(self, knowledge_base=None):
        self.knowledge_base = knowledge_base
        self.command_templates = {
            "create_file": "echo '{content}' > {path}",
            "create_dir": "mkdir -p {path}",
            "install_python": "pip install {package}",
            "install_node": "npm install {package}",
            "git_init": "git init && git add . && git commit -m 'init'",
            "git_commit": "git add . && git commit -m '{message}'",
            "run_python": "python {file}",
            "run_test": "python -m pytest {file}",
        }
        
        self.patterns = [
            {
                "name": "create_project_structure",
                "pattern": r"(?:创建|建立|生成).*(?:项目结构|目录结构|文件夹结构)",
                "template": "mkdir -p src tests && echo '项目结构已创建'",
                "extract": lambda m: {}
            },
            {
                "name": "create_tasks_py",
                "pattern": r"tasks\.py|任务管理.*逻辑",
                "template": "WRITE_FILE:src/tasks.py:import json\\nimport os\\nfrom typing import List, Dict\\nfrom dataclasses import dataclass, asdict\\nfrom pathlib import Path\\n\\n@dataclass\\nclass Task:\\n    id: int\\n    title: str\\n    done: bool = False\\n\\nclass TaskManager:\\n    def __init__(self, db_path: str = \"tasks.json\"):\\n        self.db_path = db_path\\n        self.tasks: List[Task] = []\\n        self._load()\\n\\n    def _load(self):\\n        if os.path.exists(self.db_path):\\n            with open(self.db_path) as f:\\n                data = json.load(f)\\n                self.tasks = [Task(**t) for t in data]\\n\\n    def _save(self):\\n        with open(self.db_path, \"w\") as f:\\n            json.dump([asdict(t) for t in self.tasks], f, indent=2)\\n\\n    def add(self, title: str) -> Task:\\n        task = Task(id=len(self.tasks) + 1, title=title)\\n        self.tasks.append(task)\\n        self._save()\\n        return task\\n\\n    def list_tasks(self) -> List[Task]:\\n        return self.tasks\\n\\n    def done(self, task_id: int) -> bool:\\n        for t in self.tasks:\\n            if t.id == task_id:\\n                t.done = True\\n                self._save()\\n                return True\\n        return False",
                "extract": lambda m: {}
            },
            {
                "name": "create_main_py",
                "pattern": r"main\.py",
                "template": "WRITE_FILE:src/main.py:import sys\\nfrom tasks import TaskManager\\n\\ndef main():\\n    tm = TaskManager()\\n    if len(sys.argv) < 2:\\n        print(\"用法: python main.py <add|list|done> [args]\")\\n        return\\n    cmd = sys.argv[1]\\n    if cmd == \"add\":\\n        title = sys.argv[2]\\n        t = tm.add(title)\\n        print(f\"任务已添加: \" + t.title + \" (ID: \" + str(t.id) + \")\")\\n    elif cmd == \"list\":\\n        tasks = tm.list_tasks()\\n        if not tasks:\\n            print(\"暂无任务\")\\n        else:\\n            for t in tasks:\\n                status = \"[x]\" if t.done else \"[ ]\"\\n                print(\"  \" + status + \" [\" + str(t.id) + \"] \" + t.title)\\n    elif cmd == \"done\":\\n        tid = int(sys.argv[2])\\n        if tm.done(tid):\\n            print(\"任务 \" + str(tid) + \" 已完成\")\\n        else:\\n            print(\"未找到任务 \" + str(tid))\\n\\nif __name__ == \"__main__\":\\n    main()",
                "extract": lambda m: {}
            },
            {
                "name": "install_package",
                "pattern": r"(?:安装|下载|添加|install).*(?:依赖|包|package)|pip install",
                "template": "pip install requests",
                "extract": lambda m: {}
            },
            {
                "name": "create_test_file",
                "pattern": r"(?:创建|写|生成).*测试.*文件|test.*\.py",
                "template": "WRITE_FILE:tests/test_tasks.py:import sys\\nimport os\\nsys.path.insert(0, os.path.join(os.path.dirname(__file__), \"../src\"))\\nfrom tasks import TaskManager\\n\\ndef test_add_task():\\n    tm = TaskManager(\"test_tasks.json\")\\n    t = tm.add(\"Test Task\")\\n    assert t.title == \"Test Task\"\\n    assert t.id == 1\\n    os.remove(\"test_tasks.json\")\\n    print(\"测试通过\")\\n\\nif __name__ == \"__main__\":\\n    test_add_task()",
                "extract": lambda m: {}
            },
            {
                "name": "create_main_py",
                "pattern": r"main\.py",
                "template": "WRITE_FILE:src/main.py:import sys\\nfrom tasks import TaskManager\\n\\ndef main():\\n    tm = TaskManager()\\n    if len(sys.argv) < 2:\\n        print(\"用法: python main.py <add|list|done> [args]\")\\n        return\\n    cmd = sys.argv[1]\\n    if cmd == \"add\":\\n        title = sys.argv[2]\\n        t = tm.add(title)\\n        print(f\"任务已添加: \" + t.title + \" (ID: \" + str(t.id) + \")\")\\n    elif cmd == \"list\":\\n        tasks = tm.list_tasks()\\n        if not tasks:\\n            print(\"暂无任务\")\\n        else:\\n            for t in tasks:\\n                status = \"[x]\" if t.done else \"[ ]\"\\n                print(\"  \" + status + \" [\" + str(t.id) + \"] \" + t.title)\\n    elif cmd == \"done\":\\n        tid = int(sys.argv[2])\\n        if tm.done(tid):\\n            print(\"任务 \" + str(tid) + \" 已完成\")\\n        else:\\n            print(\"未找到任务 \" + str(tid))\\n\\nif __name__ == \"__main__\":\\n    main()",
                "extract": lambda m: {}
            },
            {
                "name": "run_tests",
                "pattern": r"(?:运行|执行).*测试|pytest|unittest",
                "template": "python tests/test_tasks.py",
                "extract": lambda m: {}
            },
            {
                "name": "create_python_file",
                "pattern": r"(?:创建|写|生成).*(?:python|\.py).*文件",
                "template": "echo '# Python file\nprint(\"Hello\")' > new_file.py",
                "extract": lambda m: {}
            },
            {
                "name": "create_directory",
                "pattern": r"(?:创建|建立|生成).*目录|文件夹.*(\w+)",
                "template": "mkdir -p {path}",
                "extract": lambda m: {"path": m.group(1) if m.group(1) else "new_dir"}
            },
            {
                "name": "git_commit",
                "pattern": r"(?:提交|保存|commit).*git",
                "template": "git add . && git commit -m 'update'",
                "extract": lambda m: {}
            },
            {
                "name": "create_requirements",
                "pattern": r"(?:创建|生成).*requirements|依赖文件",
                "template": "echo '# No external dependencies needed' > requirements.txt",
                "extract": lambda m: {}
            },
        ]
        
        self.error_patterns = [
            {
                "pattern": r"ModuleNotFoundError.*No module named '(\w+)'",
                "fix": "pip install {module}",
                "extract": lambda m: {"module": m.group(1)}
            },
            {
                "pattern": r"command not found.*(\w+)",
                "fix": "apt-get install -y {cmd} || brew install {cmd} || winget install {cmd}",
                "extract": lambda m: {"cmd": m.group(1)}
            },
            {
                "pattern": r"Permission denied",
                "fix": "chmod +x {file} || sudo {cmd}",
                "extract": lambda m: {"file": ".", "cmd": m.group(0)}
            },
            {
                "pattern": r"文件不存在|No such file",
                "fix": "echo '需要先创建文件'",
                "extract": lambda m: {}
            },
        ]

    def decide_next_command(self, context: AIContext) -> AIDecision:
        """
        根据上下文决定下一个命令 (Phase 9: 知识驱动代码生成)
        
        Args:
            context: 当前上下文
            
        Returns:
            AIDecision 对象
        """
        # 0. 知识库检索 (如果可用)
        knowledge_guidance = ""
        knowledge_used = False
        code_guidance = None
        
        if self.knowledge_base and context.previous_command:
            query = context.previous_command + " " + context.plan[:100]
            guidance = self.knowledge_base.get_relevant_guidance(query, max_results=2)
            if "相关知识指导" in guidance and "暂无相关" not in guidance:
                knowledge_guidance = guidance
                knowledge_used = True
                context.knowledge_guidance = guidance
        
        # 0.5. 代码生成指导 (基于 Wiki 模式)
        if context.previous_command:
            code_guidance = generate_code_guidance(context.previous_command)
        
        # 1. 优先使用用户输入的命令进行模式匹配
        if context.previous_command:
            for pattern_def in self.patterns:
                match = re.search(pattern_def["pattern"], context.previous_command, re.IGNORECASE | re.UNICODE)
                if match:
                    params = pattern_def["extract"](match)
                    try:
                        command = pattern_def["template"].format(**params)
                        reasoning = f"从用户输入 '{context.previous_command}' 匹配模式: {pattern_def['name']}"
                        if knowledge_used:
                            reasoning += " | 已参考知识库"
                        if code_guidance:
                            reasoning += " | 已应用 Wiki 代码模式"
                        return AIDecision(
                            command=command,
                            reasoning=reasoning,
                            confidence=0.9 if not knowledge_used else 0.95,
                            requires_approval=True,
                            knowledge_used=knowledge_used,
                            code_guidance=code_guidance
                        )
                    except KeyError:
                        continue
        
        # 2. 从计划中提取未完成步骤
        plan_steps = self._extract_plan_steps(context.plan, context.progress)
        if plan_steps:
            next_step = plan_steps[0]
            # 尝试匹配模式
            for pattern_def in self.patterns:
                match = re.search(pattern_def["pattern"], next_step, re.IGNORECASE | re.UNICODE)
                if match:
                    params = pattern_def["extract"](match)
                    try:
                        command = pattern_def["template"].format(**params)
                        reasoning = f"从计划步骤 '{next_step}' 匹配模式: {pattern_def['name']}"
                        if knowledge_used:
                            reasoning += " | 已参考知识库"
                        if code_guidance:
                            reasoning += " | 已应用 Wiki 代码模式"
                        return AIDecision(
                            command=command,
                            reasoning=reasoning,
                            confidence=0.85 if not knowledge_used else 0.9,
                            requires_approval=True,
                            knowledge_used=knowledge_used,
                            code_guidance=code_guidance
                        )
                    except KeyError:
                        continue
            
            # 如果无法匹配具体命令，但知道下一步是什么
            return AIDecision(
                command="ASK_USER",
                reasoning=f"计划中的下一步: {next_step} (需要具体命令)",
                confidence=0.5,
                requires_approval=True
            )
        
        # 3. 根据进度决定下一步
        if not context.progress or context.progress.count("- ✅") == 0:
            return AIDecision(
                command="echo '初始化项目' > README.md",
                reasoning="项目未开始，创建 README",
                confidence=0.6,
                requires_approval=True
            )
        
        # 4. 默认：询问用户
        return AIDecision(
            command="ASK_USER",
            reasoning="无法自动决定，需要人工输入",
            confidence=0.3,
            requires_approval=True
        )

    def _extract_plan_steps(self, plan: str, progress: str) -> List[str]:
        """从计划中提取未完成的步骤"""
        steps = []
        in_steps = False
        
        for line in plan.split('\n'):
            line = line.strip()
            if line.startswith(('##', '#')) and 'step' in line.lower():
                in_steps = True
                continue
            if in_steps and line.startswith('-'):
                # 检查是否已完成
                step_text = line.lstrip('- ').strip()
                if not step_text.startswith('[ ]'):
                    # 检查进度中是否已完成
                    if step_text not in progress and f"完成: {step_text}" not in progress:
                        steps.append(step_text)
        
        return steps

    def fix_error(self, error: str, context: AIContext) -> AIDecision:
        """
        分析错误并生成修复命令
        
        Args:
            error: 错误信息
            context: 当前上下文
            
        Returns:
            AIDecision 对象
        """
        # 1. 错误模式匹配
        for error_def in self.error_patterns:
            match = re.search(error_def["pattern"], error, re.IGNORECASE)
            if match:
                params = error_def["extract"](match)
                try:
                    fix_cmd = error_def["fix"].format(**params)
                    return AIDecision(
                        command=fix_cmd,
                        reasoning=f"匹配错误模式，修复: {fix_cmd}",
                        confidence=0.85,
                        requires_approval=True
                    )
                except KeyError:
                    continue
        
        # 2. 查询全局经验 (需要外部传入)
        # 这里返回一个通用建议
        return AIDecision(
            command="ASK_USER",
            reasoning=f"未知错误: {error[:100]}... 需要人工修复",
            confidence=0.2,
            requires_approval=True
        )

    def _extract_command_from_plan(self, plan: str) -> Optional[str]:
        """从计划中提取明确的命令"""
        # 查找类似 "运行: python main.py" 的模式
        match = re.search(r"运行[:：]\s*(.+)", plan)
        if match:
            return match.group(1).strip()
        
        # 查找类似 "执行: npm install" 的模式
        match = re.search(r"执行[:：]\s*(.+)", plan)
        if match:
            return match.group(1).strip()
        
        return None

    def format_context_for_ai(self, context: AIContext) -> str:
        """格式化上下文为可读文本 (用于展示或发送给我)"""
        text = f"""=== 当前上下文 ===
计划:
{context.plan}

进度:
{context.progress}

激活规则:
{context.rules}

当前文件: {', '.join(context.current_files)}

Git 状态:
{context.git_status}
"""
        if context.error:
            text += f"\n错误:\n{context.error}"
        if context.previous_command:
            text += f"\n上一个命令: {context.previous_command}"
        
        return text
