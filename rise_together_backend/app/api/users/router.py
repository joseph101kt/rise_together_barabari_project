from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.progress import UserSubmissionsResponse
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
    "/me",
    response_model=FullProfileResponse,
    summary="Get the current user's full profile",
)
def get_my_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return UserService(db).get_my_profile(current_user.id)


@router.patch(
    "/me",
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
# Skills  (POST /users/me/skills  and  DELETE /users/me/skills/:skillId)
# ---------------------------------------------------------------------------

@router.post(
    "/me/skills",
    response_model=list[SkillResponse],
    summary="Add one or more skills to the current user's profile",
)
def add_skills(
    body: AddSkillsBody,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return SkillService(db).add_skills(current_user.id, body.skill_ids)


@router.delete(
    "/me/skills/{skill_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove a skill from the current user's profile",
)
def remove_skill(
    skill_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    SkillService(db).remove_skill(current_user.id, skill_id)



