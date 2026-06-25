from typing import TYPE_CHECKING, List

from sqlalchemy import BigInteger, ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.module_skill import ModuleSkill
    from app.models.user import User


class Skill(Base):
    __tablename__ = "skills"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)

    # Relationships
    user_skills: Mapped[List["UserSkill"]] = relationship(
        "UserSkill", back_populates="skill"
    )
    module_skills: Mapped[List["ModuleSkill"]] = relationship(
        "ModuleSkill", back_populates="skill"
    )

    __table_args__ = (Index("ix_skills_slug", "slug", unique=True),)


class UserSkill(Base):
    __tablename__ = "user_skills"

    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id"), primary_key=True
    )
    skill_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("skills.id"), primary_key=True
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="skills")
    skill: Mapped["Skill"] = relationship("Skill", back_populates="user_skills")

    __table_args__ = (
        UniqueConstraint("user_id", "skill_id", name="uq_user_skills"),
    )