from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.enums import UserModuleStatus
from app.repositories.module_repository import ModuleRepository
from app.repositories.progress_repository import ProgressRepository
from app.schemas.progress import (
    LinkProgressResponse,
    ModuleProgressResponse,
    UserSubmissionsResponse,
)


class ProgressService:
    def __init__(self, db: Session):
        self.progress_repo = ProgressRepository(db)
        self.module_repo = ModuleRepository(db)

    def update_module_status(
        self,
        user_id: int,
        module_id: int,
        status_value: UserModuleStatus,
    ) -> ModuleProgressResponse:
        # Verify the module exists before writing progress
        if not self.module_repo.get_details(module_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Module {module_id} not found",
            )

        result = self.progress_repo.upsert_module_progress(
            user_id=user_id,
            module_id=module_id,
            status=status_value.value,
        )
        return ModuleProgressResponse(**result)

    def update_link_progress(
        self,
        user_id: int,
        module_id: int,
        link_id: int,
        completed: bool,
    ) -> LinkProgressResponse:
        # Verify the module exists
        if not self.module_repo.get_details(module_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Module {module_id} not found",
            )

        result = self.progress_repo.upsert_link_progress(
            user_id=user_id,
            module_id=module_id,
            link_id=link_id,
            completed=completed,
        )
        return LinkProgressResponse(**result)

    def get_submissions(self, user_id: int) -> list[UserSubmissionsResponse]:
        rows = self.progress_repo.get_user_submissions(user_id)
        return [UserSubmissionsResponse(**row) for row in rows]