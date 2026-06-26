from contextlib import asynccontextmanager
from pathlib import Path


from fastapi import FastAPI
from sqlalchemy import text

import app.models  # noqa: F401 — registers all models with Base before create_all runs
from app.core.database import Base, SessionLocal, engine


# SQL for the module_card_view.
# CREATE OR REPLACE VIEW is safe to run every startup — it's idempotent.
MODULE_CARD_VIEW_SQL = (
    Path(__file__).parent / "sql" / "module_card_view.sql"
).read_text(encoding="utf-8")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- startup ---
    # Create all tables that don't exist yet.
    # Safe to run every time — won't touch existing tables.
    Base.metadata.create_all(bind=engine)

    # Create the module_card_view SQL view.
    with SessionLocal() as db:
        try:
            db.execute(text(MODULE_CARD_VIEW_SQL))
            db.commit()
        except Exception:
            db.rollback()
            raise

    yield
    # --- shutdown (nothing needed for MVP) ---


app = FastAPI(
    title="Rise Together API",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/health")
def health():
    return {"status": "ok"}