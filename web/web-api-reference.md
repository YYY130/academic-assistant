# SciFlow Web 前端 · 接口与接入文档

> **最后更新**: 2026-07-19 · **版本**: v3.0  
> **基础地址**: `http://localhost:5000`  
> **目标用户**: 需要接入此 Web 前端的其他 Agent 开发者

---

## 1. 架构概述

```
浏览器 (http://localhost:5000)
  │
  ├─ 静态页面: templates/index.html  (学术风 Chat UI，多会话隔离)
  │
  └─ API 后端: Flask (port 5000)
       │
       ├─ /api/chat → Gateway → sciflow-main Agent (主Agent)
       ├─ /api/sessions → web/sessions.json (会话管理)
       ├─ /api/messages/<id> → web/messages/<id>.json (消息持久化)
       └─ /api/knowledge → shared/knowledge_md/ (人类可读知识库)
```

**会话隔离原理**: 每个对话生成唯一 `session_id`，通过 OpenAI API 的 `user` 字段传递给 Gateway，Gateway 自动为不同 `user` 维护独立的会话上下文。

---

## 2. 快速启动

### 2.1 依赖安装

```bash
pip install flask flask-cors requests
```

### 2.2 启动

```bash
cd <项目根目录>/web
python3 server.py
```

输出：
```
🚀 SciFlow Web v3 | http://localhost:5000
```

### 2.3 验证

```bash
curl http://localhost:5000/api/health
```

正常返回：
```json
{"gateway":"connected","models":15,"status":"ok"}
```

### 2.4 生产环境建议

```bash
# 后台运行
nohup python3 web/server.py > /tmp/sciflow-web.log 2>&1 &

# 或者使用 gunicorn
pip install gunicorn
gunicorn -w 2 -b 0.0.0.0:5000 --chdir web server:app
```

---

## 3. 全部 API 接口

### 3.1 健康检查

**GET** `/api/health`

| 参数 | 无 |
|------|-----|

**响应** (200):
```json
{
  "status": "ok",
  "gateway": "connected",
  "models": 15
}
```

`gateway` 字段说明：
- `"connected"` — Gateway 可达，Agent 就绪
- `"disconnected"` — Gateway 不可达（需检查 Gateway 进程和端口）

---

### 3.2 聊天（核心接口）

**POST** `/api/chat`

**请求头**:
```
Content-Type: application/json
```

**请求体**:
```json
{
  "messages": [
    {"role": "user", "content": "帮我分析Transformer架构"},
    {"role": "assistant", "content": "..."},
    {"role": "user", "content": "再详细一点"}
  ],
  "session_id": "sess_b5da59c41b5b"
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `messages` | array | ✅ | 对话历史，每条含 `role` (`"user"`/`"assistant"`) 和 `content` |
| `session_id` | string | ✅ | 会话ID，同一会话传相同ID保持上下文连续 |

**响应**: Server-Sent Events (SSE) 流

```
data: {"content":"Transformer是"}

data: {"content":"一种..."}

: heartbeat

data: [DONE]
```

每条 `data:` 行是一个 JSON 对象，`content` 字段是增量文本。

**心跳**: 每15秒发一次 `: heartbeat` 注释行，防止连接超时。

**错误响应**:
```
data: {"error":"无法连接Gateway(port 18789)"}
data: {"error":"Gateway 401"}
```

**超时设置**: 连接超时 30 秒，读取超时 600 秒（10分钟）。

**上下文隔离**: 请求中的 `session_id` 作为 OpenAI API 的 `user` 参数传递给 Gateway。不同 `session_id` 在 Gateway 侧拥有独立的会话上下文。

---

### 3.3 会话管理

#### 3.3.1 列出所有会话

**GET** `/api/sessions`

**响应** (200):
```json
[
  {
    "id": "sess_b5da59c41b5b",
    "title": "帮我查一些ue5相关论文",
    "created": "16:21",
    "updated": "16:28",
    "message_count": 8
  },
  {
    "id": "sess_42218924e719",
    "title": "新对话",
    "created": "16:21",
    "updated": "16:21",
    "message_count": 0
  }
]
```

按创建时间倒序排列。

#### 3.3.2 创建新会话

**POST** `/api/sessions`

| 参数 | 无 |
|------|-----|

**响应** (200):
```json
{"id": "sess_a1b2c3d4e5f6"}
```

新会话初始标题为"新对话"，消息数为 0。创建后自动插入列表顶部。

#### 3.3.3 删除会话

**DELETE** `/api/sessions/{session_id}`

**响应** (200):
```json
{"ok": true}
```

同时删除对应的消息文件 `web/messages/{session_id}.json`。

---

### 3.4 消息管理

#### 3.4.1 读取消息

**GET** `/api/messages/{session_id}`

**响应** (200):
```json
[
  {"role": "user", "content": "帮我查一些ue5相关论文"},
  {"role": "assistant", "content": "🔄 [工作流] 正在分析你的需求..."}
]
```

返回格式与 `/api/chat` 的 `messages` 字段一致。空会话返回 `[]`。

#### 3.4.2 保存消息

**POST** `/api/messages/{session_id}`

**请求体**:
```json
{
  "messages": [
    {"role": "user", "content": "帮我查一些ue5相关论文"},
    {"role": "assistant", "content": "🔄 [工作流] 正在分析..."}
  ]
}
```

**响应** (200):
```json
{"ok": true}
```

保存后自动更新会话的 `message_count`、`updated` 字段。如果会话标题仍为"新对话"，自动取第一条用户消息的前30字作为新标题。

---

### 3.5 知识库

#### 3.5.1 列出知识文档

**GET** `/api/knowledge`

**响应** (200):
```json
[
  {
    "name": "检索增强生成：让大模型先查再答",
    "path": "检索增强生成：让大模型先查再答.md",
    "size": 531,
    "updated": "07-19 16:23"
  },
  {
    "name": "Transformer奠基之作",
    "path": "Transformer奠基之作.md",
    "size": 424,
    "updated": "07-19 15:58"
  }
]
```

递归扫描 `shared/knowledge_md/` 目录下所有 `.md` 文件，按修改时间倒序。

`size` 单位为字节。

#### 3.5.2 阅读知识文档

**GET** `/api/knowledge/{文件名}`

例如：`GET /api/knowledge/Transformer奠基之作.md`

**响应** (200):
```json
{
  "name": "Transformer奠基之作",
  "content": "# Attention Is All You Need\n\n> **入库时间**: 2026-07-19 16:23\n..."
}
```

`content` 字段为 Markdown 格式的完整文档内容。

---

## 4. 前端页面说明

### 4.1 页面结构

```
┌─────────────┬──────────────────────────────────┐
│  侧边栏 (260px)│       聊天区                      │
│             │                                  │
│  🎓 对话列表  │  SciFlow 智研协同 · 学术助手       │
│             │                                  │
│  ＋ 新建对话  │  用户消息 ...                      │
│  📚 知识库   │  工作流状态条 ...                   │
│             │  Agent回复 ...                     │
│  对话1       │                                  │
│  对话2       │  ────────────────────────────     │
│  对话3       │  [文本输入框]          [发送]       │
└─────────────┴──────────────────────────────────┘
```

### 4.2 工作流状态展示

Agent 回复中以 `🔄 [工作流]` / `✅ [工作流]` 开头的行会自动渲染为状态指示器：

- `🔄` — 蓝色左边框 + 脉冲动画（进行中）
- `✅` / `❌` / `⚠️` — 绿色/红色/黄色左边框（已完成/失败/警告）

无需前端额外处理，Agent 在回复中按格式输出即可。

### 4.3 多会话行为

| 行为 | 说明 |
|------|------|
| 新建对话 | 点击"＋ 新建对话"，创建全新空会话 |
| 切换对话 | 点击左侧对话列表项，加载该会话的历史消息 |
| 删除对话 | 悬停对话项，点击右侧"×"按钮 |
| 上下文隔离 | 不同 `session_id` 在 Gateway 侧拥有独立会话 |

---

## 5. 配置项

所有配置在 `web/server.py` 文件头部：

```python
GATEWAY_PORT = 18789          # OpenClaw Gateway 端口
GATEWAY_BASE = f"http://127.0.0.1:{GATEWAY_PORT}"
TARGET_AGENT = "openclaw"     # 目标 Agent，默认="openclaw"(路由到default agent)
```

### 5.1 修改目标 Agent

```python
# 改为特定 Agent
TARGET_AGENT = "openclaw/sciflow-main"

# 或保持 "openclaw" 让 Gateway 路由到默认 Agent
TARGET_AGENT = "openclaw"
```

### 5.2 修改端口

```python
# server.py 最后一行的端口
app.run(host="0.0.0.0", port=5000, debug=False)

# Gateway 端口
GATEWAY_PORT = 18789
```

### 5.3 Gateway Token

自动从 `~/.openclaw/openclaw.json` 读取，无需手动配置。

如果 Gateway 在其他机器上，手动设置：
```python
GATEWAY_TOKEN = "你的token"
GATEWAY_BASE = "http://远程IP:18789"
```

---

## 6. 数据存储位置

### 6.1 文件结构

```
web/
├── server.py              ← Flask 后端
├── sessions.json          ← 会话索引（JSON）
├── messages/              ← 消息存储目录
│   ├── sess_xxx.json      ← 每个会话一个文件
│   └── sess_yyy.json
├── templates/
│   └── index.html         ← 前端页面（单文件）
└── static/                ← 静态资源（预留）
```

### 6.2 sessions.json 格式

```json
{
  "sessions": {
    "sess_b5da59c41b5b": {
      "id": "sess_b5da59c41b5b",
      "title": "帮我查一些ue5相关论文",
      "created": "16:21",
      "updated": "16:28",
      "message_count": 8
    }
  },
  "order": ["sess_b5da59c41b5b", "sess_42218924e719"]
}
```

### 6.3 消息文件格式

```json
[
  {"role": "user", "content": "帮我查一些论文"},
  {"role": "assistant", "content": "🔄 [工作流] 正在分析需求..."},
  {"role": "assistant", "content": "找到以下论文..."}
]
```

### 6.4 Windows 路径

```
C:\Users\yuyue\Desktop\作业之类的\龙虾实训\结项作业\academic-assistant\web\
```

---

## 7. Session ID 生成规则

Session ID 格式：`sess_{12位随机hex}`

由 `uuid.uuid4().hex[:12]` 生成，例如 `sess_b5da59c41b5b`。

前端在新建会话时调用 `POST /api/sessions` 获取 ID，后续所有请求携带该 ID。

---

## 8. 错误处理

| HTTP 状态码 | 场景 |
|------------|------|
| 200 | 正常 |
| 400 | 请求缺少 `messages` 字段 |
| 404 | 知识文档不存在 或 路由未找到 |
| SSE `error` | Gateway 不可达、认证失败、超时 |

SSE 错误消息示例：
```
data: {"error":"无法连接Gateway(port 18789)"}
data: {"error":"Gateway 401"}
```

---

## 9. 集成检查清单

对接此 Web 前端前，确认以下条件：

- [ ] OpenClaw Gateway 正在运行（`openclaw status` 确认）
- [ ] Gateway 配置了目标 Agent（`agents.list` 中有 `sciflow-main` 等）
- [ ] DeepSeek API Key 已配置
- [ ] Flask 依赖已安装：`flask`, `flask-cors`, `requests`
- [ ] 端口 5000 未被占用
- [ ] `web/server.py` 中 `GATEWAY_PORT` 与 Gateway 实际端口一致
- [ ] 如果是远程 Gateway，`GATEWAY_TOKEN` 和 `GATEWAY_BASE` 已修改

---

## 10. 给协作者的一句话说明

> 前端是一个 Flask 应用，监听 `http://localhost:5000`。用户在浏览器打开这个地址就能看到多会话聊天界面。后端通过 `/api/chat` 把消息转发给 OpenClaw Gateway 的目标 Agent。前端负责多会话隔离（每个会话独立 `session_id`）、消息持久化（存 JSON 文件到 `web/messages/`）、以及知识库浏览（读 `shared/knowledge_md/` 下的 Markdown 文件）。启动只需要 `python3 web/server.py`。
