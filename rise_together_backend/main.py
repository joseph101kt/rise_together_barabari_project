from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import text
from fastapi.middleware.cors import CORSMiddleware
import app.models  # noqa: F401 — registers all models with Base before create_all runs
from app.api import api_router
from app.core.database import Base, SessionLocal, engine


MODULE_CARD_VIEW_SQL = """
CREATE OR REPLACE VIEW module_card_view AS
SELECT
    m.id,
    m.parent_id,
    m.module_type,
    m.title,
    m.description,
    m.estimated_completion_time,
    m.created_by,
    m.order_index,
    m.created_at,
    m.updated_at,
    COUNT(DISTINCT ml.link_id)     AS resource_count,
    COUNT(DISTINCT ms.skill_id)    AS skill_count,
    COUNT(DISTINCT mstar.user_id)  AS star_count
FROM modules m
LEFT JOIN module_links  ml    ON ml.module_id    = m.id
LEFT JOIN module_skills ms    ON ms.module_id    = m.id
LEFT JOIN module_stars  mstar ON mstar.module_id = m.id
GROUP BY m.id;
"""


@asynccontextmanager
async def lifespan(app: FastAPI):
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


app = FastAPI(
    title="Rise Together API",
    version="0.1.0",
    lifespan=lifespan,
)

#Enable CORS for the React frontend 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
def health():
    return {"status": "ok"}