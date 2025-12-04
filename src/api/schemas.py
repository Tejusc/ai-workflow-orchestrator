from pydantic import BaseModel
from typing import Any, Dict, List, Optional


class WorkflowInput(BaseModel):
    objective: str
    inputs: Dict[str, Any] = {}


class TaskResult(BaseModel):
    task_id: str
    status: str
    output: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class WorkflowResponse(BaseModel):
    workflow_id: str
    status: str
    results: List[TaskResult] = []

class WorkflowStatusResponse(BaseModel):
    workflow_id: str
    status: str
    tasks: List[TaskResult]

