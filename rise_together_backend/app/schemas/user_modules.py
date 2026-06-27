from datetime import datetime

from pydantic import BaseModel

from app.models.enums import LinkType, UserModuleStatus


# ---------------------------------------------------------------------------
# Submitted link (what the user provided for a module-link slot)
# ---------------------------------------------------------------------------

class UserModuleLinkResponse(BaseModel):
    """
    A single user_module_link row, enriched with the slot's order_index
    and the link the user actually submitted.
    """
    module_link_id: int
    order_index: int          # from module_links — preserves slot ordering
    link_id: int
    link_title: str
    link_url: str
    link_type: LinkType
    completed: bool
    completed_at: datetime | None = None

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# user_module
# ---------------------------------------------------------------------------

class UserModuleResponse(BaseModel):
    """
    Returned by GET /user_modules and GET /user_modules/{module_id}.
    Includes the progress row plus all submission links the user has filed.
    """
    user_id: int
    module_id: int
    status: UserModuleStatus
    started_at: datetime | None = None
    completed_at: datetime | None = None

    submitted_links: list[UserModuleLinkResponse] = []

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Request bodies
# ---------------------------------------------------------------------------

class UserModuleCreateRequest(BaseModel):
    """Body for POST /user_modules — starts tracking a module."""
    module_id: int


class UserModuleLinkCreateRequest(BaseModel):
    """
    Body for POST /user_modules/{module_id}/links.
    The caller must specify which module-link slot they are submitting against.
    link_type is always submission — callers cannot override it.
    """
    module_link_id: int
    url: str
    title: str


class UserModuleLinkPatchRequest(BaseModel):
    """Body for PATCH /user_modules/{module_id}/links/{module_link_id}."""
    completed: bool