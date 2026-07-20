# AGENTS.md - SciFlow 学术科研助手项目规范

本项目基于 OpenClaw 多智能体框架构建，采用「一主三翼双库」架构。

## 架构概览
- **一主**：科研助手主Agent（全局中枢，需求拆解/任务调度/结果审核）
- **三翼**：文献精读链路 / 论文写作链路 / 知识增值链路
- **双库**：库A（持久化个人知识库）+ 库B（任务级临时工作库）

## 当前开发阶段
一期聚焦**文献精读链路**（检索→略读→精读→分析→知识入库），完成后打通知识库核心输入入口。

## Agent 清单
| Agent | 层级 | 职责 |
|-------|------|------|
| 科研助手主Agent | 全局中枢 | 需求理解、任务调度、结果整合 |
| 阅读编排器Agent | 文献链路-调度层 | 编排搜索→略读→精读→分析→入库全流程 |
| 搜索Agent | 文献链路-执行层 | 多源学术检索、去重、元数据标准化 |
| 略读Agent | 文献链路-执行层 | 相关性初筛、价值分层 |
| 精读Agent | 文献链路-执行层 | 单篇深度解析，调度3项Skill |
| 分析Agent | 文献链路-执行层 | 多篇聚合对比、综述素材生成 |
| 知识关联Agent | 文献链路-执行层 | 知识标准化、向量化、入库持久化 |

## 并行精读机制
精读Agent（`sciflow-deepread`）为**单Agent定义**，不预先创建多个固定Agent。当需要并行处理N篇论文时，编排器 spawn N个同类型临时实例：
```
sessions_spawn(agentId="sciflow-deepread", task="精读论文A", mode="run")
sessions_spawn(agentId="sciflow-deepread", task="精读论文B", mode="run")
```
每个实例独立运行，处理单一论文，互不干扰。

## Agent 间通信
- 科研助手主Agent → 阅读编排器：`sessions_spawn` 启动子任务
- 阅读编排器 → 下辖执行Agent：`sessions_spawn` 顺序/并行调度
- 执行Agent → 编排器：完成回执通过 session 返回
- 消息格式：统一 JSON，含 `task_id / action / payload / status`

## 开发顺序
1. SOUL.md + 接口规范（本文档）
2. Skill 具体实现（结构解析/难点解读/批判分析）
3. Agent 配置注册 + 联调
4. 全链路联调测试

## 注意事项
- 科研助手主Agent 与当前工作区主Agent（CJLAI助理）是两个独立实体，互不混淆
- 所有 Agent 均部署在 WSL2 本地环境
- Skill 以 OpenClaw Skill 插件形式开发，由对应 Agent 按需调用
