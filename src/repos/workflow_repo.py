from sqlalchemy.orm import Session
from src.models.workflow import Workflow


def get_workflow_by_id(db: Session, workflow_id: str) -> Workflow | None:
    return db.get(Workflow, workflow_id)
