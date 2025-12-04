from sqlalchemy.orm import Session

from src.api.schemas import WorkflowInput, WorkflowResponse, TaskResult
from src.core.logging import get_logger
from src.core.db import SessionLocal
from src.core.tools import execute_tool
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

        For now, we create a single 'summarize_text' task that uses the LLM-backed
        summarize_text_tool. We derive the text from the inputs or fall back
        to the objective.
        """
        db = self._get_db()
        try:
            workflow = Workflow(
                objective=request.objective,
                status="planned",
            )
            db.add(workflow)
            db.flush()  # get workflow.id without full commit yet

            # Prefer explicit text from inputs, fallback to objective.
            text = ""
            if isinstance(request.inputs, dict):
                text = str(request.inputs.get("text", "")).strip()
            if not text:
                text = request.objective

            initial_task = Task(
                workflow_id=workflow.id,
                type="summarize_text",  # tool name
                status="pending",
                input={"text": text},
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
        DB-backed execution:
        - Load workflow + tasks
        - For each task, route to the appropriate tool based on task.type
        - Update task status/output/error
        - Update workflow status based on task outcomes
        """
        db = self._get_db()
        try:
            workflow: Workflow | None = db.get(Workflow, workflow_id)
            if workflow is None:
                logger.error(
                    "Workflow not found",
                    extra={"workflow_id": workflow_id},
                )
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
            any_failed = False

            for task in workflow.tasks:
                try:
                    payload = task.input or {}
                    # Route via tool registry
                    result = execute_tool(task.type, payload)

                    task.status = "completed"
                    task.output = result
                    task.error = None

                except Exception as e:
                    any_failed = True
                    task.status = "failed"
                    task.error = str(e)
                    logger.error(
                        "Task execution failed",
                        extra={
                            "workflow_id": workflow.id,
                            "task_id": task.id,
                            "tool_type": task.type,
                            "error": str(e),
                        },
                    )

                results.append(
                    TaskResult(
                        task_id=task.id,
                        status=task.status,
                        output=task.output,
                        error=task.error,
                    )
                )

            workflow.status = "failed" if any_failed else "completed"
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
