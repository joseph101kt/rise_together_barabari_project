from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, DateTime, ForeignKey, Index, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.module import Module
    from app.models.user import User


class ModuleStar(Base):
    __tablename__ = "module_stars"

    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id"), primary_key=True
    )
    module_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("modules.id"), primary_key=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="starred_modules")
    module: Mapped["Module"] = relationship("Module", back_populates="stars")

    __table_args__ = (
        Index("ix_module_stars_module_id", "module_id"),
        UniqueConstraint("user_id", "module_id", name="uq_module_stars"),
    )