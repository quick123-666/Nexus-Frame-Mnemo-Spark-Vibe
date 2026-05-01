<div align="center">

# NFM-SV

**Nexus-Frame-Mnemo-Spark-Vibe**

> _An Agent-Centric Vibe Coding Operating System_
> 
> _智能体驱动的意图编程操作系统_

[![Phase](https://img.shields.io/badge/Phase-9%20Complete-6C63FF?style=for-the-badge)](https://github.com/quick123-666/Nexus-Frame-Mnemo-Spark-Vibe)
[![Python](https://img.shields.io/badge/Python-3.12+-007ACC?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-FF6B6B?style=for-the-badge)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-2ECC71?style=for-the-badge)](https://github.com/quick123-666/Nexus-Frame-Mnemo-Spark-Vibe)

</div>

---

<div align="center">

| English | 中文 |
|:-------:|:----:|
| 🧠 Where human intent meets autonomous execution | 🧠 人类意图与自主执行的交汇点 |
| 📐 Graph-based rules guide every decision | 📐 图规则引导每一次决策 |
| 💾 Cross-project memory enables continuous learning | 💾 跨项目记忆实现持续进化 |

</div>

---

## 🌐 Overview · 概述

<div align="center">

### English

**NFM-SV** is a next-generation **Vibe Coding OS** that transforms natural language into executable code. Built on an **Agent-Centric** architecture, the AI Agent acts as the kernel — orchestrating rules, memory, execution, and human oversight into a seamless development loop.

The system follows four core principles:

1. **Planning is Central** — Human-driven direction via documents, not AI guesswork.
2. **Context is Asset** — High-quality context (rules, memory) matters more than code.
3. **Small Steps, Fast Iteration** — Commit & Clear cycles maintain peak AI performance.
4. **Learning from Experience** — Every error becomes shared knowledge across projects.

### 中文

**NFM-SV** 是一个新一代**意图编程操作系统**，将自然语言转化为可执行代码。基于**智能体中心**架构，AI Agent 作为系统内核——协调规则、记忆、执行和人类监督，形成无缝的开发循环。

系统遵循四大核心理念：

1. **规划为核心** — 通过文档由人类驱动方向，而非 AI 猜测。
2. **上下文即资产** — 高质量的上下文（规则、记忆）比代码本身更重要。
3. **小步快跑** — 提交与清空循环保持 AI 最佳性能。
4. **经验驱动进化** — 每个错误都成为跨项目的共享知识。

</div>

---

## 🏗️ Architecture · 架构

<div align="center">

```
┌──────────────────────────────────────────────────────────────────┐
│                    NFM-SV Architecture · 系统架构                 │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌─────────────┐     ┌─────────────┐     ┌─────────────────┐   │
│   │   Nexus 🧠   │◄──►│ LocalBrain 🤖│◄──►│  Knowledge 📚   │   │
│   │  Agent Brain │    │  AI Engine   │    │ 149 Wiki Docs   │   │
│   └──────┬──────┘     └─────────────┘     └─────────────────┘   │
│          │                                                       │
│     ┌────┴────┬──────────┬────────┬────────┬─────────┐           │
│     │         │          │        │        │         │           │
│   ┌─▼──┐   ┌──▼─┐     ┌─▼──┐    ┌▼──┐    ┌▼──┐    ┌▼──────┐    │
│   │Frame│   │Mnemo│    │Spark│   │Git │   │Vibe│    │Global │    │
│   │ 📐  │   │ 💾  │    │ ⚡  │   │Ops │   │ 🎨 │    │Mnemo  │    │
│   │Rules│   │Memory│   │Exec │   │ 📦 │   │HITL│    │ 💾    │    │
│   └─────┘   └─────┘    └─────┘   └────┘   └────┘    └───────┘    │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

</div>

### Module Matrix · 模块矩阵

| Module · 模块 | Symbol | Function · 功能 | Key Feature · 核心特性 |
|:-------------|:------:|:---------------|:----------------------|
| **Nexus** | 🧠 | Agent Brain · 智能体大脑 | Dynamic prompt composition · 动态提示词组合 |
| **Frame** | 📐 | Graph Rule Engine · 图规则引擎 | SQLite graph with inheritance · SQLite 图结构支持继承 |
| **Mnemo** | 💾 | Memory Bank · 记忆库 | File-based project state · 基于文件的项目状态 |
| **Spark** | ⚡ | Command Executor · 命令执行器 | Safe shell + WRITE_FILE · 安全 Shell + 文件写入 |
| **GitOps** | 📦 | Version Control · 版本控制 | Auto commit after change · 变更后自动提交 |
| **Vibe** | 🎨 | HITL Interface · 人机交互界面 | Dashboard + approval · 面板 + 审批流 |
| **LocalBrain** | 🤖 | Local AI Engine · 本地 AI 引擎 | 10+ pattern matching · 10+ 模式匹配 |
| **Knowledge** | 📚 | Wiki Integration · 知识库集成 | 149 docs, 395 keywords · 149 文档 395 关键词 |
| **GlobalMnemo** | 💾 | Cross-Project Memory · 跨项目记忆 | Error-solution sharing · 错误方案共享 |

---

## 🚀 Quick Start · 快速开始

### Prerequisites · 前置条件

- Python 3.12+
- Git

### Installation · 安装

```bash
git clone https://github.com/quick123-666/Nexus-Frame-Mnemo-Spark-Vibe.git
cd Nexus-Frame-Mnemo-Spark-Vibe
```

### Usage · 使用

<div align="center">

#### Method 1: NFM System Agent (Recommended) · 方法一：系统智能体（推荐）

</div>

```python
from nfm_agent import NFMSystemAgent

# Create and initialize · 创建并初始化
agent = NFMSystemAgent(project_path="./my_project")
agent.initialize()

# Execute with AI assistance · AI 辅助执行
result = agent.execute_command(
    "创建 Python 文件 main.py",
    context_tags=["python", "git"]
)
```

<div align="center">

#### Method 2: Nexus Brain Direct · 方法二：直接使用 Nexus 大脑

</div>

```python
from frame import FrameEngine, RuleNode
from mnemo import MemoryBank, GlobalMnemo
from spark import SparkExecutor, GitOps
from vibe import VibeInterface
from nexus import NexusBrain

# Initialize subsystems · 初始化子系统
frame = FrameEngine("rules.db")
frame.add_rule(RuleNode(
    id="base", category="git",
    content="Commit after every change.",
    weight=100, triggers=["git"]
))

memory = MemoryBank("./memory-bank")
spark = SparkExecutor(cwd=".")
git = GitOps(cwd=".")
git.init()

vibe = VibeInterface(use_input=True)
global_memory = GlobalMnemo("global_mnemo.db")

# Create Nexus Brain · 创建 Nexus 大脑
nexus = NexusBrain(frame, memory, spark, git, vibe, global_memory)

# Execute with human-in-the-loop · 人机协同执行
result = nexus.execute_with_human_loop("创建项目结构", ["git", "python"])
```

---

## 📋 Development Phases · 开发阶段

<div align="center">

| Phase · 阶段 | Name · 名称 | Status · 状态 | Description · 描述 |
|:------------:|:-----------|:-------------:|:------------------|
| **1** | Core Skeleton · 核心骨架 | ✅ | Frame, Mnemo, Nexus 基础架构 |
| **2** | Spark Executor · 执行器 | ✅ | 安全 Shell 执行 + Git 自动化 |
| **3** | Vibe Interface · 交互界面 | ✅ | HITL 面板 + 审批流 + 错误恢复 |
| **4** | Templates · 模板 | ✅ | Python & Web 项目脚手架 |
| **5** | Global Memory · 全局记忆 | ✅ | 跨项目错误方案数据库 |
| **6** | Local AI · 本地 AI | ✅ | LocalBrain 模式匹配引擎 |
| **7** | Real Project · 真实项目 | ✅ | CLI Task Manager 端到端构建 |
| **8** | Knowledge Base · 知识库 | ✅ | LLM Wiki 集成 (149 文档) |
| **9** | Knowledge-Driven Code · 知识驱动 | ✅ | Wiki 代码模式提升生成质量 |

</div>

---

## 📊 Knowledge Base · 知识库

NFM-SV integrates with the **Mercury-Crab-Agent Wiki** · NFM-SV 集成 Mercury-Crab-Agent 知识库：

| Metric · 指标 | Value · 数值 |
|:-------------|:-----------:|
| 📄 Indexed Documents · 索引文档 | **149** |
| 🔑 Coding Keywords · 编程关键词 | **395** |
| 💾 Total Content · 总内容量 | **33.64 MB** |

### Covered Topics · 覆盖主题

- 🌊 Vibe Coding methodologies · 意图编程方法论
- 🤖 Claude Code best practices (47.7k⭐) · Claude Code 最佳实践
- 🧩 Context Engineering guides · 上下文工程指南
- 🧪 Pydantic AI Agent patterns · Pydantic AI 智能体模式
- 🔌 MCP Server development · MCP 服务器开发
- 🧪 Testing strategies · 测试策略 (pytest, TestModel, FunctionModel)
- 🌿 Git workflow patterns · Git 工作流模式
- 🛡️ Error handling patterns · 错误处理模式

---

## 🎯 Key Features · 核心特性

<div align="center">

### 1. Graph-Based Rule Engine · 图规则引擎

Rules stored as nodes and edges in SQLite · 规则以节点和边的形式存储在 SQLite 中

| Feature · 特性 | Description · 描述 |
|:--------------|:------------------|
| **Inheritance · 继承** | Child rules inherit parent properties · 子规则继承父规则属性 |
| **Conflict Resolution · 冲突解决** | Weight-based priority system · 基于权重的优先级系统 |
| **Dynamic Activation · 动态激活** | Rules triggered by context tags · 根据上下文标签触发规则 |

### 2. Cross-Project Memory · 跨项目记忆

```python
# Save experience · 保存经验
global_memory.add_experience(
    "ModuleNotFoundError: requests",
    "pip install requests",
    ["python"]
)

# Search solutions · 搜索方案
solutions = global_memory.search_solutions(
    "ModuleNotFoundError", ["python"]
)
```

### 3. Knowledge-Enhanced Decision Making · 知识增强决策

Every command decision is enhanced by · 每个命令决策均由以下增强：

- 📚 Wiki document retrieval (149 docs) · Wiki 文档检索 (149 文档)
- 🧩 Code pattern matching (6 patterns) · 代码模式匹配 (6 种模式)
- 📏 Quality checklist (8 rules) · 质量检查清单 (8 项规则)
- 🚫 Anti-pattern prevention (8 rules) · 反模式防护 (8 项规则)

### 4. Human-in-the-Loop · 人机协同

Safety-first execution · 安全第一的执行流程：

1. 📋 Display dashboard · 显示面板 (plan, progress)
2. 👤 Request human approval · 请求人类审批 (y/n/modify)
3. ⚡ Execute command · 执行命令
4. 📦 Auto-commit on success · 成功后自动提交
5. 🔄 Error recovery with global memory · 全局记忆错误恢复

</div>

---

## 🛡️ Safety Features · 安全特性

<div align="center">

| Feature · 特性 | Description · 描述 |
|:--------------|:------------------|
| ⏱️ **Timeout · 超时** | Commands timeout after 30s · 命令 30 秒超时 |
| 👤 **Approval Required · 审批必需** | Every command needs human approval · 每个命令需人类审批 |
| 🛑 **Abort Support · 中止支持** | Users can abort at any step · 用户可随时中止 |
| 🎭 **Mock Mode · 模拟模式** | Test mode without real execution · 无真实执行的测试模式 |
| 🔒 **Isolated Environment · 隔离环境** | Each project has its own memory and rules · 每个项目独立记忆和规则 |

</div>

---

## 📁 Project Structure · 项目结构

```
Nexus-Frame-Mnemo-Spark-Vibe/
├── frame/              # 📐 Graph-based rule engine · 图规则引擎
│   ├── engine.py       #     RuleNode, RuleEdge, FrameEngine
│   └── __init__.py
├── mnemo/              # 💾 Memory bank · 记忆库
│   ├── bank.py         #     MemoryBank (file-based) · 基于文件
│   ├── global_exp.py   #     GlobalMnemo (SQLite) · SQLite 经验库
│   └── __init__.py
├── spark/              # ⚡ Command executor · 命令执行器
│   ├── executor.py     #     SparkExecutor + WRITE_FILE
│   ├── git_ops.py      #     GitOps automation · Git 自动化
│   └── __init__.py
├── vibe/               # 🎨 Human interface · 人机交互
│   ├── interface.py    #     VibeInterface (HITL)
│   └── __init__.py
├── nexus/              # 🧠 Agent brain · 智能体大脑
│   ├── brain.py        #     NexusBrain (orchestrator) · 协调器
│   └── __init__.py
├── llm/                # 🤖 AI engine · AI 引擎
│   ├── local_brain.py  #     LocalBrain (pattern matching) · 模式匹配
│   └── __init__.py
├── knowledge/          # 📚 Knowledge base · 知识库
│   ├── base.py         #     KnowledgeBase (wiki indexer) · Wiki 索引
│   ├── code_patterns.py#     Wiki-derived code patterns · Wiki 代码模式
│   └── __init__.py
├── templates/          # 📦 Project scaffolds · 项目脚手架
│   ├── python/         #     Python project template
│   └── web/            #     Web project template
├── memory-bank/        # 💾 Project memory · 项目记忆
│   ├── plan.md
│   ├── progress.md
│   └── tech.md
├── nfm_agent.py        # 🧠 NFMSystemAgent · 系统智能体
├── main.py             # 🚀 CLI entry point · CLI 入口
├── config.yaml         # ⚙️ Configuration · 配置
└── README.md           # 📄 This file
```

---

## 🤝 Contributing · 贡献

<div align="center">

1. Fork the repository · Fork 仓库
2. Create your feature branch · 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. Commit your changes · 提交更改 (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch · 推送到分支 (`git push origin feature/amazing-feature`)
5. Open a Pull Request · 提交 Pull Request

</div>

---

## 📄 License · 许可证

<div align="center">

[MIT License](LICENSE) — Free to use, modify, and distribute.

[MIT 许可证](LICENSE) — 自由使用、修改和分发。

</div>

---

<div align="center">

**Built with 🧠 by Synth Agent — Phase 9 Complete**

_由 Synth Agent 构建 · 第 9 阶段完成_

<p align="center">
  <img src="https://img.shields.io/badge/⭐-Star%20this%20repo-6C63FF?style=for-the-badge" alt="Star">
</p>

</div>
