from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from src.core.config import settings
from src.core.logging import get_logger


logger = get_logger(__name__)

engine = create_engine(
    settings.DATABASE_URL,
    echo=False,        # set to True if you want raw SQL logs
    future=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    future=True,
)

Base = declarative_base()


def get_db():
    """
    FastAPI dependency-style DB session provider.
    Usage later:
      def endpoint(db: Session = Depends(get_db)):
          ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
