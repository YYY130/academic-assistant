# 🧪 Academic Assistant — OpenClaw 多智能体学术助手

> *9 个 AI 智能体协作完成论文搜索、推荐与写作的完整学术研究助手。*

---

## ✨ 功能特性

- **多智能体流水线** — 9 个专用 AI 智能体分工协作
- **论文发现与分析** — 搜索 arXiv/Semantic Scholar，快速筛选、深度阅读、综合分析
- **个性化推荐** — 智能体学习你的研究兴趣，持续推荐相关论文
- **学术写作** — 基于实验数据自动生成论文草稿
- **双数据库** — 持久化向量知识库（DB A）+ 临时实验数据存储（DB B）
- **并行处理** — 多篇论文同时分析，互不阻塞

## 🧠 系统架构

```
┌─────────────────────────────────────────────────────┐
│                    用户界面                          │
│          (WebChat / Discord / Telegram / CLI)        │
└─────────────────────────┬───────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────┐
│                    主 Agent                          │
│          意图识别 · 任务调度 · 用户交互                │
│                  model: Pro                          │
└──────┬─────────────────────┬────────────────────────┘
       │                     │
       ▼                     ▼
┌──────────────┐   ┌───────────────┐   ┌────────────┐
│   阅读编排器   │   │  个性化推荐    │   │   写作Agent │
│   管线调度     │   │  兴趣推荐      │   │  数据→论文  │
│ model: Flash  │   │ model: Flash  │   │ model: Pro │
└──────┬───────┘   └───────┬───────┘   └─────┬──────┘
       │                    │                 │
       ▼                    ▼                 ▼
  ┌──────────┐       ┌────────┐       ┌────────┐
  │ 搜索Agent │       │  DB A  │       │  DB B  │
  │  论文搜索  │       │ 向量知识库│       │ 实验数据 │
  │ Flash    │       │ (持久化) │       │ (临时)  │
  └────┬─────┘       └────────┘       └────────┘
       ▼
  ┌──────────┐
  │ 略读Agent │
  │  快速筛选  │
  │ Flash    │
  └────┬─────┘
       ▼
  ┌──────────┐
  │ 精读Agent │← 可并行多个实例
  │  深度阅读  │
  │  Flash   │
  └────┬─────┘
       │
   ┌───┴────────┐
   ▼            ▼
┌────────┐ ┌──────────┐
│分析Agent│ │ 关联Agent │
│综合分析  │ │ 入库归档   │
│Flash   │ │ Flash    │
└────┬───┘ └────┬─────┘
     │          │
     └──→ 编排器汇总 → 主Agent → 用户
```

## 🤖 智能体一览

| Agent | 角色 | 模型 | 职责 |
|-------|------|-------|------|
| **main_agent** | 学术研究助手 | Pro | 意图识别、任务调度、用户交互 |
| **reading_orchestrator** | 阅读编排器 | Flash | 多阶段阅读管线调度、并发控制 |
| **search_agent** | 搜索 Agent | Flash | 多源论文搜索（arXiv, S2, Web） |
| **skim_agent** | 略读 Agent | Flash | 快速评估相关性、论文筛选 |
| **deep_read_agent** | 精读 Agent | Flash | 全文深度分析、结构化笔记 |
| **analysis_agent** | 分析 Agent | Flash | 跨论文综合、洞察提取 |
| **association_agent** | 关联 Agent | Flash | 结构化入库向量知识库（DB A） |
| **personalized_recommender** | 个性化推荐 Agent | Flash | 兴趣画像 × 知识库 → 推荐 |
| **writing_agent** | 写作 Agent | Pro | 数据驱动的学术论文生成 |

## 🗄️ 双数据库设计

| 维度 | DB A（向量知识库） | DB B（实验数据库） |
|------|-------------------|-------------------|
| **存储内容** | 论文知识、关联关系 | 实验数据、分析结果 |
| **生命周期** | 跨任务、持久化 | 单次任务、用完即弃 |
| **访问者** | 主 Agent、推荐 Agent、关联 Agent | 写作 Agent |
| **索引方式** | all-MiniLM-L6-v2（本地嵌入） | 结构化文件存储 |
| **路径** | `shared/db_a/` | `shared/db_b/` |

## 📡 智能体通信

基于 OpenClaw 内置工具：

| 工具 | 用途 |
|------|------|
| `sessions_spawn` | 创建子 Agent 执行子任务 |
| `sessions_send` | 跨 Agent 消息传递 |
| `sessions_history` | 查看子 Agent 执行结果 |
| `memory_search` | 跨会话记忆搜索 |

### 阅读管线流程

```
main_agent
  └─ spawn → reading_orchestrator
       ├─ spawn → search_agent
       ├─ spawn → skim_agent
       ├─ spawn → deep_read_agent (×N 并行)
       ├─ spawn → analysis_agent (并行)
       └─ spawn → association_agent (并行)
       └─ 结果汇总 → 编排器 → main_agent → 用户
```

## 🚀 快速开始

### 环境要求

- 已安装 [OpenClaw](https://github.com/openclaw/openclaw)
- 已配置 LLM 供应商 API Key（推荐 DeepSeek）

### 一键配置

```bash
python setup.py
```

脚本会自动：
- 查找你的 OpenClaw 配置文件
- 合并 9 个 Agent 定义到 `openclaw.json`
- 创建必要的数据目录
- 备份原有配置

> 使用 `python setup.py --dry-run` 可预览变更内容。
> 使用 `python setup.py --path /your/project/path` 指定项目路径。

### 手动安装

1. 将 `config/openclaw.agents.json` 合并到你的 OpenClaw 配置中
2. 重启网关：
   ```bash
   openclaw gateway restart
   ```

### 启动 Web 前端（WSL）

```bash
cd /mnt/c/Users/yuyue/Desktop/作业之类的/龙虾实训/结项作业/academic-assistant
python3 web/server.py
```

> 请先确保 OpenClaw 网关已启动（`openclaw gateway restart`）。
> Web 前端通过网关端口 `18789` 连接。
> 启动后在浏览器打开 **http://localhost:5000/** 即可访问。

### 使用示例

```
用户: "帮我查一下 transformer 注意力机制的最新论文"
  → 自动调度阅读管线 → 返回阅读报告

用户: "推荐几篇 NLP 方向的论文"
  → 推荐 Agent 查知识库 → 返回推荐列表

用户: "根据实验数据写一篇论文"
  → 写作 Agent 查 DB B → 返回论文草稿
```

### 快速测试

```bash
python shared/scripts/store_to_db_a.py --action list
```

## 📖 文档

| 文档 | 说明 |
|------|------|
| [API 文档](docs/API.md) | Web 前端所有 API 接口参考 |
| [系统架构图](docs/architecture.html) | 完整系统架构可视化（浏览器打开） |
| [已知问题清单](docs/known-issues.md) | 当前版本已知限制与 Bug |

## 📁 项目结构

```
academic-assistant/
├── agents-workspace/           # 9 个智能体的运行工作区
│   ├── main_agent/
│   ├── reading_orchestrator/
│   ├── search_agent/
│   ├── skim_agent/
│   ├── deep_read_agent/
│   ├── analysis_agent/
│   ├── association_agent/
│   ├── personalized_recommender/
│   └── writing_agent/
├── shared/
│   ├── db_a/                   # 向量知识库
│   ├── db_b/                   # 实验数据存储
│   └── scripts/                # 共享工具脚本
├── config/
│   ├── openclaw.agents.json    # Agent 配置
│   ├── agent_config.yaml       # Agent 参数
│   ├── database.yaml           # 数据库设置
│   └── default.yaml            # 默认配置
├── docs/                       # 文档
├── experiment/                 # 样例实验数据
├── references/                 # 参考文献
└── web/                        # Web 界面
```

## 💡 设计理念

1. **真正的 AI 智能体** — 每个 Agent 都是 OpenClaw 平台上真实的 LLM 实体，不是脚本模拟
2. **Spawn 并行模式** — 主 Agent 按需创建子 Agent，天然支持并发论文分析
3. **记忆分层** — 核心 Agent（主、推荐、写作）有持久记忆；管线 Agent 每次任务不保留历史
4. **数据分离** — 知识沉淀（DB A）与过程数据（DB B）生命周期不同，管理更高效
5. **最小依赖** — 仅需 OpenClaw 运行环境 + 配置好的 LLM 供应商，无需额外基础设施

## 📦 技术栈

- **平台:** [OpenClaw](https://github.com/openclaw/openclaw)
- **大模型:** DeepSeek V4 Pro / Flash
- **嵌入模型:** all-MiniLM-L6-v2（本地）
- **存储:** 文件型向量知识库、结构化文件
- **界面:** WebChat / Discord / Telegram / Web 前端
