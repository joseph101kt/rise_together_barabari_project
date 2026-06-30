from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings


engine = create_engine(
    settings.DATABASE_URL,
    echo=False,  # set True temporarily if you want to see SQL in terminal
    pool_pre_ping=True,  # drops stale connections before using them
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    """FastAPI dependency. Yields a session and closes it when the request is done."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()