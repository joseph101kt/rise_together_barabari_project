from datetime import date, datetime

from pydantic import BaseModel, EmailStr

from app.models.enums import LinkType, UserRole
from app.schemas.shared import ProfileLinkResponse, SkillResponse


# ---------------------------------------------------------------------------
# Sub-schemas used inside profile responses
# ---------------------------------------------------------------------------

class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: UserRole
    created_at: datetime

    model_config = {"from_attributes": True}


class PublicUserResponse(BaseModel):
    """Same as UserResponse but without email — used on public profile pages."""
    id: int
    name: str
    role: UserRole
    created_at: datetime

    model_config = {"from_attributes": True}


class ProfileResponse(BaseModel):
    headline: str | None = None
    bio: str | None = None

    model_config = {"from_attributes": True}


class EducationResponse(BaseModel):
    id: int
    institution: str
    degree: str | None = None
    field_of_study: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    description: str | None = None

    model_config = {"from_attributes": True}


class ExperienceResponse(BaseModel):
    id: int
    company: str
    role: str
    description: str | None = None
    start_date: date | None = None
    end_date: date | None = None

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Full profile responses
# ---------------------------------------------------------------------------

class FullProfileResponse(BaseModel):
    """
    Returned by GET /users/me.
    Includes email and all private fields.
    Maps directly to ProfileRepository.get_full_profile(public=False).
    """
    user: UserResponse
    profile: ProfileResponse
    education: list[EducationResponse]
    experience: list[ExperienceResponse]
    skills: list[SkillResponse]
    profileLinks: list[ProfileLinkResponse]


class PublicProfileResponse(BaseModel):
    """
    Returned by GET /users/:id.
    Email is stripped. Everything else is the same shape.
    Maps directly to ProfileRepository.get_full_profile(public=True).
    """
    user: PublicUserResponse
    profile: ProfileResponse
    education: list[EducationResponse]
    experience: list[ExperienceResponse]
    skills: list[SkillResponse]
    profileLinks: list[ProfileLinkResponse]


# ---------------------------------------------------------------------------
# Update request — PATCH /users/me
# All top-level fields are optional so the client can send partial updates.
# education and experience arrays are a full replace when provided.
# ---------------------------------------------------------------------------

class ProfileUpdateData(BaseModel):
    headline: str | None = None
    bio: str | None = None


class EducationRequest(BaseModel):
    institution: str
    degree: str | None = None
    field_of_study: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    description: str | None = None


class ExperienceRequest(BaseModel):
    company: str
    role: str
    description: str | None = None
    start_date: date | None = None
    end_date: date | None = None


class ProfileLinkRequest(BaseModel):
    title: str
    url: str
    link_type: LinkType
    description: str | None = None


class ProfileUpdateRequest(BaseModel):
    """
    Body for PATCH /users/me.
    All sections are optional — only send the ones you want to update.
    Sending education: [] will clear all education entries.
    """
    profile: ProfileUpdateData | None = None
    education: list[EducationRequest] | None = None
    experience: list[ExperienceRequest] | None = None
    profileLinks: list[ProfileLinkRequest] | None = None