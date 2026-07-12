# app/api/modules/router.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.modules import ModuleResponse
from app.services.module_service import ModuleService

router = APIRouter(prefix="/modules", tags=["Modules"])


@router.get(
    "/roots",
    response_model=list[ModuleResponse],
    summary="Get ONLY root modules (where parent_id is NULL) with their descendant trees.",
)
def list_root_modules(db: Session = Depends(get_db)):
    return ModuleService(db).get_root_modules()


@router.get(
    "",
    response_model=list[ModuleResponse],
    summary="Get ALL modules in the database with their complete descendant trees.",
)
def list_all_modules(db: Session = Depends(get_db)):
    return ModuleService(db).get_all_modules()


@router.get(
    "/{module_id}",
    response_model=ModuleResponse,
    summary="Get a module and its complete descendant tree.",
)
def get_module(module_id: int, db: Session = Depends(get_db)):
    return ModuleService(db).get_module(module_id)