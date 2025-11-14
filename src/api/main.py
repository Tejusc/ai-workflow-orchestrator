from fastapi import FastAPI
from pydantic import BaseModel
import uuid
from typing import Literal

from src.api.schemas import WorkflowInput, WorkflowResponse
from src.orchestration.orchestrator import Orchestrator


class HealthResponse(BaseModel):
    status: Literal["ok"]
    service: str
    version: str
    request_id: str


app = FastAPI(
    title="AI Workflow Orchestrator",
    version="0.1.0",
    description="Backend service for LLM-driven workflow planning and execution.",
)

orchestrator = Orchestrator()


@app.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    """
    Basic health endpoint to verify the API is running.
    """
    return HealthResponse(
        status="ok",
        service="ai-workflow-orchestrator",
        version="0.1.0",
        request_id=str(uuid.uuid4()),
    )


@app.post("/workflows/run", response_model=WorkflowResponse)
def run_workflow(request: WorkflowInput) -> WorkflowResponse:
    """
    Create and execute a workflow for the given objective + inputs.
    For now this uses a dummy orchestrator implementation that returns
    a fake completed workflow.
    """
    workflow_id = orchestrator.plan_workflow(request)
    result = orchestrator.execute_workflow(workflow_id)
    return result
