from typing import List
from uuid import uuid4

from sqlalchemy.orm import Session

from src.api.schemas import WorkflowInput, WorkflowResponse, TaskResult
from src.core.logging import get_logger
from src.core.db import SessionLocal
from src.models.workflow import Workflow, Task


logger = get_logger(__name__)


class Orchestrator:
    def __init__(self):
        logger.info("Orchestrator initialized")

    def _get_db(self) -> Session:
        return SessionLocal()

    def plan_workflow(self, request: WorkflowInput) -> str:
        """
        Create a workflow + initial task in the database.
        For now, we create a single generic task.
        """
        db = self._get_db()
        try:
            workflow = Workflow(
                objective=request.objective,
                status="planned",
            )
            db.add(workflow)
            db.flush()  # get workflow.id without full commit yet

            initial_task = Task(
                workflow_id=workflow.id,
                type="dummy",
                status="pending",
                input={"inputs": request.inputs},
            )
            db.add(initial_task)

            db.commit()

            logger.info(
                "Planned workflow in DB",
                extra={
                    "workflow_id": workflow.id,
                    "objective": request.objective,
                    "task_count": 1,
                },
            )

            return workflow.id
        except Exception as e:
            db.rollback()
            logger.error(
                "Error planning workflow",
                extra={"error": str(e)},
            )
            raise
        finally:
            db.close()

    def execute_workflow(self, workflow_id: str) -> WorkflowResponse:
        """
        Very simple execution:
        - Load workflow + tasks
        - Mark tasks as completed with dummy output
        - Mark workflow as completed
        """
        db = self._get_db()
        try:
            workflow: Workflow | None = db.get(Workflow, workflow_id)
            if workflow is None:
                logger.error(
                    "Workflow not found",
                    extra={"workflow_id": workflow_id},
                )
                # In a real system, you'd raise a domain error
                return WorkflowResponse(
                    workflow_id=workflow_id,
                    status="not_found",
                    results=[],
                )

            logger.info(
                "Executing workflow from DB",
                extra={"workflow_id": workflow_id},
            )

            results: list[TaskResult] = []

            for task in workflow.tasks:
                # dummy execution
                task.status = "completed"
                task.output = {
                    "message": "dummy execution from DB-backed orchestrator"
                }

                results.append(
                    TaskResult(
                        task_id=task.id,
                        status=task.status,
                        output=task.output,
                        error=task.error,
                    )
                )

            workflow.status = "completed"
            db.commit()

            logger.info(
                "Workflow execution completed",
                extra={
                    "workflow_id": workflow.id,
                    "task_count": len(workflow.tasks),
                    "status": workflow.status,
                },
            )

            return WorkflowResponse(
                workflow_id=workflow.id,
                status=workflow.status,
                results=results,
            )
        except Exception as e:
            db.rollback()
            logger.error(
                "Error executing workflow",
                extra={"workflow_id": workflow_id, "error": str(e)},
            )
            raise
        finally:
            db.close()
