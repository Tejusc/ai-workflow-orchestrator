from typing import List
from uuid import uuid4

from src.api.schemas import WorkflowInput, WorkflowResponse, TaskResult
from src.core.logging import get_logger


logger = get_logger(__name__)


class Orchestrator:
    def __init__(self):
        # later: inject db, llm client, tool registry, etc.
        logger.info("Orchestrator initialized")

    def plan_workflow(self, request: WorkflowInput) -> str:
        """
        For now, just return a fake workflow_id.
        Later: create tasks, persist them, etc.
        """
        workflow_id = str(uuid4())
        logger.info(
            "Planned workflow",
            extra={
                "workflow_id": workflow_id,
                "objective": request.objective,
                "has_inputs": bool(request.inputs),
            },
        )
        # TODO: store workflow + initial tasks in DB
        return workflow_id

    def execute_workflow(self, workflow_id: str) -> WorkflowResponse:
        """
        Temporary implementation: return a dummy response.
        Later: load tasks from DB, execute them, update status.
        """
        logger.info("Executing workflow", extra={"workflow_id": workflow_id})

        dummy_task = TaskResult(
            task_id="task-1",
            status="completed",
            output={"message": "dummy execution"},
        )

        logger.info(
            "Workflow execution completed",
            extra={
                "workflow_id": workflow_id,
                "task_count": 1,
                "status": "completed",
            },
        )

        return WorkflowResponse(
            workflow_id=workflow_id,
            status="completed",
            results=[dummy_task],
        )
