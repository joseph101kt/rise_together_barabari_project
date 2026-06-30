from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.profile_repository import ProfileRepository
from app.schemas.users import FullProfileResponse, ProfileUpdateRequest, PublicProfileResponse


class UserService:
    def __init__(self, db: Session):
        self.profile_repo = ProfileRepository(db)
        self.db = db

    def get_my_profile(self, user_id: int) -> FullProfileResponse:
        data = self.profile_repo.get_full_profile(user_id, public=False)
        if data is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return FullProfileResponse(**data)

    def get_public_profile(self, user_id: int) -> PublicProfileResponse:
        data = self.profile_repo.get_full_profile(user_id, public=True)
        if data is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return PublicProfileResponse(**data)

    def update_profile(self, user_id: int, request: ProfileUpdateRequest) -> FullProfileResponse:
        """
        Each section of the request is optional.
        Only the sections that are present in the request body are updated.
        """
        if request.profile is not None:
            self.profile_repo.upsert_profile(
                user_id=user_id,
                headline=request.profile.headline,
                bio=request.profile.bio,
            )

        if request.education is not None:
            self.profile_repo.upsert_education(
                user_id=user_id,
                entries=[e.model_dump(exclude_none=True) for e in request.education],
            )

        if request.experience is not None:
            self.profile_repo.upsert_experience(
                user_id=user_id,
                entries=[e.model_dump(exclude_none=True) for e in request.experience],
            )

        if request.profileLinks is not None:
            self.profile_repo.upsert_profile_links(
                user_id=user_id,
                links=[lnk.model_dump(exclude_none=True) for lnk in request.profileLinks],
            )

        self.db.commit()

        # Return the fresh profile after all updates
        return self.get_my_profile(user_id)