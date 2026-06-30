from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import BigInteger, DateTime, Enum, ForeignKey, Index, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import UserModuleStatus

if TYPE_CHECKING:
    from app.models.module import Module
    from app.models.user import User


class UserModule(Base):
    __tablename__ = "user_modules"

    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id"), primary_key=True
    )
    module_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("modules.id"), primary_key=True
    )

    status: Mapped[UserModuleStatus] = mapped_column(
        Enum(UserModuleStatus, name="user_module_status"),
        nullable=False,
        default=UserModuleStatus.in_progress,
        server_default=UserModuleStatus.in_progress.value,
    )

    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="module_progress")
    module: Mapped["Module"] = relationship("Module", back_populates="user_progress")

    __table_args__ = (
        Index("ix_user_modules_user_id", "user_id"),
        Index("ix_user_modules_module_id", "module_id"),
        Index("ix_user_modules_status", "status"),
        UniqueConstraint("user_id", "module_id", name="uq_user_modules"),
    )