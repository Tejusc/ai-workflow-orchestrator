from fastapi import FastAPI
from pydantic import BaseModel
import uuid
from typing import Literal


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

