from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.module import Module
    from app.models.skill import Skill


class ModuleSkill(Base):
    __tablename__ = "module_skills"

    module_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("modules.id"), primary_key=True
    )
    skill_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("skills.id"), primary_key=True
    )

    # Relationships
    module: Mapped["Module"] = relationship("Module", back_populates="module_skills")
    skill: Mapped["Skill"] = relationship("Skill", back_populates="module_skills")

    __table_args__ = (
        UniqueConstraint("module_id", "skill_id", name="uq_module_skills"),
    )