from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.module_repository import ModuleRepository
from app.repositories.user_module_repository import UserModuleRepository
from app.schemas.user_modules import (
    UserModuleCreateRequest,
    UserModuleLinkCreateRequest,
    UserModuleLinkPatchRequest,
    UserModuleResponse,
)


class UserModuleService:
    def __init__(self, db: Session):
        self.repo = UserModuleRepository(db)
        self.module_repo = ModuleRepository(db)

    # ------------------------------------------------------------------
    # Reads
    # ------------------------------------------------------------------

    def get_user_modules(self, user_id: int) -> list[UserModuleResponse]:
        rows = self.repo.get_user_modules(user_id)
        return [UserModuleResponse(**row) for row in rows]

    def get_user_module(self, user_id: int, module_id: int) -> UserModuleResponse:
        row = self.repo.get_user_module(user_id, module_id)
        if row is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No progress record found for module {module_id}.",
            )
        return UserModuleResponse(**row)

    # ------------------------------------------------------------------
    # Writes
    # ------------------------------------------------------------------

    def create_user_module(
        self, user_id: int, body: UserModuleCreateRequest
    ) -> UserModuleResponse:
        if not self.module_repo.exists(body.module_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Module {body.module_id} not found.",
            )

        try:
            row = self.repo.create_user_module(user_id, body.module_id)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail=str(exc)
            ) from exc

        return UserModuleResponse(**row)

    def create_user_module_link(
        self,
        user_id: int,
        module_id: int,
        body: UserModuleLinkCreateRequest,
    ) -> UserModuleResponse:
        if not self.module_repo.exists(module_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Module {module_id} not found.",
            )

        # Ensure the user has a user_module row before submitting a link
        if self.repo.get_user_module(user_id, module_id) is None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Start module {module_id} before submitting links.",
            )

        try:
            row = self.repo.create_user_module_link(
                user_id=user_id,
                module_id=module_id,
                module_link_id=body.module_link_id,
                url=body.url,
                title=body.title,
            )
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail=str(exc)
            ) from exc

        return UserModuleResponse(**row)

    def patch_user_module_link(
        self,
        user_id: int,
        module_id: int,
        module_link_id: int,
        body: UserModuleLinkPatchRequest,
    ) -> UserModuleResponse:
        try:
            row = self.repo.patch_user_module_link(
                user_id=user_id,
                module_id=module_id,
                module_link_id=module_link_id,
                completed=body.completed,
            )
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
            ) from exc

        return UserModuleResponse(**row)