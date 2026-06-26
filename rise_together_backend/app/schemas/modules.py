from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from app.models.enums import ModuleType
from app.schemas.shared import ModuleLinkResponse, SkillResponse


class ModuleCardResponse(BaseModel):
    """
    Flat module card — returned by GET /modules and inside details/tree.
    resource_count, skill_count, star_count come from module_card_view.
    """
    id: int
    parent_id: int | None = None
    module_type: ModuleType
    title: str
    description: str | None = None
    estimated_completion_time: str | None = None
    created_by: int
    order_index: int
    resource_count: int = 0
    skill_count: int = 0
    star_count: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ModuleDetailsResponse(BaseModel):
    """
    Returned by GET /modules/:id.
    One level deep — children are flat cards, not recursive.
    Maps to ModuleRepository.get_details().
    """
    module: ModuleCardResponse
    skills: list[SkillResponse]
    links: list[ModuleLinkResponse]
    children: list[ModuleCardResponse]


class ModuleTreeResponse(BaseModel):
    """
    Returned by GET /modules/:id/tree.
    Recursive — children have the same shape as the parent.
    Maps to ModuleRepository.get_tree().

    model_rebuild() below is required for Pydantic v2 to resolve
    the self-referential 'children' field.
    """
    id: int
    parent_id: int | None = None
    module_type: ModuleType
    title: str
    description: str | None = None
    estimated_completion_time: str | None = None
    created_by: int
    order_index: int
    resource_count: int = 0
    skill_count: int = 0
    star_count: int = 0
    created_at: datetime
    updated_at: datetime
    children: list[ModuleTreeResponse] = []

    model_config = {"from_attributes": True}


# Required: tells Pydantic to resolve the forward reference now that the
# class is fully defined.
ModuleTreeResponse.model_rebuild()