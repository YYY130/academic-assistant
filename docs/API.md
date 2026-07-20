# API 文档

> Academic Assistant Web 前端 API 参考。
> 基础地址: `http://localhost:5000`

---

## 目录

- [会话管理](#会话管理)
- [消息管理](#消息管理)
- [对话接口](#对话接口)
- [知识库](#知识库)
- [知识图谱](#知识图谱)
- [健康检查](#健康检查)

---

## 会话管理

### 获取会话列表

```
GET /api/sessions
```

返回所有会话的列表。

**响应示例:**

```json
[
  {
    "id": "sess_abc123",
    "title": "transformer 注意力机制",
    "created": "09:15",
    "updated": "09:30",
    "message_count": 12
  }
]
```

### 创建新会话

```
POST /api/sessions
```

创建新的空会话。

**响应示例:**

```json
{
  "id": "sess_def456"
}
```

### 删除会话

```
DELETE /api/sessions/{session_id}
```

删除指定会话及其消息记录。

**参数:**

| 参数 | 类型 | 说明 |
|------|------|------|
| `session_id` | path | 会话 ID（如 `sess_abc123`） |

**响应示例:**

```json
{
  "ok": true
}
```

---

## 消息管理

### 获取会话消息

```
GET /api/messages/{session_id}
```

获取指定会话的全部消息记录。

**参数:**

| 参数 | 类型 | 说明 |
|------|------|------|
| `session_id` | path | 会话 ID |

**响应示例:**

```json
[
  {"role": "user", "content": "帮我查一下 transformer"},
  {"role": "assistant", "content": "好的，我来调度阅读管线..."}
]
```

### 保存消息

```
POST /api/messages/{session_id}
```

保存消息列表到指定会话。

**请求体:**

```json
{
  "messages": [
    {"role": "user", "content": "你好"},
    {"role": "assistant", "content": "你好！有什么可以帮助你的？"}
  ]
}
```

**响应示例:**

```json
{
  "ok": true
}
```

---

## 对话接口

### 发送对话消息（流式）

```
POST /api/chat
```

发送消息给 OpenClaw Gateway 并获取流式 SSE 响应。

**请求体:**

```json
{
  "messages": [
    {"role": "user", "content": "帮我查一下 transformer 注意力机制"}
  ],
  "session_id": "sess_abc123"
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `messages` | array | ✅ | OpenAI 格式的消息列表 |
| `session_id` | string | ❌ | 会话 ID，用于 Gateway 会话隔离 |

**响应格式（SSE）：**

```
data: {"content": "好的"}
data: {"content": "，我来"}
data: {"content": "调度阅读管线..."}
data: [DONE]
```

> 客户端使用 `EventSource` 或 `fetch` 逐行解析 `data:` 前缀的事件流。

---

## 知识库

### 获取知识库文件列表

```
GET /api/knowledge
```

返回 `shared/knowledge_md/` 目录下的所有 Markdown 文件。

**响应示例:**

```json
[
  {
    "name": "Transformer奠基之作",
    "path": "Transformer奠基之作.md",
    "size": 1234,
    "updated": "07-19 15:30"
  }
]
```

### 读取知识库文件

```
GET /api/knowledge/{filename}
```

读取指定知识库文件的完整内容。

**参数:**

| 参数 | 类型 | 说明 |
|------|------|------|
| `filename` | path | 文件名（含 `.md` 后缀） |

**响应示例:**

```json
{
  "name": "Transformer奠基之作",
  "content": "# Attention Is All You Need\n\n..."
}
```

---

## 知识图谱

### 获取知识图谱数据

```
GET /api/knowledge-graph
```

从向量知识库（DB A）构建关联图谱，返回力导向图格式数据。

**响应示例:**

```json
{
  "nodes": [
    {"id": "paper_001", "label": "Attention Is All You Need...", "type": "paper", "title": "...", "summary": "...", "topics": [...], "methods": [...]},
    {"id": "topic:Transformer", "label": "Transformer", "type": "topic"},
    {"id": "method:Attention", "label": "Attention", "type": "method"}
  ],
  "edges": [
    {"source": "paper_001", "target": "topic:Transformer", "relation": "belongs_to"},
    {"source": "paper_001", "target": "method:Attention", "relation": "uses"},
    {"source": "paper_001", "target": "paper_002", "relation": "related", "style": "dashed"}
  ]
}
```

**节点类型:**

| type | 说明 |
|------|------|
| `paper` | 论文节点，包含标题、摘要、主题、方法等 |
| `topic` | 主题节点（由论文的 `related_topics` 提取） |
| `method` | 方法节点（由论文的 `methods_used` 提取） |

**边类型:**

| relation | 样式 | 说明 |
|----------|------|------|
| `belongs_to` | 实线 | 论文属于某主题 |
| `uses` | 实线 | 论文使用了某方法 |
| `related` | 虚线 | 两篇论文因共享主题/方法产生关联 |

---

## 健康检查

### 检查服务状态

```
GET /api/health
```

检查 Web 前端与 OpenClaw Gateway 的连接状态。

**响应示例（已连接 Gateway）:**

```json
{
  "status": "ok",
  "gateway": "connected",
  "models": 3
}
```

**响应示例（Gateway 未启动）:**

```json
{
  "status": "ok",
  "gateway": "disconnected"
}
```

> Web 前端本身总是返回 `"status": "ok"`，`gateway` 字段表示与 OpenClaw 网关的连接状态。
