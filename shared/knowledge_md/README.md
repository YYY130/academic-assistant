# 库A — 全局论文持久化知识库

> 创建时间：2026-07-19
> 
> 说明：本库存储所有通过 SciFlow 科研助手系统查询、分析、生成的论文记录。

## 结构

```
knowledge_base/
├── README.md          ← 本文件（使用说明）
├── INDEX.md           ← 全库索引（按主题分类）
├── environment/       ← 环境科学领域
│   ├── climate_change.md    ← 气候变化/碳中和
│   ├── microplastics.md     ← 微塑料污染
│   ├── pfas.md              ← PFAS新型污染物
│   ├── remediation.md       ← 环境修复技术
│   └── ai_monitoring.md     ← AI+环境监测
├── ai/               ← 人工智能领域
│   ├── trends_2026.md       ← 2025-2026 AI学术风向
│   ├── llm_reasoning.md     ← 大语言模型推理
│   └── transformer.md       ← Transformer架构分析
└── generated/         ← 系统生成的论文/报告
    ├── ai_trends_report.md   ← AI趋势报告
    └── env_science_report.md ← 环境科学报告
```

## 使用方式

- 用户通过主Agent查询时，优先检索库A
- 新查询的论文在 sciflow-reader 完成流程后，自动存入对应分类
- 支持按主题/关键词/时间跨库检索
