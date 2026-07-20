# 大语言模型推理 — 论文库

> 来源会话：2026-07-19 "搜索1篇关于大语言模型推理的最新论文"
> 更新于：2026-07-19

---

## 📄 论文清单

### 1. Towards Thinking-Optimal Scaling of Test-Time Compute for LLM Reasoning (TOPS)
- **作者：** Wenkai Yang, Shuming Ma, Yankai Lin, Furu Wei（人大高瓴AI学院 & Microsoft Research）
- **会议：** **NeurIPS 2025**
- **arXiv：** 2502.18080，2025年2月
- **代码：** https://github.com/RUCBM/TOPS
- **核心发现：**
  - 提出 **TOPS（Thinking-Optimal Scaling）** 框架，解决 LLM 推理时测试时计算（Test-Time Compute）的扩展效率问题
  - 发现并非所有问题都需要增加推理计算量，关键在于**动态分配**：简单问题用少量推理、复杂问题用深度推理
  - 提出"思考最优"策略，在保持推理准确率的同时显著降低计算开销
- **亮点：** 针对推理模型的"智能分配计算资源"范式，是 2025 年推理模型方向的重要工作

---

> **共收录：1 篇（精读论文） | 来源查询：sciflow-reader 精读任务**
