from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.shared import SkillResponse
from app.services.skill_service import SkillService

router = APIRouter(prefix="/skills", tags=["Skills"])


@router.get(
    "",
    response_model=list[SkillResponse],
    summary="List all available skills",
)
def list_skills(db: Session = Depends(get_db)):
    return SkillService(db).list_all()