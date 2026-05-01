#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NFM-SV Knowledge: Code Generation Patterns from Wiki
基于 wiki 知识库的代码生成最佳实践
"""
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class CodePattern:
    """代码模式定义"""
    name: str
    category: str  # python, testing, git, error_handling, etc.
    description: str
    template: str
    rules: List[str]  # 最佳实践规则
    source: str  # wiki 文档来源

# 从 Wiki 提取的代码生成模式
WIKI_CODE_PATTERNS = {
    # Python 项目结构
    "python_project_structure": CodePattern(
        name="Python 项目结构",
        category="python",
        description="标准 Python 项目目录结构",
        template="""src/{project_name}/
├── __init__.py
├── main.py
├── config.py
├── tests/
│   ├── __init__.py
│   ├── test_main.py
│   └── conftest.py
├── requirements.txt
├── .env.example
└── README.md""",
        rules=[
            "文件 < 500 行",
            "函数 < 50 行",
            "使用虚拟环境",
            "类型注解必须",
        ],
        source="wiki/projects/context-engineering-claude-code-full-guide/CLAUDE.md"
    ),
    
    # Python 文件模板
    "python_file_template": CodePattern(
        name="Python 文件模板",
        category="python",
        description="标准 Python 文件结构",
        template='''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
{module_name} - {description}
"""
from typing import {types}
import logging

logger = logging.getLogger(__name__)


class {ClassName}:
    """{class_description}"""
    
    def __init__(self, {params}):
        """初始化"""
        {init_code}
    
    def {method_name}(self, {method_params}) -> {return_type}:
        """
        {method_description}
        
        Args:
            {args}
        
        Returns:
            {returns}
        
        Raises:
            {exceptions}
        """
        try:
            {method_body}
        except {Exception} as e:
            logger.error(f"Error in {method_name}: {e}")
            raise''',
        rules=[
            "Google 风格 docstring",
            "类型注解完整",
            "错误处理明确",
            "日志记录",
        ],
        source="wiki/projects/context-engineering-claude-code-full-guide/CLAUDE.md"
    ),
    
    # 测试文件模板
    "test_file_template": CodePattern(
        name="测试文件模板",
        category="testing",
        description="Pytest 标准测试结构",
        template='''"""
Test {module_name}
"""
import pytest
from {module_path} import {ClassName}


@pytest.fixture
def sample_{instance}():
    """提供测试样本"""
    return {ClassName}({fixture_params})


def test_{function}_success(sample_{instance}):
    """测试成功场景"""
    result = sample_{instance}.{method}({test_args})
    assert result is not None
    assert isinstance(result, {expected_type})


def test_{function}_failure(sample_{instance}):
    """测试失败场景"""
    with pytest.raises({Exception}) as exc_info:
        sample_{instance}.{method}({invalid_args})
    assert "{error_message}" in str(exc_info.value)''',
        rules=[
            "使用 pytest fixtures",
            "测试描述性名称",
            "覆盖边缘情况",
            "测试错误处理",
        ],
        source="wiki/projects/context-engineering-use-cases-agent-factory-with-subagents/examples/testing_examples/"
    ),
    
    # 错误处理模式
    "error_handling_pattern": CodePattern(
        name="错误处理模式",
        category="error_handling",
        description="自定义异常层次结构",
        template='''class {BaseError}(Exception):
    """{base_description}"""
    pass


class {SpecificError}({BaseError}):
    """{specific_description}"""
    def __init__(self, {params}):
        {init_code}
        super().__init__({message})


# 使用示例
try:
    {risky_operation}
except {SpecificError} as e:
    logger.warning(f"Operation failed: {e}")
    return {fallback_result}
except {BaseError} as e:
    logger.error(f"Base error: {e}")
    raise''',
        rules=[
            "自定义异常层次",
            "具体异常优先",
            "日志记录所有错误",
            "提供回退方案",
        ],
        source="wiki/projects/context-engineering-claude-code-full-guide/CLAUDE.md"
    ),
    
    # Git 工作流
    "git_workflow_pattern": CodePattern(
        name="Git 工作流模式",
        category="git",
        description="标准 Git 分支策略",
        template="""main (protected) ←── PR ←── feature/{feature_name}
↓ ↑
deploy development

# 日常流程:
git checkout main && git pull origin main
git checkout -b feature/{feature_name}
# 开发...
git add .
git commit -m "{type}({scope}): {subject}"
git push origin feature/{feature_name}""",
        rules=[
            "分支类型: feat/fix/docs/style/refactor/test/chore",
            "提交信息格式: <type>(<scope>): <subject>",
            "main 分支受保护",
            "PR 必须审查",
        ],
        source="wiki/projects/context-engineering-claude-code-full-guide/CLAUDE.md"
    ),
    
    # 配置管理模式
    "config_pattern": CodePattern(
        name="配置管理模式",
        category="python",
        description="环境变量配置",
        template='''"""
Configuration management with validation
"""
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    """应用配置"""
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
    
    {setting_name}: {setting_type} = Field(default={default})
    
    @field_validator("{setting_name}")
    @classmethod
    def validate_{setting_name}(cls, v):
        if not v:
            raise ValueError("{setting_name} cannot be empty")
        return v


settings = Settings()''',
        rules=[
            "使用 pydantic-settings",
            "环境变量验证",
            ".env.example 模板",
            "不要硬编码密钥",
        ],
        source="wiki/projects/context-engineering-use-cases-agent-factory-with-subagents/examples/main_agent_reference/"
    ),
}

# 代码质量规则
CODE_QUALITY_RULES = {
    "file_size": {"max_lines": 500, "description": "文件不超过 500 行"},
    "function_size": {"max_lines": 50, "description": "函数不超过 50 行"},
    "class_size": {"max_lines": 100, "description": "类不超过 100 行"},
    "line_length": {"max_chars": 100, "description": "行长度不超过 100 字符"},
    "type_hints": {"required": True, "description": "所有函数必须有类型注解"},
    "docstrings": {"style": "google", "description": "公共函数必须有 docstring"},
    "error_handling": {"required": True, "description": "必须有错误处理"},
    "testing": {"min_coverage": 0.8, "description": "关键路径测试覆盖率 > 80%"},
}

# 反模式 (Anti-Patterns)
ANTI_PATTERNS = [
    "不要硬编码 API 密钥 - 使用环境变量",
    "不要跳过测试 - 始终包含测试",
    "不要忽略错误处理 - 实现 try/catch",
    "不要创建过于复杂的代码 - 保持简单 (KISS)",
    "不要忘记安全 - 验证所有输入",
    "不要为了通过测试而 mock - 修复代码本身",
    "不要在提交信息中包含 AI 工具名称",
    "不要构建推测性功能 - 遵循 YAGNI 原则",
]


def get_pattern_for_task(task_description: str) -> Optional[CodePattern]:
    """根据任务描述获取最相关的代码模式"""
    task_lower = task_description.lower()
    
    if any(kw in task_lower for kw in ["创建项目", "project structure", "初始化"]):
        return WIKI_CODE_PATTERNS["python_project_structure"]
    elif any(kw in task_lower for kw in ["创建文件", "python file", ".py"]):
        return WIKI_CODE_PATTERNS["python_file_template"]
    elif any(kw in task_lower for kw in ["测试", "test", "pytest"]):
        return WIKI_CODE_PATTERNS["test_file_template"]
    elif any(kw in task_lower for kw in ["错误", "error", "exception", "异常"]):
        return WIKI_CODE_PATTERNS["error_handling_pattern"]
    elif any(kw in task_lower for kw in ["git", "commit", "branch", "分支"]):
        return WIKI_CODE_PATTERNS["git_workflow_pattern"]
    elif any(kw in task_lower for kw in ["配置", "config", "settings", "env"]):
        return WIKI_CODE_PATTERNS["config_pattern"]
    
    return None


def get_quality_checklist() -> Dict:
    """获取代码质量检查清单"""
    return CODE_QUALITY_RULES


def get_anti_patterns() -> List[str]:
    """获取反模式列表"""
    return ANTI_PATTERNS


def generate_code_guidance(task_description: str) -> str:
    """生成代码生成指导"""
    pattern = get_pattern_for_task(task_description)
    
    guidance = "📚 代码生成指导 (基于 Wiki 知识库):\n\n"
    
    if pattern:
        guidance += f"**推荐模式**: {pattern.name}\n"
        guidance += f"**来源**: {pattern.source}\n\n"
        guidance += f"**模板**:\n```\n{pattern.template}\n```\n\n"
        guidance += f"**最佳实践**:\n"
        for rule in pattern.rules:
            guidance += f"  ✅ {rule}\n"
    else:
        guidance += "暂无特定模式，遵循通用规则:\n"
    
    guidance += "\n**质量要求**:\n"
    for rule_name, rule in CODE_QUALITY_RULES.items():
        guidance += f"  📏 {rule['description']}\n"
    
    guidance += "\n**反模式 (避免)**:\n"
    for anti in ANTI_PATTERNS[:4]:
        guidance += f"  ❌ {anti}\n"
    
    return guidance
