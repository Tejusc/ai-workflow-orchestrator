# AI Workflow Orchestrator

Backend service that uses LLMs and tools to break down a high-level objective into smaller tasks, route them to the right tools (APIs, retrieval, etc.), and return structured results.

## Overview

The system lets a client send an objective like:

> "Read these meeting notes, extract action items, and create Jira tickets."

The orchestrator:
1. Plans a workflow (tasks + dependencies).
2. Executes tasks using LLMs and tools.
3. Stores workflow state and results.
4. Exposes APIs to run and inspect workflows.

## Tech Stack (v1)

- Language: Python
- API: FastAPI
- DB: PostgreSQL (with pgvector later)
- Vector Store: pgvector (or Qdrant in v2)
- LLM: OpenAI-compatible API (configurable)

## High-Level Components

- `api/` – FastAPI endpoints
- `orchestration/` – workflow planning and execution
- `embeddings/` – embeddings client + utilities
- `retrieval/` – document and vector search
- `core/` – shared utilities (logging, config, db)
- `models/` – ORM / Pydantic models
- `tests/` – automated tests
- `docs/` – diagrams and architecture notes

## Roadmap (v1)

- [ ] Basic FastAPI app with `/health`
- [ ] `POST /workflows/run` endpoint (dummy in-memory implementation)
- [ ] Orchestrator skeleton (`plan_workflow`, `execute_workflow`)
- [ ] PostgreSQL integration (SQLAlchemy models)
- [ ] Simple tool registry and one example tool
- [ ] Embeddings + retrieval scaffold
- [ ] Structured logging for workflows and tasks
- [ ] Minimal integration tests

## Running Locally (to be updated)

```bash
# create virtual env
python -m venv .venv
source .venv/bin/activate  # on macOS/Linux

# install deps
pip install -r requirements.txt

# run api
uvicorn src.api.main:app --reload

