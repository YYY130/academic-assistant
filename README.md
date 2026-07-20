# 🧪 Academic Assistant — OpenClaw Multi-Agent System

> *A full-stack academic research assistant powered by 9 collaborative AI agents. Search papers → recommend readings → generate reports — all handled by autonomous agents.*

---

## ✨ Features

- **Multi-Agent Pipeline** — 9 specialized AI agents collaborating on a shared goal
- **Paper Discovery & Analysis** — Search arXiv/Semantic Scholar, skim, deep-read, and analyze papers
- **Personalized Recommendation** — Agent that learns your research interests over time
- **Academic Writing** — Generate draft papers from experimental data
- **Dual Database** — Persistent vector knowledge base (DB A) + ephemeral experiment storage (DB B)
- **Parallel Processing** — Multiple papers analyzed concurrently via agent spawning

## 🧠 System Architecture

```
┌─────────────────────────────────────────────────────┐
│                   User Interface                     │
│          (WebChat / Discord / Telegram / CLI)        │
└─────────────────────────┬───────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────┐
│                   Main Agent                         │
│          Intent recognition · Task dispatch          │
│                  model: Pro                          │
└──────┬─────────────────────┬────────────────────────┘
       │                     │
       ▼                     ▼
┌──────────────┐   ┌───────────────┐   ┌────────────┐
│   Reading    │   │ Personalized  │   │  Writing   │
│ Orchestrator │   │ Recommender   │   │   Agent    │
│ Pipeline mgr │   │ Interest-based│   │ Data→Paper │
│ model: Flash │   │ model: Flash  │   │ model: Pro │
└──────┬───────┘   └───────┬───────┘   └─────┬──────┘
       │                    │                 │
       ▼                    ▼                 ▼
  ┌──────────┐       ┌────────┐       ┌────────┐
  │ Search   │       │  DB A  │       │  DB B  │
  │   Agent  │       │ Vector │       │  Exp.  │
  │ Flash    │       │  K.B.  │       │  Data  │
  └────┬─────┘       │(persist)│      │(ephem) │
       ▼             └────────┘       └────────┘
  ┌──────────┐
  │  Skim    │
  │  Agent   │
  │  Filter  │
  └────┬─────┘
       ▼
  ┌──────────┐
  │  Deep    │← parallel instances
  │  Reader  │
  │  Flash   │
  └────┬─────┘
       │
   ┌───┴────────┐
   ▼            ▼
┌────────┐ ┌──────────┐
│Analyst │ │Associator│
│Combine │ │ Store KB │
│Flash   │ │ Flash    │
└────┬───┘ └────┬─────┘
     │          │
     └──→ Orchestrator → Main Agent → User
```

## 🤖 Agent Overview

| Agent | Role | Model | Responsibility |
|-------|------|-------|---------------|
| **main_agent** | Research Assistant | Pro | Intent recognition, task dispatch, user interaction |
| **reading_orchestrator** | Pipeline Manager | Flash | Orchestrate multi-stage reading pipeline, concurrency |
| **search_agent** | Scout | Flash | Multi-source paper search (arXiv, S2, Web) |
| **skim_agent** | Filter | Flash | Quick relevance assessment, paper triage |
| **deep_read_agent** | Deep Reader | Flash | Full-text analysis, structured note-taking |
| **analysis_agent** | Analyst | Flash | Cross-paper synthesis, insight extraction |
| **association_agent** | Archivist | Flash | Structured ingestion into vector KB (DB A) |
| **personalized_recommender** | Curator | Flash | Interest profile × knowledge base → recommendations |
| **writing_agent** | Writer | Pro | Data-driven academic paper generation |

## 🗄️ Dual Database Design

| Dimension | DB A (Vector KB) | DB B (Experiment Data) |
|-----------|------------------|----------------------|
| **Content** | Paper knowledge, relationships | Experiment data, analysis results |
| **Lifetime** | Cross-task, persistent | Per-task, ephemeral |
| **Accessed by** | Main Agent, Recommender, Associator | Writing Agent |
| **Index** | all-MiniLM-L6-v2 (local embeddings) | Structured file storage |
| **Path** | `shared/db_a/` | `shared/db_b/` |

## 📡 Agent Communication

Built on OpenClaw's native tools:

| Tool | Purpose |
|------|---------|
| `sessions_spawn` | Create child agents for subtasks |
| `sessions_send` | Cross-agent messaging |
| `sessions_history` | Retrieve child agent results |
| `memory_search` | Cross-session memory retrieval |

### Reading Pipeline Flow

```
main_agent
  └─ spawn → reading_orchestrator
       ├─ spawn → search_agent
       ├─ spawn → skim_agent
       ├─ spawn → deep_read_agent (×N parallel)
       ├─ spawn → analysis_agent (parallel)
       └─ spawn → association_agent (parallel)
       └─ results consolidated → orchestrator → main_agent → user
```

## 🚀 Getting Started

### Prerequisites

- [OpenClaw](https://github.com/openclaw/openclaw) installed and running
- API keys for configured LLM providers (DeepSeek recommended)

### One-Click Setup

```bash
python setup.py
```

The script will:
- Locate your OpenClaw configuration
- Merge the 9 agent definitions into `openclaw.json`
- Create required data directories
- Back up your existing config

> Use `python setup.py --dry-run` to preview changes first.
> Use `python setup.py --path /your/project/path` for custom locations.

### Manual Installation

1. Merge `config/openclaw.agents.json` into your OpenClaw configuration
2. Restart the gateway:
   ```bash
   openclaw gateway restart
   ```

### Run Web Frontend (WSL)

```bash
cd /mnt/c/Users/yuyue/Desktop/作业之类的/龙虾实训/结项作业/academic-assistant
python3 web/server.py
```

> Make sure OpenClaw gateway is running first (`openclaw gateway restart`).
> The web interface connects to the gateway on port `18789`.

### Usage Examples

```
User: "Find me the latest papers on transformer attention mechanisms"
  → Pipeline dispatches automatically → returns reading report

User: "Recommend some NLP papers"
  → Recommender queries KB → returns curated list

User: "Write a paper based on experiment data"
  → Writing Agent queries DB B → returns draft
```

### Quick Test

```bash
python shared/scripts/store_to_db_a.py --action list
```

## 📁 Project Structure

```
academic-assistant/
├── agents-workspace/           # Runtime workspace for 9 agents
│   ├── main_agent/
│   ├── reading_orchestrator/
│   ├── search_agent/
│   ├── skim_agent/
│   ├── deep_read_agent/
│   ├── analysis_agent/
│   ├── association_agent/
│   ├── personalized_recommender/
│   └── writing_agent/
├── shared/
│   ├── db_a/                   # Vector knowledge base
│   ├── db_b/                   # Experiment data store
│   └── scripts/                # Shared agent utilities
├── config/
│   ├── openclaw.agents.json    # Agent configuration
│   ├── agent_config.yaml       # Agent parameters
│   ├── database.yaml           # Database settings
│   └── default.yaml            # Default config
├── docs/                       # Documentation
├── experiment/                 # Sample experiment data
├── references/                 # Reference papers
└── web/                        # Web interface
```

## 💡 Design Philosophy

1. **Real AI Agents** — Each agent is a genuine LLM-powered entity on the OpenClaw platform, not a scripted simulation
2. **Spawn-based Parallelism** — Main agent spawns child agents on demand, enabling concurrent paper analysis
3. **Memory-Aware** — Core agents (main, recommender, writer) maintain persistent memory; pipeline agents are stateless per task
4. **Data Separation** — Knowledge assets (DB A) and process data (DB B) have distinct lifecycles for efficient storage management
5. **Minimal Dependencies** — Only requires OpenClaw runtime + configured LLM providers; no additional infrastructure

---

## 📦 Tech Stack

- **Platform:** [OpenClaw](https://github.com/openclaw/openclaw)
- **LLMs:** DeepSeek V4 Pro / Flash
- **Embeddings:** all-MiniLM-L6-v2 (local)
- **Storage:** File-based vector KB, structured files
- **Interface:** WebChat, Discord, Telegram, CLI

---

*Built with OpenClaw — an open-source agent framework.*
