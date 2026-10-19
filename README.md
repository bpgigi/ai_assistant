# AI Assistant - AI 智能学习助手

基于 Python、FastAPI 和大语言模型构建的 Web AI 智能助手，支持多轮对话、RAG 知识库问答、对话历史持久化及知识来源追踪。

本项目从最初的 Python 命令行聊天程序逐步发展为集成后端 API、数据库、前端页面和 RAG 检索系统的 AI 应用，主要用于学习和实践 AI 应用开发与后端工程化技术。

## 核心功能

- **AI 多轮对话**：调用 DeepSeek API，结合历史消息实现上下文连续对话。
- **会话管理**：使用 SQLite 持久化聊天记录，支持创建、切换、删除会话。
- **RAG 知识库问答**：使用 ChromaDB 和 Sentence Transformers 实现文档向量化、语义检索和基于资料的问答。
- **查询改写**：结合历史对话，将用户问题改写为适合检索的独立问题。
- **知识来源追踪**：在 RAG 回答中返回检索文档的来源和相似度距离。
- **RAG 效果评估**：实现 Precision、Recall、Hit Rate 等检索指标，以及基于 LLM 的生成质量评估。
- **配置管理**：使用 Pydantic Settings 管理模型参数、API 配置和 RAG 检索参数。
- **自动化测试**：使用 pytest 测试核心业务逻辑、FastAPI 接口和 RAG 功能。

## 当前项目状态

已完成基础 Web 聊天系统、RAG 集成、来源展示、评估模块及自动化测试。

当前正在完善工程结构、依赖管理和项目文档，后续计划实现多文档知识库管理功能。
## 技术栈

| 分类 | 使用技术 | 主要用途 |
|---|---|---|
| 开发语言 | Python 3.12 | 后端业务逻辑 |
| Web 框架 | FastAPI | REST API、接口校验 |
| 大语言模型 | DeepSeek、OpenAI SDK | AI 对话与模型调用 |
| 数据库 | SQLite | 会话及聊天记录持久化 |
| 向量数据库 | ChromaDB | 文档向量存储与语义检索 |
| Embedding | Sentence Transformers、all-MiniLM-L6-v2 | 文本向量化 |
| 数据校验 | Pydantic | 请求响应模型、结构化输出 |
| 配置管理 | Pydantic Settings | 环境变量与模型参数配置 |
| 前端 | HTML、CSS、JavaScript | 聊天交互页面 |
| 自动化测试 | pytest、FastAPI TestClient | 单元测试、接口测试 |
| 部署 | Ubuntu、Nginx、HTTPS | Web 应用部署 |

## 项目结构

```text
ai_assistant/
├── api.py                    # FastAPI 应用入口
├── assistant.py              # AI 助手核心逻辑
├── Conversation.py           # 单个会话管理
├── database.py               # SQLite 数据库操作
├── dependencies.py           # FastAPI 公共依赖
├── schemas.py                # Pydantic 请求与响应模型
├── config.py                 # 项目配置管理
├── llm_service.py            # 大语言模型调用
├── exceptions.py             # 自定义异常
├── tools.py                  # Tool Calling 工具定义
│
├── routers/                  # API 路由
│   ├── conversations.py      # 会话管理接口
│   └── messages.py           # 聊天消息接口
│
├── rag/                      # RAG 核心模块
│   └── service.py            # 文档索引、向量检索、查询改写
│
├── evaluation/               # RAG 效果评估
│   └── rag_eval.py           # 检索与生成质量评估
│
├── frontend/
│   └── index.html            # Web 聊天界面
│
├── tests/                    # 自动化测试
│   ├── test_api.py
│   ├── test_basic.py
│   ├── test_database.py
│   ├── test_rag_integration.py
│   └── test_rag_evaluation.py
│
├── study_notes.md            # 示例知识库文档
├── prompt.json               # 助手角色提示词
├── .env.example              # 环境变量示例
├── requirements.in           # 直接依赖清单
└── requirements.txt          # 依赖版本清单
```

注：以上省略了虚拟环境、缓存、数据库文件和早期学习实验脚本。
## 安装与运行

### 1. 获取项目

```bash
git clone https://github.com/bpgigi/ai_assistant.git
cd ai_assistant
```

### 2. 创建 Python 虚拟环境

推荐使用 Python 3.12。

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows PowerShell 下可使用：

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. 安装项目依赖

```bash
python -m pip install -r requirements.txt
```

注意：当前依赖文件主要基于 WSL Ubuntu 环境整理，Windows 跨平台安装仍需进一步验证。

### 4. 配置环境变量

复制配置模板：

```bash
cp .env.example .env
```

编辑 `.env`，填写自己的 DeepSeek API Key：

```dotenv
DEEPSEEK_API_KEY=your_api_key_here
```

其余参数可按需调整。`.env` 包含敏感配置，不应提交到 Git 仓库。

### 5. 启动 FastAPI

在项目根目录执行：

```bash
fastapi dev api.py
```

启动后可访问：

- API 文档：`http://127.0.0.1:8000/docs`
- Web 前端：通过 HTTP 静态文件服务或 Nginx 提供 `frontend/index.html`

### 6. 初始化示例 RAG 知识库

在项目根目录执行：

```bash
python -m rag.service
```

该命令会读取 `study_notes.md`，对文档进行分块和向量化，并写入本地 ChromaDB。

首次运行 Embedding 模型前，需要确保对应模型已经下载至本地缓存。

### 7. 运行自动化测试

```bash
python -m pytest -v
```

最近一次本地回归测试结果：

```text
28 passed in 10.86s
```

测试覆盖会话管理、API 接口、数据库操作、RAG 集成及评估等功能。

## 后续开发计划

- 支持多文档知识库导入与管理
- 提供文档上传、列表、删除 API
- 完善知识来源的历史持久化
- 改进 RAG 检索和评估流程
- 完善跨平台环境配置与部署
- 逐步引入 Docker 和 CI/CD