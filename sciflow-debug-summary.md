# SciFlow 多Agent项目 —— 子Agent超时问题 完整排查与修复报告

> **日期**：2026-07-19  
> **项目**：academic-assistant（基于 OpenClaw 2026.7.1-beta.5）  
> **环境**：Windows 11 + WSL2 Ubuntu-24.04，Gateway 运行在 WSL 内，Flask web 前端在端口 5000

---

## 故障现象

- `sciflow-main`（主Agent，default agent）可以正常回复用户
- 任何对子Agent（`sciflow-reader`、`sciflow-search` 等）的调用均失败
- 表现为主Agent返回 "已派发任务，等待中..." 后永远收不到结果
- 子Agent session 要么超时被 kill，要么静默完成但结果丢失

---

## 根因分析（共发现 4 个问题）

### 🔴 问题 1：`tools.agentToAgent.allow` 白名单缺失

**文件**：`~/.openclaw/openclaw.json`

OpenClaw Gateway 有一个全局的 agent 间通信白名单 `tools.agentToAgent.allow`。修复前只允许 3 个 agent：

```json
"agentToAgent": {
  "enabled": true,
  "allow": ["search", "writer", "bot-a"]
}
```

所有 `sciflow-*` agent 均不在列表中，导致：
- `sessions_send` 返回 `"Agent-to-agent messaging denied by tools.agentToAgent.allow."`
- `sessions_history` 返回 `"Agent-to-agent history denied by tools.agentToAgent.allow."`

**修复**：将所有 9 个 sciflow agent 加入白名单。

---

### 🔴 问题 2：子Agent 缺少 DeepSeek API 认证配置

**目录**：`~/.openclaw/agents/sciflow-*/agent/`

OpenClaw 的非 default agent 不会从环境变量 fallback 获取 API key。每个 agent 需要自己的 `agent/models.json` 和 `agent/plugins/` 来配置模型认证。

修复前状态：
- `sciflow-main`：✅ 有 `models.json` + `plugins/deepseek/`
- 其余 8 个子Agent：❌ `agent/` 目录为空

子Agent 无法调用 DeepSeek API → LLM 调用失败 → 超时。

**修复**：从 `sciflow-main` 复制 `models.json` 和 `plugins/` 到所有 8 个子Agent。

---

### 🔴 问题 3：TOOLS.md 中 Agent ID 全部写错（最关键！）

**文件**：`agents-workspace/reading_orchestrator/TOOLS.md`

阅读编排器的工具文档中，子Agent ID 与实际注册的完全不匹配：

| TOOLS.md 写的（❌ 错误） | 实际注册的 Agent ID（✅ 正确） |
|---|---|
| `search_agent` | `sciflow-search` |
| `skim_agent` | `sciflow-skim` |
| `deep_read_agent` | `sciflow-deepread` |
| `analysis_agent` | `sciflow-analyze` |
| `association_agent` | `sciflow-knowledge` |

LLM 读到 `TOOLS.md` 中的错误 ID，`sessions_spawn(agentId="search_agent")` → 返回 `"agentId is not allowed"` → 流水线中断 → 超时。

**为什么 `sciflow-main` 有时也出问题**：SOUL.md 中写的是 "阅读编排器"，LLM 会把中文翻译回英文 `reading_orchestrator`，而不是使用正确的 `sciflow-reader`。从实际 session 日志中观察到的错误：

```json
{
  "status": "forbidden",
  "error": "agentId is not allowed for sessions_spawn (allowed: sciflow-reader, ...)",
  "role": "reading_orchestrator"
}
```

**修复**：
- `reading_orchestrator/TOOLS.md`：全部改为正确的 agent ID
- `reading_orchestrator/SOUL.md`：所有引用处附上精确 agent ID
- `reading_orchestrator/AGENTS.md`：流程步骤中使用精确 ID，末尾加禁止使用错误名称的警告
- `main_agent/SOUL.md`：所有引用处附上精确 agent ID
- `main_agent/AGENTS.md`：表格中标注"精确agentId"，加禁止自行翻译的警告

---

### 🔴 问题 4：`runTimeoutSeconds` 过短 + auto-announce 推送不可靠

#### 4a. 超时预算不足

**文件**：`~/.openclaw/openclaw.json` → `agents.defaults.subagents.runTimeoutSeconds`

修复前：**120 秒（2分钟）**

阅读流水线需要：web_search（多源检索）→ web_fetch（抓取论文）→ LLM 精读分析 → 写文件。2 分钟远不够。从 session 轨迹中可见：

| Session | 结果 | 原因 |
|---|---|---|
| `30d6933b` | ❌ aborted | `timedOutByRunBudget: True` |
| `6a69a799` | ❌ aborted | `timedOutByRunBudget: True` |
| `95718ef5` | ❌ aborted | `timedOutByRunBudget: True` |

**修复**：`runTimeoutSeconds: 120 → 600`（10分钟）

#### 4b. auto-announce 推送不可靠（导致"子Agent完成了但结果丢了"）

OpenClaw 使用 push-based auto-announce 机制：子Agent 完成后，系统自动推送一个通知到父Agent 的 session。但实际测试发现：

- **`sessions_yield` 只推送第一个完成的子任务通知**
- 并行启动的 N 个 `sciflow-deepread` 实例中，只有第一个完成时会触发通知
- 后续完成的实例静默完成，不触发新通知
- 编排器如果"数通知=数完成"，会误判还有任务未完成，陷入空等待
- 主Agent 如果只等 auto-announce 推送而不主动拉取，同理收不到结果

**修复（双保险机制）**：

```
记录所有 childSessionKey → []

while 没收齐全部结果:
    sessions_yield()            ← ① push：等一个通知（至少触发事件）
    for each childSessionKey:   ← ② pull：主动逐个拉
        result = sessions_history(childSessionKey)
        if result 非空且有完整输出:
            标记该 child 为"已完成"
        elif result 包含 error:
            标记该 child 为"失败"
    → 全部标记 → 退出循环，进入下一阶段
    → 没收齐 → 继续循环
```

**核心原则**：
- 不数通知数量来判断完成
- 每个 child 都要用 `sessions_history` 主动拉取一次
- push 负责保底，pull 负责确认

**涉及文件**：
- `reading_orchestrator/WORKFLOW.md`：新增完整的"双保险收结果机制"章节
- `reading_orchestrator/AGENTS.md`：并行精读调度改为双保险模式
- `main_agent/AGENTS.md`：spawn 后改为主动轮询 `sessions_history`，不依赖 auto-announce
- `main_agent/SOUL.md`：输出接口新增主动拉取的说明

---

## 修改文件清单

### OpenClaw 全局配置（WSL 内）

| 文件 | 改动 |
|---|---|
| `~/.openclaw/openclaw.json` | ① `tools.agentToAgent.allow` 增加 9 个 sciflow agent ② `agents.defaults.subagents.runTimeoutSeconds`: 120→600 |
| `~/.openclaw/agents/sciflow-{reader,search,skim,deepread,analyze,knowledge,recommend,writer}/agent/models.json` | 新建，从 sciflow-main 复制 |
| `~/.openclaw/agents/sciflow-{同上}/agent/plugins/` | 新建，从 sciflow-main 复制 |

### 项目工作台文件（Windows 侧，通过 /mnt/c/ 挂载）

| 文件 | 改动 |
|---|---|
| `agents-workspace/reading_orchestrator/TOOLS.md` | 修正全部 5 个 agent ID |
| `agents-workspace/reading_orchestrator/SOUL.md` | 所有引用处附上精确 agent ID |
| `agents-workspace/reading_orchestrator/AGENTS.md` | ① 精确 agent ID ② 双保险收结果机制 ③ 每步 spawn 后主动拉取 |
| `agents-workspace/reading_orchestrator/WORKFLOW.md` | 新增"并行结果收集：双保险机制"章节（含伪代码） |
| `agents-workspace/main_agent/SOUL.md` | ① 精确 agent ID ② 结果收集机制说明 |
| `agents-workspace/main_agent/AGENTS.md` | ① 精确 agent ID ② spawn 后主动轮询模式 ③ 禁止依赖 auto-announce |

---

## 架构经验总结

### 1. Agent ID 命名一致性

在 OpenClaw 多Agent 系统中，Agent ID 是关键的"API 契约"。工作台文档（SOUL.md、AGENTS.md、TOOLS.md）中的 Agent ID 必须与 `openclaw.json` 中注册的 `id` 字段完全一致。LLM 不会自动做模糊匹配——`search_agent` 和 `sciflow-search` 在 LLM 看来是两个不同的工具调用。

**建议**：在工作台文档中始终使用 `agentId`（精确值）而非中文名称，或两者并列（如 `sciflow-reader（阅读编排器）`）。

### 2. OpenClaw 非 default agent 的认证

非 default agent 不会 fallback 到环境变量 `DEEPSEEK_API_KEY`。每个 agent 必须有自己的 `agent/models.json`（或 SQLite auth store）。创建新 agent 后要检查其 `agent/` 目录是否包含必要的认证配置。

### 3. OpenClaw 的 push-based 通知不可靠

`sessions_yield` 和 auto-announce 只推送第一个完成的通知。**永远不要**依赖通知数量来判断子任务完成情况。正确做法是：

- push（yield等通知）+ pull（sessions_history主动拉）双保险
- 遍历所有 `childSessionKey`，逐个确认完成
- 循环直到全部收齐

### 4. 子Agent 超时预算

阅读流水线（搜索→略读→精读→分析→入库）涉及多次 web 请求和 LLM 推理，`runTimeoutSeconds` 至少应设为 300-600 秒。默认的 120 秒仅适用于简单的单步任务。
