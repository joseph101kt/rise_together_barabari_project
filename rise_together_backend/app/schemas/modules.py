from __future__ import annotations

from pydantic import BaseModel, Field

from app.schemas.shared import ModuleLinkResponse, SkillResponse


class ModuleResponse(BaseModel):
    """
    Recursive module response.

    Returned by:
    - GET /modules
    - GET /modules/{module_id}
    """

    id: int
    parent_id: int | None = None
    title: str
    description: str | None = None
    estimated_completion_time: str | None = None
    order_index: int

    skills: list[SkillResponse] = Field(default_factory=list)
    links: list[ModuleLinkResponse] = Field(default_factory=list)
    children: list["ModuleResponse"] = Field(default_factory=list)

    model_config = {"from_attributes": True}


ModuleResponse.model_rebuild()