from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.module_repository import ModuleRepository
from app.schemas.modules import ModuleCardResponse, ModuleDetailsResponse, ModuleTreeResponse


class ModuleService:
    def __init__(self, db: Session):
        self.module_repo = ModuleRepository(db)

    def list_modules(self, parent_id: int | None = None) -> list[ModuleCardResponse]:
        rows = self.module_repo.get_card_list(parent_id=parent_id)
        return [ModuleCardResponse(**row) for row in rows]

    def get_module(self, module_id: int) -> ModuleDetailsResponse:
        data = self.module_repo.get_details(module_id)
        if data is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Module {module_id} not found",
            )
        return ModuleDetailsResponse(
            module=ModuleCardResponse(**data["module"]),
            skills=data["skills"],
            links=data["links"],
            children=[ModuleCardResponse(**c) for c in data["children"]],
        )

    def get_tree(self, module_id: int) -> ModuleTreeResponse:
        data = self.module_repo.get_tree(module_id)
        if data is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Module {module_id} not found",
            )
        return ModuleTreeResponse(**data)