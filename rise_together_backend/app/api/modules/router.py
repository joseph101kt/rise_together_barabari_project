from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.modules import ModuleCardResponse, ModuleDetailsResponse, ModuleTreeResponse
from app.schemas.progress import (
    LinkProgressRequest,
    LinkProgressResponse,
    ModuleProgressRequest,
    ModuleProgressResponse,
)
from app.services.module_service import ModuleService
from app.services.progress_services import ProgressService

router = APIRouter(prefix="/modules", tags=["Modules"])


# ---------------------------------------------------------------------------
# Module reads
# ---------------------------------------------------------------------------

@router.get(
    "",
    response_model=list[ModuleCardResponse],
    summary="List modules. Defaults to root level (no parent). Pass ?parent_id=N for children.",
)
def list_modules(parent_id: int | None = None, db: Session = Depends(get_db)):
    return ModuleService(db).list_modules(parent_id=parent_id)


@router.get(
    "/{module_id}",
    response_model=ModuleDetailsResponse,
    summary="Get a module with its skills, links, and direct children",
)
def get_module(module_id: int, db: Session = Depends(get_db)):
    return ModuleService(db).get_module(module_id)


@router.get(
    "/{module_id}/tree",
    response_model=ModuleTreeResponse,
    summary="Get a module and all its descendants as a nested tree",
)
def get_module_tree(module_id: int, db: Session = Depends(get_db)):
    return ModuleService(db).get_tree(module_id)


# ---------------------------------------------------------------------------
# Progress
# ---------------------------------------------------------------------------

@router.patch(
    "/{module_id}/progress",
    response_model=ModuleProgressResponse,
    summary="Update the current user's progress status on a module",
)
def update_module_progress(
    module_id: int,
    body: ModuleProgressRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return ProgressService(db).update_module_status(
        user_id=current_user.id,
        module_id=module_id,
        status_value=body.status,
    )


@router.patch(
    "/{module_id}/links/{link_id}/progress",
    response_model=LinkProgressResponse,
    summary="Mark a specific link within a module as completed or not",
)
def update_link_progress(
    module_id: int,
    link_id: int,
    body: LinkProgressRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return ProgressService(db).update_link_progress(
        user_id=current_user.id,
        module_id=module_id,
        link_id=link_id,
        completed=body.completed,
    )