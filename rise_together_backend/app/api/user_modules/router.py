from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.user_modules import (
    UserModuleCreateRequest,
    UserModuleLinkCreateRequest,
    UserModuleLinkPatchRequest,
    UserModuleResponse,
)
from app.services.user_module_service import UserModuleService

router = APIRouter(prefix="/user_modules", tags=["User Modules"])


@router.get(
    "",
    response_model=list[UserModuleResponse],
    summary="Get all modules the current user is tracking, with their submitted links.",
)
def list_user_modules(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return UserModuleService(db).get_user_modules(current_user.id)


@router.get(
    "/{module_id}",
    response_model=UserModuleResponse,
    summary="Get the current user's progress on a single module, with submitted links.",
)
def get_user_module(
    module_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return UserModuleService(db).get_user_module(current_user.id, module_id)


@router.post(
    "",
    response_model=UserModuleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Start tracking a module (creates a user_module row with status=in_progress).",
)
def create_user_module(
    body: UserModuleCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return UserModuleService(db).create_user_module(current_user.id, body)


@router.post(
    "/{module_id}/links",
    response_model=UserModuleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit a link for a module-link slot. Returns the updated user_module with all submitted links.",
)
def create_user_module_link(
    module_id: int,
    body: UserModuleLinkCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return UserModuleService(db).create_user_module_link(
        current_user.id, module_id, body
    )


@router.patch(
    "/{module_id}/links/{module_link_id}",
    response_model=UserModuleResponse,
    summary="Mark a submitted link as completed or not. Auto-syncs the module status.",
)
def patch_user_module_link(
    module_id: int,
    module_link_id: int,
    body: UserModuleLinkPatchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return UserModuleService(db).patch_user_module_link(
        current_user.id, module_id, module_link_id, body
    )