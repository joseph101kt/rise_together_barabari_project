from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.models.enums import ModuleType
from app.schemas.progress import ModuleProgressResponse
from app.schemas.shared import ModuleLinkResponse, SkillResponse


class ModuleResponse(BaseModel):
    """
    Recursive module response used throughout the API.

    Returned by:
    - GET /modules
    - GET /modules/{module_id}

    Every module node has the exact same structure, allowing the frontend
    to recursively render the tree without any special cases.
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

    progress: ModuleProgressResponse | None = None

    direct_skills: list[SkillResponse] = Field(default_factory=list)
    skills: list[SkillResponse] = Field(default_factory=list)

    links: list[ModuleLinkResponse] = Field(default_factory=list)

    children: list["ModuleResponse"] = Field(default_factory=list)

    model_config = {
        "from_attributes": True,
    }


ModuleResponse.model_rebuild()