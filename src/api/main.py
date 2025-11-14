from fastapi import FastAPI
from pydantic import BaseModel
import uuid
from typing import Literal

from src.api.schemas import WorkflowInput, WorkflowResponse
from src.core.config import settings
from src.orchestration.orchestrator import Orchestrator
from src.core.logging import get_logger


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
        version="0.1.0",
        request_id=request_id,
    )


@app.post("/workflows/run", response_model=WorkflowResponse)
def run_workflow(request: WorkflowInput) -> WorkflowResponse:
    """
    Create and execute a workflow for the given objective + inputs.
    For now this uses a dummy orchestrator implementation that returns
    a fake completed workflow.
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
