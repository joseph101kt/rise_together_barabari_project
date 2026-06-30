from datetime import datetime

from pydantic import BaseModel

from app.models.enums import LinkType, SubLinkType, UserModuleStatus


class UserModuleLinkResponse(BaseModel):
    module_link_id: int
    order_index: int
    link_id: int
    link_title: str
    link_url: str
    link_type: LinkType
    sub_link_type: SubLinkType | None = None
    og_title: str | None = None        
    og_description: str | None = None  
    og_image: str | None = None        
    completed: bool
    completed_at: datetime | None = None

    model_config = {"from_attributes": True}


class UserModuleResponse(BaseModel):
    user_id: int
    module_id: int
    status: UserModuleStatus
    started_at: datetime | None = None
    completed_at: datetime | None = None
    submitted_links: list[UserModuleLinkResponse] = []

    model_config = {"from_attributes": True}


class UserModuleCreateRequest(BaseModel):
    module_id: int


class UserModuleLinkCreateRequest(BaseModel):
    module_link_id: int
    url: str
    title: str


class UserModuleLinkPatchRequest(BaseModel):
    completed: bool