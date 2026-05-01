# Nexus-Frame-Mnemo-Spark-Vibe (NFM-SV)

> **An Agent-Centric Vibe Coding Operating System**  
> Where human intent meets autonomous execution, guided by graph-based rules and cross-project memory.

![Phase](https://img.shields.io/badge/Phase-9%20Complete-brightgreen)
![Python](https://img.shields.io/badge/Python-3.12+-blue)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 🧠 What is NFM-SV?

NFM-SV is a **Vibe Coding OS** that transforms natural language intent into executed code. It follows the **Agent-Centric** architecture where the AI Agent is the kernel, and all other modules are tools/services.

### Core Philosophy
1. **Planning is Central** — AI autonomous planning leads to code rot. Humans control direction through documents (plan.md, AGENTS.md).
2. **Context is Asset, Code is Byproduct** — Maintaining high-quality context (Memory Bank, Frame Rules) is more important than the code itself.
3. **Small Steps, Fast Iteration** — AI context windows are limited. The "Commit & Clear" cycle maintains peak efficiency.
4. **Learning from Experience** — Cross-project memory enables the system to get smarter with every error.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    NFM-SV Architecture                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐   │
│  │   Nexus 🧠    │◄──►│ LocalBrain 🤖│◄──►│ Knowledge 📚 │   │
│  │  (Agent Brain)│    │  (AI Engine) │    │ (Wiki 149 docs)│  │
│  └──────┬───────┘    └──────────────┘    └──────────────┘   │
│         │                                                    │
│    ┌────┴────┬────────┬────────┬────────┬────────┐           │
│    │         │        │        │        │        │           │
│  ┌─▼─┐    ┌─▼─┐    ┌─▼─┐    ┌▼──┐    ┌▼──┐    ┌▼──┐        │
│  │Frame│  │Mnemo│   │Spark│   │Git │   │Vibe│    │Global│   │
│  │📐   │  │💾   │   │⚡    │   │Ops │   │🎨  │    │Mnemo │   │
│  │Rules│  │Memory│  │Exec  │   │📦  │   │HITL│    │💾    │   │
│  └─────┘  └─────┘   └─────┘   └────┘   └────┘    └──────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Module Overview

| Module | Symbol | Function | Key Feature |
|--------|--------|----------|-------------|
| **Nexus** | 🧠 | Agent Brain | Orchestrates all subsystems, composes dynamic prompts |
| **Frame** | 📐 | Graph Rule Engine | SQLite-based rule graph with inheritance and conflict resolution |
| **Mnemo** | 💾 | Memory Bank | Project state (plan.md, progress.md, tech.md) |
| **Spark** | ⚡ | Command Executor | Safe shell execution with timeouts and WRITE_FILE support |
| **GitOps** | 📦 | Version Control | Automatic git init, add, commit after every change |
| **Vibe** | 🎨 | HITL Interface | Dashboard display, human approval, error recovery |
| **LocalBrain** | 🤖 | Local AI Engine | Pattern matching with 10+ code patterns |
| **Knowledge** | 📚 | Wiki Integration | 149 indexed documents, 395 keywords from LLM best practices |
| **GlobalMnemo** | 💾 | Cross-Project Memory | Error-solution pairs shared across all projects |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Git

### Installation
```bash
git clone https://github.com/quick123-666/Nexus-Frame-Mnemo-Spark-Vibe.git
cd Nexus-Frame-Mnemo-Spark-Vibe
```

### Usage

#### 1. Using NFM System Agent (Recommended)
```python
from nfm_agent import NFMSystemAgent

# Create and initialize
agent = NFMSystemAgent(project_path="./my_project")
agent.initialize()

# Execute commands with AI assistance
result = agent.execute_command(
    "创建 Python 文件 main.py",
    context_tags=["python", "git"]
)
```

#### 2. Using Nexus Brain Directly
```python
from frame import FrameEngine, RuleNode
from mnemo import MemoryBank, GlobalMnemo
from spark import SparkExecutor, GitOps
from vibe import VibeInterface
from nexus import NexusBrain

# Initialize subsystems
frame = FrameEngine("rules.db")
frame.add_rule(RuleNode(id="base", category="git", content="Commit after every change.", weight=100, triggers=["git"]))

memory = MemoryBank("./memory-bank")
spark = SparkExecutor(cwd=".")
git = GitOps(cwd=".")
git.init()

vibe = VibeInterface(use_input=True)
global_memory = GlobalMnemo("global_mnemo.db")

# Create Nexus Brain
nexus = NexusBrain(frame, memory, spark, git, vibe, global_memory)

# Execute with human-in-the-loop
result = nexus.execute_with_human_loop("创建项目结构", ["git", "python"])
```

#### 3. CLI Mode
```bash
python main.py init python my_project
```

---

## 📋 Development Phases

| Phase | Name | Status | Description |
|-------|------|--------|-------------|
| 1 | Core Skeleton | ✅ | Frame (graph rules), Mnemo (memory), Nexus (brain) |
| 2 | Spark Executor | ✅ | Safe shell execution, Git automation |
| 3 | Vibe Interface | ✅ | HITL dashboard, approval workflow, error recovery |
| 4 | Templates | ✅ | Python & web project scaffolding |
| 5 | Global Memory | ✅ | Cross-project error-solution database |
| 6 | Local AI | ✅ | LocalBrain with pattern matching engine |
| 7 | Real Project | ✅ | CLI Task Manager built end-to-end |
| 8 | Knowledge Base | ✅ | LLM Wiki integration (149 docs, 395 keywords) |
| 9 | Knowledge-Driven Code | ✅ | Wiki-based code patterns improve generation quality |

---

## 🧪 Testing

```bash
# Run quick pattern test
python test_quick.py

# Run full e2e test
python test_e2e.py

# Run knowledge base test
python test_knowledge.py
```

---

## 📊 Knowledge Base

NFM-SV integrates with the **Mercury-Crab-Agent Wiki** containing:
- **149 indexed documents**
- **395 coding keywords**
- **33.64 MB** of LLM best practices

### Covered Topics
- Vibe Coding methodologies
- Claude Code best practices (from 47.7k-star repo)
- Context Engineering guides
- Pydantic AI Agent patterns
- MCP Server development
- Testing strategies (pytest, TestModel, FunctionModel)
- Git workflow patterns
- Error handling patterns

---

## 🔧 Configuration

### config.yaml
```yaml
project:
  name: "my-project"
  type: "python"

agent:
  interactive: true
  use_mock: false

knowledge:
  wiki_path: "../Mercury-Crab-Agent/wiki"
  index_file: "knowledge_index.json"
```

---

## 📁 Project Structure

```
Nexus-Frame-Mnemo-Spark-Vibe/
├── frame/              # Graph-based rule engine
│   ├── engine.py       # RuleNode, RuleEdge, FrameEngine
│   └── __init__.py
├── mnemo/              # Memory bank
│   ├── bank.py         # MemoryBank (file-based)
│   ├── global_exp.py   # GlobalMnemo (SQLite experience DB)
│   └── __init__.py
├── spark/              # Command executor
│   ├── executor.py     # SparkExecutor + WRITE_FILE support
│   ├── git_ops.py      # GitOps automation
│   └── __init__.py
├── vibe/               # Human interface
│   ├── interface.py    # VibeInterface (HITL)
│   └── __init__.py
├── nexus/              # Agent brain
│   ├── brain.py        # NexusBrain (orchestrator)
│   └── __init__.py
├── llm/                # AI engine
│   ├── local_brain.py  # LocalBrain (pattern matching)
│   └── __init__.py
├── knowledge/          # Knowledge base
│   ├── base.py         # KnowledgeBase (wiki indexer)
│   ├── code_patterns.py # Wiki-derived code patterns
│   └── __init__.py
├── templates/          # Project scaffolds
│   ├── python/         # Python project template
│   └── web/            # Web project template
├── memory-bank/        # Project memory
│   ├── plan.md
│   ├── progress.md
│   └── tech.md
├── nfm_agent.py        # NFMSystemAgent (unified controller)
├── main.py             # CLI entry point
├── config.yaml         # Configuration
└── README.md           # This file
```

---

## 🎯 Key Features

### 1. Graph-Based Rule Engine
Rules are stored as nodes and edges in SQLite, supporting:
- **Inheritance** — child rules inherit parent properties
- **Conflict Resolution** — weight-based priority system
- **Dynamic Activation** — rules triggered by context tags

### 2. Cross-Project Memory
Errors and solutions are stored globally:
```python
# Save experience
global_memory.add_experience("ModuleNotFoundError: requests", "pip install requests", ["python"])

# Search solutions
solutions = global_memory.search_solutions("ModuleNotFoundError", ["python"])
```

### 3. Knowledge-Enhanced Decision Making
Every command decision is enhanced by:
- Wiki document retrieval (149 docs)
- Code pattern matching (6 patterns)
- Quality checklist (8 rules)
- Anti-pattern prevention (8 rules)

### 4. Human-in-the-Loop
Safety-first execution:
1. Display dashboard (plan, progress)
2. Request human approval (y/n/modify)
3. Execute command
4. Auto-commit on success
5. Error recovery with global memory

---

## 🛡️ Safety Features

| Feature | Description |
|---------|-------------|
| **Timeout** | Commands timeout after 30s |
| **Approval Required** | Every command needs human approval |
| **Abort Support** | Users can abort at any step |
| **Mock Mode** | Test mode without real execution |
| **Isolated Environment** | Each project has its own memory and rules |

---

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

MIT License — see LICENSE file for details.

---

*Built with 🧠 by Synth Agent — Phase 9 Complete*
