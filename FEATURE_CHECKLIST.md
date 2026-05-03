# NFM-SV (Nexus-Frame-Mnemo-Spark-Vibe) 功能清单与部署指南

## 📋 1. 架构概览
本项目是一个全能型的 **AI 自主 Agent 框架**，集成了记忆、推理、视觉操作和代码修复能力。所有模块均可通过 `installer.py` 一键部署。

| 模块代号 | 名称 | 核心功能 | 状态 |
| :--- | :--- | :--- | :--- |
| **Nexus** | 大脑中枢 | 决策路由、子代理调度、意图识别 | ✅ 已集成 |
| **Mnemo** | 记忆银行 | 长期记忆存储、上下文快照、会话回溯 | ✅ 已集成 |
| **Frame** | 规则引擎 | 行为约束、动态规则库、防幻觉检查 | ✅ 已集成 |
| **Spark** | 执行引擎 | 任务拆解、GitOps 操作、代码生成 | ✅ 已集成 |
| **Vibe** | 交互界面 | 聊天前端 (FastAPI+WebSocket)、实时反馈 | ✅ 已集成 |
| **Visual** | 视觉感知 | **Mano-P** 集成、GUI 自动化、屏幕识别 | ✅ 已集成 |
| **Knowledge** | 知识库 | 本地 Wiki 索引、项目推荐、代码模式匹配 | ✅ 已集成 |
| **Chat** | 聊天室 | 实时多人聊天、AI 机器人集成 (Nexus Chat) | ✅ 新增 |

## 🛠️ 2. 依赖环境清单
运行本项目需要以下 Python 库支持（`installer.py` 会自动安装）：

### 2.1 核心服务 (Core)
- [x] `fastapi`: Web 框架
- [x] `uvicorn`: ASGI 服务器
- [x] `pydantic`: 数据验证
- [x] `websockets`: 实时通信
- [x] `httpx`: 异步 HTTP 请求 (LLM API)
- [x] `psutil`: 系统性能监控

### 2.2 视觉自动化 (Mano-P)
- [x] `mss`: 跨平台屏幕截图
- [x] `pynput`: 鼠标/键盘控制
- [x] `pillow`: 图像处理
- [x] `customtkinter`: 现代化 GUI 界面

### 2.3 AI 知识库与工具
- [x] `llmwikify`: LLM 驱动的知识库管理
- [x] `fastmcp`: MCP 协议支持 (Agent 通信)
- [x] `aiofiles`: 异步文件 I/O

## 🚀 3. 部署流程 (Installer Checklist)
`installer.py` 部署时将逐项确认以下状态：

1. **环境检测**:
   - [x] Python 3.10+
   - [x] pip 可用
   - [x] 系统架构兼容 (Windows/Linux/MacOS)

2. **依赖安装**:
   - [x] Core Dependencies
   - [x] Visual Dependencies
   - [x] AI Dependencies

3. **内置与外部集成验证**:
   | 组件名称 | 类型 | 路径/来源 | 状态 |
   | :--- | :--- | :--- | :--- |
   | **Nexus-Medic-Team** | 🟢 内置模块 | `./nexus/medic_team.py` (随仓库分发) | ✅ 已内置 |
   | **Mercury-Crab-Agent** | 🔵 外部依赖 | [quick123-666/Mercury-Crab-Agent](https://github.com/quick123-666/Mercury-Crab-Agent) | ✅ 已集成 |
   | **Mano-P** | 🔵 外部依赖 | [Mininglamp-AI/Mano-P](https://github.com/Mininglamp-AI/Mano-P) | ✅ 已集成 |
   | **PBL Tutorials** | 🟡 数据注入 | [practical-tutorials/project-based-learning](https://github.com/practical-tutorials/project-based-learning) | ✅ 已注入 |

4. **配置文件**:
   - [x] 生成 `config.yaml` (若不存在)

5. **启动项**:
   - [x] 创建 `start_nfm_sv.bat` (Windows)
   - [x] 验证 `web/server.py` 端口 8000 可用

## 🧪 4. 已集成的高级特性
- **动态拦截**: 在 Vibe 界面输入 "Mano" 或 "GUI" 即可触发视觉模式。
- **单端口运行**: Mercury 和 Medic 已从独立服务转为内部后台任务 (Background Tasks)。
- **PBL 学习库**: 包含 50,000+ 字的项目实战教程索引，LocalBrain 可随时调用推荐。
