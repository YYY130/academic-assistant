# 🧪 智能学术助手 — OpenClaw 多智能体系统

> **"读论文 → 推荐 → 写作，全链路由独立AI智能体协作完成。"**

## 🧠 架构总览

```
用户
   │
   ▼
┌─────────────────────────────────────────────┐
│           主 Agent                          │
│   学术助手总调度                            │
│   model: deepseek/deepseek-v4-pro            │
└──────┬──────────────────────┬───────────────┘
       │                      │
       ▼                      ▼
┌──────────────┐    ┌──────────────────┐   ┌──────────────┐
│ 阅读编排器    │    │ 个性化推荐Agent   │   │   写作Agent   │
│ 管线总指挥    │    │ 选书师·懂你的兴趣 │   │ 执笔人·数据→论文│
│ flash        │    │ flash            │   │ pro           │
└──────┬───────┘    └────────┬─────────┘   └──────┬───────┘
       │                     │                    │
       ▼                     ▼                    ▼
  ┌──────────┐          ┌────────┐          ┌────────┐
  │ 搜索Agent │          │ DB A   │          │ DB B   │
  │ 侦察兵    │          │ 向量    │          │ 实验    │
  │ flash    │          │ 知识库  │          │ 数据库  │
  └────┬─────┘          │ (持久)  │          │(任务级) │
       ▼                └────────┘          └────────┘
  ┌──────────┐
  │ 略读Agent │
  │ 过滤器    │
  │ flash    │
  └────┬─────┘
       ▼
  ┌──────────┐
  │ 精读Agent │← 可并行多个实例
  │ 深度读者   │
  │ flash    │
  └────┬─────┘
       │
       ├──────────────┐
       ▼               ▼
  ┌──────────┐    ┌──────────┐
  │ 分析Agent │    │ 关联Agent │
  │ 综合分析   │    │ 入库归档   │
  │ flash    │    │ flash    │
  └────┬─────┘    └────┬─────┘
       │               │
       └──→ 结果汇总到编排器 → 主Agent → 用户
```

## 🤖 9个OpenClaw AI智能体

| Agent | 身份 | 模型 | 核心能力 |
|-------|------|------|---------|
| **main_agent** | 学术研究助手 | Pro | 用户交互、意图识别、全局调度 |
| **reading_orchestrator** | 阅读编排器 | Flash | 管线调度、并发控制、质量审查 |
| **search_agent** | 搜索Agent侦察兵 | Flash | 多渠道论文搜索（arXiv/S2/Web） |
| **skim_agent** | 略读Agent过滤器 | Flash | 快速筛选、相关性评估 |
| **deep_read_agent** | 精读Agent深度读者 | Flash | 深度解析、结构化笔记 |
| **analysis_agent** | 分析Agent | Flash | 综合多篇论文、提炼洞察 |
| **association_agent** | 关联Agent档案员 | Flash | 结构化入库DB A |
| **personalized_recommender** | 个性化推荐Agent选书师 | Flash | 画像×知识库、智能推荐 |
| **writing_agent** | 写作Agent执笔人 | Pro | 数据→论文、学术写作 |

## 🗄️ 双数据库设计

| | DB A（向量知识库） | DB B（实验数据库） |
|:--|:--|:--|
| **存储内容** | 论文知识、关联关系 | 实验数据、分析结果 |
| **生命周期** | 跨任务持久保存 | 任务级，用完即弃 |
| **访问者** | 主Agent、推荐Agent、关联Agent | 写作Agent |
| **索引方式** | 小模型向量化（all-MiniLM-L6-v2） | 结构化文件存储 |
| **持久化路径** | `shared/db_a/` | `shared/db_b/` |

## 📡 Agent间通信机制

Agent之间通过 OpenClaw 内置工具通信：

```
sessions_spawn    → 创建子Agent执行任务（主→子）
sessions_send     → 发送消息给其他Agent Session
sessions_history  → 查看子Agent的执行结果
memory_search     → 搜索记忆（跨会话）
```

### 阅读管线通信流程

```
main_agent
  └─ sessions_spawn → reading_orchestrator
       ├─ sessions_spawn → search_agent
       ├─ sessions_spawn → skim_agent
       ├─ sessions_spawn → deep_read_agent (×N并行)
       ├─ sessions_spawn → analysis_agent (并行)
       └─ sessions_spawn → association_agent (并行)
```

## 🚀 快速使用

### 1. 部署到 OpenClaw

将 `config/openclaw.agents.json` 中的配置合并到你的 `openclaw.json` 中，重启Gateway：

```bash
openclaw gateway restart
```

### 2. 与主Agent对话

在各通道（WebChat/Discord/Telegram等）直接与主Agent对话：

> "帮我查一下transformer注意力机制的最新论文"
> → 自动调度阅读管线 → 返回阅读报告

> "推荐几篇NLP方向的论文"
> → 推荐Agent查知识库 → 返回推荐列表

> "根据实验数据写一篇论文"
> → 写作Agent查DB B → 返回论文草稿

### 3. 演示数据入库

```bash
python shared/scripts/store_to_db_a.py --action list
```

## 📂 项目结构

```
academic-assistant/
├── agents-workspace/          # 9个AI智能体的工作区
│   ├── main_agent/            # 主Agent
│   ├── reading_orchestrator/  # 阅读编排器
│   ├── search_agent/          # 搜索Agent
│   ├── skim_agent/            # 略读Agent
│   ├── deep_read_agent/       # 精读Agent
│   ├── analysis_agent/        # 分析Agent
│   ├── association_agent/     # 关联Agent
│   ├── personalized_recommender/ # 个性化推荐Agent
│   └── writing_agent/         # 写作Agent
│       └── {SOUL.md, AGENTS.md, TOOLS.md, MEMORY.md}
├── shared/
│   ├── db_a/                  # DB A 向量知识库持久化
│   ├── db_b/                  # DB B 实验数据库
│   └── scripts/               # Agent可调用的共享脚本
│       ├── store_to_db_a.py   # DB A 入库
│       └── query_db_a.py      # DB A 查询
├── config/
│   ├── openclaw.agents.json   # OpenClaw多Agent配置
│   ├── default.yaml           # 默认配置
│   ├── agent_config.yaml      # Agent参数
│   └── database.yaml          # 数据库配置
└── README.md
```

## 💡 设计要点

1. **每个Agent都是真AI** — 不是代码逻辑模拟，是OpenClaw平台上活生生的智能体，有自己的灵魂和规则
2. **子Agent spawn模式** — 主Agent通过 `sessions_spawn` 创建子任务，天然支持并行（多篇论文同时精读）
3. **记忆 vs 无状态** — 主Agent、推荐Agent、写作Agent有持久记忆（MEMORY.md）；管道Agent（搜索/略读/精读/分析/关联）每次跑新任务，不保留历史
4. **双库分离** — DB A存知识沉淀（论文精华），DB B存过程数据（实验结果），生命周期不同
5. **最小依赖** — 只需要 OpenClaw + 各Agent配置的模型，无需额外基础设施
