from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.skill import Skill, UserSkill


class SkillRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> list[Skill]:
        return self.db.query(Skill).order_by(Skill.name).all()

    def get_by_id(self, skill_id: int) -> Skill | None:
        return self.db.query(Skill).filter(Skill.id == skill_id).first()

    def get_user_skills(self, user_id: int) -> list[Skill]:
        return (
            self.db.query(Skill)
            .join(UserSkill, UserSkill.skill_id == Skill.id)
            .filter(UserSkill.user_id == user_id)
            .order_by(Skill.name)
            .all()
        )

    def add_user_skill(self, user_id: int, skill_id: int) -> None:
        """
        Adds a skill to a user. Silently ignores duplicates.
        Raises 404 if the skill_id doesn't exist.
        """
        if not self.get_by_id(skill_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Skill {skill_id} not found",
            )
        try:
            self.db.add(UserSkill(user_id=user_id, skill_id=skill_id))
            self.db.flush()
        except IntegrityError:
            self.db.rollback()  # already exists — that's fine

    def remove_user_skill(self, user_id: int, skill_id: int) -> None:
        """
        Removes a skill from a user.
        Raises 404 if the user doesn't have that skill.
        """
        row = (
            self.db.query(UserSkill)
            .filter(UserSkill.user_id == user_id, UserSkill.skill_id == skill_id)
            .first()
        )
        if row is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Skill {skill_id} not found on your profile",
            )
        self.db.delete(row)
        self.db.flush()