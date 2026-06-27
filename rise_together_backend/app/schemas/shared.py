"""
Shared schemas used across more than one domain.
Import from here to avoid circular imports.
"""

from app.models.enums import LinkType
from pydantic import BaseModel, HttpUrl


class LinkResponse(BaseModel):
    """A link as it appears in module detail or user profile."""
    id: int
    title: str
    url: str
    description: str | None = None
    link_type: LinkType

    model_config = {"from_attributes": True}


class ModuleLinkResponse(LinkResponse):
    module_link_id: int

    og_title: str | None = None
    og_description: str | None = None
    og_image: str | None = None

    order_index: int


class ProfileLinkResponse(LinkResponse):
    """Link as it appears on a user's profile (GitHub, portfolio, etc.)."""
    pass


class SkillResponse(BaseModel):
    id: int
    name: str
    slug: str

    model_config = {"from_attributes": True}