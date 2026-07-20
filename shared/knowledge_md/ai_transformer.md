# Transformer架构分析 — 知识库

> 来源会话：2026-07-19 "帮我分析Transformer架构"
> 更新于：2026-07-19

---

## 📄 核心文献

### 1. Attention Is All You Need
- **作者：** Vaswani A, Shazeer N, Parmar N, et al.
- **会议：** NeurIPS 2017
- **核心贡献：**
  - 提出纯基于自注意力机制的 Transformer 架构，彻底抛弃 RNN/LSTM 的循环结构
  - 核心组件：Multi-Head Self-Attention、Feed Forward Network、残差连接 + LayerNorm、Positional Encoding
  - 奠定了 BERT、GPT 系列等大模型的基础架构

## 🏗️ 架构要点

| 组件 | 说明 |
|------|------|
| Self-Attention | 通过 QKV 计算任意两个位置的注意力权重，捕获长距离依赖 |
| Multi-Head | 并行多个注意力头，捕捉不同子空间的语义信息 |
| FFN | 两个 1×1 卷积/全连接层，引入非线性变换 |
| Add & Norm | 残差连接缓解梯度消失；LayerNorm 稳定训练 |
| Positional Encoding | 正弦/余弦函数编码位置信息（后续改用 RoPE） |

> **共收录：1 篇（经典文献） | 来源查询：Transformer架构分析问答**
