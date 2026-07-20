# SciFlow 学术科研助手 — 开发文档

## 项目概述

基于 OpenClaw 多智能体框架的「一主三翼双库」学术科研助手系统。一期聚焦**文献精读链路**（检索→略读→精读→分析→知识入库）。

## 目录结构

```
科研助手/
├── AGENTS.md                          # 项目级 Agent 规范
├── README.md                          # 本文档
│
├── agents/                            # 7个 Agent 配置
│   ├── 主Agent/                       # 科研助手主Agent（全局中枢）
│   │   ├── SOUL.md                    #   人设、职责、I/O接口
│   │   ├── AGENTS.md                  #   行为规范、调度协议
│   │   └── MEMORY.md                  #   长期记忆
│   │
│   ├── 阅读编排器/                    # 文献精读链路调度中枢
│   │   ├── SOUL.md                    #   双模式调度（全链路/直通精读）
│   │   ├── AGENTS.md                  #   模式判断、并行精读调度
│   │   ├── MEMORY.md
│   │   └── WORKFLOW.md                #   5阶段流程编排
│   │
│   ├── 搜索Agent/                     # arXiv 文献检索
│   │   ├── SOUL.md
│   │   ├── AGENTS.md
│   │   └── MEMORY.md
│   │
│   ├── 略读Agent/                     # 相关性初筛、价值分层
│   │   ├── SOUL.md
│   │   ├── AGENTS.md
│   │   └── MEMORY.md
│   │
│   ├── 精读Agent/                     # 单篇深度解析（单定义多实例）
│   │   ├── SOUL.md                    #   并行机制说明
│   │   ├── AGENTS.md                  #   Skill调度顺序
│   │   └── MEMORY.md
│   │
│   ├── 分析Agent/                     # 多篇聚合对比
│   │   ├── SOUL.md
│   │   ├── AGENTS.md
│   │   └── MEMORY.md
│   │
│   └── 知识关联Agent/                 # 向量化、索引、入库
│       ├── SOUL.md
│       ├── AGENTS.md
│       └── MEMORY.md
│
├── skills/                            # 5个 Skill
│   ├── SKILL_PLAN.md                  #   需求规划文档
│   ├── paper-structure-parser.md      #   结构解析Skill（精读Agent）
│   ├── paper-difficulty-interpreter.md#   难点解读Skill（精读Agent）
│   ├── paper-critical-analyst.md      #   批判分析Skill（精读Agent）
│   ├── knowledge-indexer.md           #   知识入库Skill（知识关联Agent）
│   └── knowledge-indexer/
│       └── scripts/
│           └── index_knowledge.py     #   入库脚本（Embedding+FAISS+JSON+MD）
│
├── data/                              # 运行时数据（按需创建）
│   ├── vector_db/                     #   FAISS 向量索引
│   │   ├── index.faiss
│   │   └── id_map.json
│   └── knowledge_index.json           #   结构化元数据索引
│
└── knowledge/                         # 用户共享文件夹
    ├── <论文标题> - 精读笔记.md        #   单篇精读笔记（人可读）
    └── INDEX.md                       #   全局目录（按年份分组）
```

## Agent 注册信息

| Agent ID | 名称 | 模型 | Skills | 可调度下级 |
|----------|------|------|--------|-----------|
| `sciflow-main` | 科研助手主Agent | pro | - | reader, writer, recommend |
| `sciflow-reader` | 阅读编排器 | pro | - | search, skim, deepread, analyze, knowledge |
| `sciflow-search` | 搜索Agent | flash | arxiv-paper-searcher | - |
| `sciflow-skim` | 略读Agent | flash | - | - |
| `sciflow-deepread` | 精读Agent | pro | paper-structure-parser, paper-difficulty-interpreter, paper-critical-analyst | - |
| `sciflow-analyze` | 分析Agent | pro | - | - |
| `sciflow-knowledge` | 知识关联Agent | flash | knowledge-indexer | - |

> 注：`sciflow-writer`（写作协作Agent）、`sciflow-recommend`（个性化推荐Agent）为二期预留，暂未开发。

## 阅读编排器双模式

| 模式 | 触发条件 | 流程 |
|------|---------|------|
| 全链路 | payload 含 `query` | 搜索 → 略读 → 精读(并行) → 分析 → 入库 |
| 直通精读 | payload 含 `papers` | 精读(并行) → (可选)分析 → (可选)入库 |

## 并行精读机制

- `sciflow-deepread` 为单Agent定义，不创建多个固定Agent
- 需要并行处理N篇论文时，编排器 spawn N个临时实例
- 单次并行上限：**5个实例**（全局 maxConcurrent=8，预留3个给系统）
- 每个实例在独立 session 中运行，处理单一论文

## Skill 来源总览

| Skill | 归属Agent | 来源 | 类型 |
|-------|-----------|------|------|
| `arxiv-paper-searcher` | 搜索Agent | ClawHub 商店 (songxf1024, v1.0.2) | Python脚本 |
| `paper-structure-parser` | 精读Agent | 自研 | Prompt工程 |
| `paper-difficulty-interpreter` | 精读Agent | 自研 | Prompt工程 |
| `paper-critical-analyst` | 精读Agent | 自研 | Prompt工程 |
| `knowledge-indexer` | 知识关联Agent | 自研 | Python脚本 |

## 存储架构

### 与 OpenClaw 主系统隔离

| 组件 | OpenClaw 主系统 | SciFlow |
|------|----------------|---------|
| 向量库 | `openclaw-agent.sqlite` | `data/vector_db/index.faiss` |
| Embedding 模型 | nomic-embed-text (Ollama) | nomic-embed-text (Ollama，复用模型) |
| 用途 | CJLAI助理 Memory 语义搜索 | 论文内容语义检索 |

### 三层存储设计

1. **向量层** `data/vector_db/`：FAISS 索引 + ID映射，Agent 语义检索用
2. **索引层** `data/knowledge_index.json`：结构化元数据（papers/tags/profile），Agent 过滤查询用
3. **展示层** `knowledge/`：md 精读笔记 + INDEX.md 目录，用户/团队直接阅读

## 依赖清单

```bash
pip install faiss-cpu numpy requests --break-system-packages
```

运行时依赖：
- Ollama (本地 127.0.0.1:11434) + nomic-embed-text 模型
- arXiv API（由 arxiv-paper-searcher Skill 自动调用）
- OpenClaw Gateway（Agent 调度）

## 开发进度

| 模块 | 状态 | 备注 |
|------|------|------|
| 项目文档（SRS + 架构设计） | ✅ | temp/ 下两份源文档 |
| Agent SOUL/AGENTS/MEMORY | ✅ | 7个Agent全部完成 |
| 精读Agent 3项Skill | ✅ | 结构解析/难点解读/批判分析 |
| 搜索Agent Skill | ✅ | arxiv-paper-searcher (商店安装) |
| 知识关联Agent Skill | ✅ | knowledge-indexer (自研+测试通过) |
| 并行精读机制 | ✅ | 单定义多实例，上限5 |
| Agent 注册配置 | ✅ | openclaw.json agents.list |
| 全链路联调 | ⬜ | 待测试 |
| 写作协作链路（二期） | ⬜ | sciflow-writer |
| 知识增值链路（二期） | ⬜ | sciflow-recommend |
