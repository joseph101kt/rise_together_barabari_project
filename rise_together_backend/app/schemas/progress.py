from datetime import datetime

from pydantic import BaseModel

from app.models.enums import LinkType, ModuleType, UserModuleStatus


# ---------------------------------------------------------------------------
# Request bodies
# ---------------------------------------------------------------------------

class ModuleProgressRequest(BaseModel):
    status: UserModuleStatus


class LinkProgressRequest(BaseModel):
    completed: bool


# ---------------------------------------------------------------------------
# Response bodies
# ---------------------------------------------------------------------------

class ModuleProgressResponse(BaseModel):
    """Returned after PATCH /modules/:id/progress."""
    module_id: int
    user_id: int
    status: UserModuleStatus
    started_at: datetime | None = None
    completed_at: datetime | None = None

    model_config = {"from_attributes": True}


class LinkProgressResponse(BaseModel):
    """Returned after PATCH /modules/:moduleId/links/:linkId/progress."""
    module_id: int
    link_id: int
    user_id: int
    completed: bool
    completed_at: datetime | None = None

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Submissions view — GET /users/me/submissions
# ---------------------------------------------------------------------------

class SubmissionModuleResponse(BaseModel):
    """Lightweight module info shown alongside a submission."""
    id: int
    title: str
    module_type: ModuleType
    description: str | None = None


class SubmissionLinkResponse(BaseModel):
    """A single submission link with the user's completion state."""
    id: int
    title: str
    url: str
    link_type: LinkType
    completed: bool
    completed_at: datetime | None = None


class UserSubmissionsResponse(BaseModel):
    """
    One entry per module that has at least one submission link.
    Maps to ProgressRepository.get_user_submissions().
    """
    module: SubmissionModuleResponse
    submissionLinks: list[SubmissionLinkResponse]