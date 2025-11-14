from typing import List
from uuid import uuid4

from src.api.schemas import WorkflowInput, WorkflowResponse, TaskResult


class Orchestrator:
    def __init__(self):
        # later: inject db, llm client, tool registry, etc.
        pass

    def plan_workflow(self, request: WorkflowInput) -> str:
        """
        For now, just return a fake workflow_id.
        Later: create tasks, persist them, etc.
        """
        workflow_id = str(uuid4())
        # TODO: store workflow + initial tasks in DB
        return workflow_id

    def execute_workflow(self, workflow_id: str) -> WorkflowResponse:
        """
        Temporary implementation: return a dummy response.
        Later: load tasks from DB, execute them, update status.
        """
        dummy_task = TaskResult(
            task_id="task-1",
            status="completed",
            output={"message": "dummy execution"},
        )
        return WorkflowResponse(
            workflow_id=workflow_id,
            status="completed",
            results=[dummy_task],
        )

