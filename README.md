# AI Workflow Orchestrator

Backend service that uses LLMs and tools to turn a high-level objective into a workflow of tasks, execute them, and return structured results.  

Think of it as a **mini AI control plane**:
- API in → workflow planned → tasks persisted → tools + LLM called → results stored + exposed via API.

---

## High-Level Overview

### What it does (today)

- Exposes an HTTP API:
  - `POST /workflows/run`  
    - Create + execute a workflow for a given objective and inputs.
  - `GET /workflows/{workflow_id}`  
    - Fetch current status and results for a workflow.

- Persists:
  - **Workflows** (objective, status, timestamps)
  - **Tasks** (type, input, output, error, status)

- Executes tasks by:
  - Routing to a **tool registry**
  - Including an **LLM-backed summarization tool** (`summarize_text`)

- Uses:
  - **Postgres** (via Docker) for persistence
  - **FastAPI** for the HTTP layer
  - **SQLAlchemy** for ORM
  - **OpenAI Chat Completions API** (configurable via env) for LLM calls
  - Structured logging for observability

---

## Architecture

### Components

- `src/api/main.py`
  - FastAPI app
  - `/health`, `/workflows/run`, `/workflows/{id}` endpoints

- `src/api/schemas.py`
  - Pydantic models:
    - `WorkflowInput`
    - `TaskResult`
    - `WorkflowResponse`
    - `WorkflowStatusResponse`

- `src/core/config.py`
  - Central configuration using `pydantic-settings`
  - Reads `.env` for:
    - `DATABASE_URL`
    - `LLM_API_BASE`
    - `LLM_API_KEY`
    - `LLM_MODEL`

- `src/core/db.py`
  - SQLAlchemy engine, session, `Base`, and `get_db` dependency

- `src/models/workflow.py`
  - `Workflow` + `Task` ORM models

- `src/core/logging.py`
  - Structured logger used across API + orchestrator + tools

- `src/core/tools.py`
  - Tool registry:
    - `echo`
    - `uppercase`
    - `summarize_text` (LLM-backed)

- `src/core/llm_client.py`
  - OpenAI-compatible LLM client
  - Wraps `/v1/chat/completions`

- `src/orchestration/orchestrator.py`
  - Orchestrator that:
    - Creates workflows + tasks in DB (`plan_workflow`)
    - Loads tasks, routes to tools, updates results (`execute_workflow`)

- `src/repos/workflow_repo.py`
  - Simple data access for `Workflow` by id

---

## Data Model

### `workflows` table

- `id` (string, UUID)
- `objective` (text)
- `status` (string: `planned`, `completed`, `failed`, etc.)
- `created_at`
- `updated_at`

### `tasks` table

- `id` (string, UUID)
- `workflow_id` (FK → `workflows.id`)
- `type` (tool name: e.g. `summarize_text`)
- `status` (`pending`, `completed`, `failed`)
- `input` (JSON)
- `output` (JSON)
- `error` (text)
- `created_at`
- `updated_at`

---

## Request Flow

### 1. `POST /workflows/run`

Input:

```json
{
  "objective": "Summarize this text",
  "inputs": {
    "text": "Some longer text to summarize..."
  }
}
