from src.core.db import engine, Base
from src.models.workflow import Workflow, Task  # noqa: F401


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_db()
