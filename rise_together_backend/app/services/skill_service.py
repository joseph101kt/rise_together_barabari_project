from sqlalchemy.orm import Session

from app.repositories.skill_repository import SkillRepository
from app.schemas.shared import SkillResponse


class SkillService:
    def __init__(self, db: Session):
        self.skill_repo = SkillRepository(db)
        self.db = db

    def list_all(self) -> list[SkillResponse]:
        skills = self.skill_repo.get_all()
        return [SkillResponse.model_validate(s) for s in skills]

    def add_skills(self, user_id: int, skill_ids: list[int]) -> list[SkillResponse]:
        """
        Adds one or more skills to the user.
        Returns the user's full updated skill list.
        Raises 404 for any skill_id that doesn't exist.
        """
        for skill_id in skill_ids:
            self.skill_repo.add_user_skill(user_id, skill_id)
        self.db.commit()
        return self._get_user_skills(user_id)

    def remove_skill(self, user_id: int, skill_id: int) -> None:
        """Removes a single skill. Raises 404 if the user doesn't have it."""
        self.skill_repo.remove_user_skill(user_id, skill_id)
        self.db.commit()

    def _get_user_skills(self, user_id: int) -> list[SkillResponse]:
        skills = self.skill_repo.get_user_skills(user_id)
        return [SkillResponse.model_validate(s) for s in skills]