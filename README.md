# Reflexion Agent

*A LangGraph-powered research assistant that iteratively **reflects**, **searches**, and **revises** its own answers.*

![Python](https://img.shields.io/badge/python-3.12%2B-blue?logo=python)
![LangGraph](https://img.shields.io/badge/LangGraph-0.0.x-9cf?logo=langchain)
![LangChain](https://img.shields.io/badge/LangChain-0.3.x-yellow?logo=langchain)
[![LangSmith](https://img.shields.io/badge/LangSmith-Traces-blueviolet?logo=langchain)](https://smith.langchain.com/o/856312b1-7816-4389-80cb-b01e398655be/projects/p/b2155aff-ef1a-46ae-b9a5-2607e5cdb310?timeModel=%7B%22duration%22%3A%227d%22%7D)
![Rich](https://img.shields.io/badge/Rich‑CLI-Colorful-green?logo=python)
![Tavily](https://img.shields.io/badge/Tavily-Search-blueviolet)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

---

## Table of Contents

1. [Why Reflexion?](#why-reflexion)
2. [How it Works](#how-it-works)
3. [Architecture Overview](#architecture-overview)
4. [Quick Start](#quick-start)
5. [Repository Structure](#repository-structure)
6. [Environment Variables](#environment-variables)
7. [License](#license)

---

## Why Reflexion?

Traditional LLM agents answer once and call it a day.
**Reflexion Agent** uses a three‑stage loop to *self‑improve*:

| Stage            | Purpose                                                              |
| ---------------- | -------------------------------------------------------------------- |
| **Draft**        | Generate a first answer **plus** critique & search queries           |
| **Search Tools** | Execute the Tavily web‑search tool for each query                    |
| **Reviser**      | Integrate fresh evidence, apply the critique, and rewrite the answer |

The loop repeats until either the answer passes its own quality check or `MAX_ITERATIONS` (default = 3) is reached.

---

## How it Works

### LangGraph workflow

```text
 ┌────────┐   search   ┌────────────────┐
 │ Draft  │ ─────────► │ Execute Tools │
 └────────┘ ◄───────── └────────────────┘
     │                        │
     ▼ revise                 ▼
 ┌────────┐  (conditional) ┌────────────┐
 │ END    │◄───────────────│  Reviser   │
 └────────┘                └────────────┘
```

* **Nodes** are regular LangChain chains; edges are managed by LangGraph.
* A small callback inspects the state to decide whether to loop or halt.

---

## Architecture Overview

![Reflexion Agent Architecture](reflexion_actor.png)

The diagram shows the high‑level components that power the agent: prompt templates, structured tool calls, Tavily search, and the LangGraph event loop.

---

## Quick Start

```bash
# 1. Clone & enter
git clone https://github.com/ndkhoa211/reflexion_agent
cd reflexion_agent

# 2. Create an isolated env (uv is recommended but pip works)
uv venv        # or: python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv pip install -e .        # or: pip install -r requirements.txt

# 3. Set your secrets
cp .env.example .env   # then edit OPENAI_API_KEY, TAVILY_API_KEY, ...

# 4. Run
python main.py
```

You’ll see the Rich flow diagram printed live, followed by the *Final Answer* panel.

---

## Repository Structure

```text
reflexion_agent/
├── main.py                 # Entry point – builds & runs the LangGraph
├── chains.py               # Draft & Reviser prompt templates
├── tool_executor.py        # Tavily‑powered search ToolNode
├── schemas.py              # Pydantic schemas used for function calling
├── reflection_agent.png    # Auto‑generated graph diagram
├── reflexion_actor.png     # High‑level architecture snapshot
├── pyproject.toml          # Min‑pinned dependencies (uv‑style)
└── uv.lock                 # Exact versions for reproducibility
```

---

## Environment Variables

| Variable                  | Purpose                |
| ------------------------- | ---------------------- |
| `OPENAI_API_KEY`          | Chat & embedding model |
| `TAVILY_API_KEY`          | Web search tool        |
| `LANGSMITH_API_KEY` (opt) | Tracing & dashboards   |

Load them via a local `.env` – `python‑dotenv` is called at start‑up.

---

## License

[MIT](LICENSE) – free to adapt, remix, and build upon.

Happy reflecting! 🚀
