# app/api/modules/router.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.modules import ModuleResponse
from app.services.module_service import ModuleService

router = APIRouter(prefix="/modules", tags=["Modules"])


@router.get(
    "",
    response_model=list[ModuleResponse],
    summary="Get all root modules with their complete descendant trees.",
)
def list_modules(db: Session = Depends(get_db)):
    return ModuleService(db).get_root_modules()


@router.get(
    "/roots",
    response_model=list[ModuleResponse],
    summary="Get ONLY root modules (where parent_id is NULL) with their descendant trees.",
)
def list_root_modules_only(db: Session = Depends(get_db)):
    return ModuleService(db).get_all_root_modules_only()


@router.get(
    "/{module_id}",
    response_model=ModuleResponse,
    summary="Get a module and its complete descendant tree.",
)
def get_module(module_id: int, db: Session = Depends(get_db)):
    return ModuleService(db).get_module(module_id)