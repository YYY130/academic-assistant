# 已知问题与限制

> 最后更新: 2026-07-20

---

## 🚧 功能缺陷

### 1. 知识库检索仅为关键词匹配

`query_db_a.py` 的搜索实现使用的是简单的关键词匹配，而非真正的向量检索。虽然数据库命名为「向量知识库」，但实际并没有使用嵌入模型进行语义搜索。

**影响:** 查询结果不够精确，无法理解同义词或语义相近的表述。

**建议改进:** 接入 OpenClaw 的 `memory_search` 或本地 Sentence-Transformer 做语义嵌入。

---

### 2. 知识图谱非真正图数据库

`/api/knowledge-graph` 返回的图谱是在 Web 服务启动后，从 pickle 文件中读取论文记录、在内存中计算关联关系构建的。不是真正的图数据库（如 Neo4j、NebulaGraph）。

**影响:**
- 数据量大时性能下降
- 无法进行复杂的图查询（如最短路径、社区发现）
- 重启后重新计算，无持久化缓存

**建议改进:** 引入轻量级图数据库或使用 NetworkX 做图分析并缓存结果。

---

### 3. 会话数据本地 JSON 文件存储

所有聊天会话和消息记录存储在 `web/sessions.json` 和 `web/messages/*.json` 文件中，使用 JSON 文件作为数据库。

**影响:**
- 高并发下存在写冲突（当前用 threading.Lock 缓解，但不彻底）
- 不支持持久化备份
- 消息量大时文件读写性能下降

**建议改进:** 迁移到 SQLite 或轻量级数据库。

---

### 4. Web 前端无用户认证

当前 Web 前端完全开放访问，任何能连接到 `http://localhost:5000` 的人都可以使用。

**影响:** 如果将 Web 端口暴露到公网，存在安全风险。

**建议:** 仅在本地使用，或添加基本认证（Basic Auth / OAuth）。

---

## ⚠️ 已知配置问题

### 5. Agent 工作区路径硬编码

`config/openclaw.agents.json` 中的 workspace 路径使用了 Windows 绝对路径（如 `C:\Users\...\academic-assistant\agents-workspace\main_agent`）。

**影响:** 在其他机器或 WSL 环境中需要手动修改路径。

**建议改进:** 使用相对路径或在 setup.py 中添加自动路径替换逻辑。

---

### 6. Gateway Token 启动时加载

`web/server.py` 中的 `GATEWAY_TOKEN` 在模块导入时一次性加载，不会随 `openclaw.json` 的更新而刷新。

**影响:** 修改 Gateway token 后需要重启 Web 服务。

---

### 7. 依赖缺少 requirements.txt

项目没有 `requirements.txt` 或 `pyproject.toml`，新用户需要自行安装 Flask、requests、pickle 等依赖。

**建议:** 后续补充依赖声明。

---

## 🔧 环境兼容性

### 8. 国内 GitHub / arxiv 访问不稳定

- GitHub 推送依赖 SSH 通道（HTTPS 可能被阻断）
- arxiv 搜索结果依赖网络环境
- OpenClaw 配置中的模型 API 调用依赖对应供应商的网络可达性

---

## 📋 已知 BUG

| # | 问题 | 状态 |
|---|------|------|
| 1 | `deep_read_agent` 使用 `model: deepseek/deepseek-v4-pro` 但 Agent 配置表中写的是 Flash（配置表 vs agent_config.yaml 不一致） | 未修复 |
| 2 | 知识图谱 API 中 `paper_id` 重复记录未在入库时去重，而是在 API 调用时过滤 | 未修复 |
| 3 | Web 前端 SSE 心跳间隔 15 秒，长对话可能因 Gateway 超时而中断 | 未修复 |
