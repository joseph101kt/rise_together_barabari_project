from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.shared import SkillResponse
from app.schemas.users import FullProfileResponse, ProfileUpdateRequest, PublicProfileResponse
from app.services.skill_service import SkillService
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


class AddSkillsBody(BaseModel):
    skill_ids: list[int]


# ---------------------------------------------------------------------------
# Profile
# ---------------------------------------------------------------------------

@router.get(
    "/self",
    response_model=FullProfileResponse,
    summary="Get the current user's full profile",
)
def get_my_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return UserService(db).get_my_profile(current_user.id)


@router.patch(
    "/self",
    response_model=FullProfileResponse,
    summary="Update profile, education, experience, or profile links",
)
def update_my_profile(
    request: ProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return UserService(db).update_profile(current_user.id, request)


@router.get(
    "/{user_id}",
    response_model=PublicProfileResponse,
    summary="Get another user's public profile",
)
def get_user_profile(user_id: int, db: Session = Depends(get_db)):
    return UserService(db).get_public_profile(user_id)


# ---------------------------------------------------------------------------
# Skills
# ---------------------------------------------------------------------------

@router.post(
    "/{user_id}/skills",
    response_model=list[SkillResponse],
    summary="Add one or more skills to a user's profile",
)
def add_skills(
    user_id: int,
    body: AddSkillsBody,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.id != user_id:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Cannot modify another user's skills.")
    return SkillService(db).add_skills(user_id, body.skill_ids)


@router.delete(
    "/{user_id}/skills/{skill_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove a skill from a user's profile",
)
def remove_skill(
    user_id: int,
    skill_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.id != user_id:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Cannot modify another user's skills.")
    SkillService(db).remove_skill(user_id, skill_id)