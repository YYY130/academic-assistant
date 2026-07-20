# SciFlow Web 接入 OpenClaw 多Agent 配置完成

## ✅ 已完成

### 1. openclaw.json 已更新
- ✅ `gateway.http.endpoints.chatCompletions.enabled = true`
- ✅ 9个 SciFlow Agent 已部署到 `agents.list`
- ✅ 主Agent可调度子Agent（allowAgents 已配置）

### 2. Web 后端已改造
- ✅ Flask server.py → 代理到 OpenClaw Gateway (port 18789)
- ✅ API路径: `/v1/chat/completions` (OpenAI兼容)
- ✅ Agent路由: `model: "openclaw/sciflow-main"` → 主Agent
- ✅ 流式SSE响应，前端无感知切换

### 3. 前端不变
- 用户感受完全相同：学术风UI、流式打字、Markdown渲染

## 🔧 需要手动操作（1次）

Gateway 需要重启才能加载新配置：

```bash
openclaw gateway restart
```

或者直接在终端里按 Ctrl+C 停掉然后重新启动。

## 🚀 重启后

```
浏览器 → http://localhost:5000 → Flask → OpenClaw Gateway → sciflow-main Agent
                                                                    ├─ sessions_spawn → sciflow-reader
                                                                    │     └─ → search → skim → deepread → analyze → knowledge
                                                                    ├─ sessions_spawn → sciflow-recommend
                                                                    └─ sessions_spawn → sciflow-writer
```

用户在前端跟主Agent对话，主Agent根据需求自动调度子Agent，结果汇总后返回前端。
