from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
import uuid
from typing import Literal

from sqlalchemy.orm import Session

from src.api.schemas import (
    WorkflowInput,
    WorkflowResponse,
    WorkflowStatusResponse,
    TaskResult,
)
from src.orchestration.orchestrator import Orchestrator
from src.core.logging import get_logger
from src.core.config import settings
from src.core.db import get_db
from src.repos.workflow_repo import get_workflow_by_id


class HealthResponse(BaseModel):
    status: Literal["ok"]
    service: str
    version: str
    request_id: str


app = FastAPI(
    title="AI Workflow Orchestrator",
    version=settings.API_VERSION,
    description="Backend service for LLM-driven workflow planning and execution.",
)

logger = get_logger("api")
orchestrator = Orchestrator()


@app.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    """
    Basic health endpoint to verify the API is running.
    """
    request_id = str(uuid.uuid4())
    logger.info("Health check request", extra={"request_id": request_id})

    return HealthResponse(
        status="ok",
        service="ai-workflow-orchestrator",
        version=settings.API_VERSION,
        request_id=request_id,
    )


@app.post("/workflows/run", response_model=WorkflowResponse)
def run_workflow(request: WorkflowInput) -> WorkflowResponse:
    """
    Create and execute a workflow for the given objective + inputs.
    Currently:
      - Creates a DB-backed workflow + single summarize_text task
      - Executes the workflow by routing tasks to tools
      - Returns structured results.
    """
    request_id = str(uuid.uuid4())
    logger.info(
        "Received workflow run request",
        extra={
            "request_id": request_id,
            "objective": request.objective,
            "has_inputs": bool(request.inputs),
        },
    )

    workflow_id = orchestrator.plan_workflow(request)
    result = orchestrator.execute_workflow(workflow_id)

    logger.info(
        "Returning workflow result",
        extra={
            "request_id": request_id,
            "workflow_id": workflow_id,
            "status": result.status,
            "task_count": len(result.results),
        },
    )

    return result


@app.get("/workflows/{workflow_id}", response_model=WorkflowStatusResponse)
def get_workflow_status(
    workflow_id: str,
    db: Session = Depends(get_db),
) -> WorkflowStatusResponse:
    """
    Fetch the current status of a workflow and all its tasks.
    This is essential for monitoring and UI/debugging.
    """
    wf = get_workflow_by_id(db, workflow_id)
    if wf is None:
        logger.warning(
            "Workflow not found on status fetch",
            extra={"workflow_id": workflow_id},
        )
        raise HTTPException(status_code=404, detail="Workflow not found")

    tasks = [
        TaskResult(
            task_id=t.id,
            status=t.status,
            output=t.output,
            error=t.error,
        )
        for t in wf.tasks
    ]

    logger.info(
        "Returning workflow status",
        extra={
            "workflow_id": wf.id,
            "status": wf.status,
            "task_count": len(tasks),
        },
    )

    return WorkflowStatusResponse(
        workflow_id=wf.id,
        status=wf.status,
        tasks=tasks,
    )
