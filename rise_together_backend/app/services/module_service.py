from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.module_repository import ModuleRepository
from app.schemas.modules import ModuleResponse


class ModuleService:
    def __init__(self, db: Session):
        self.module_repo = ModuleRepository(db)

    def get_root_modules(self) -> list[ModuleResponse]:
        rows = self.module_repo.get_root_modules()
        return [ModuleResponse(**row) for row in rows]

    def get_module(self, module_id: int) -> ModuleResponse:
        data = self.module_repo.get_module(module_id)
        if data is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Module {module_id} not found",
            )
        return ModuleResponse(**data)