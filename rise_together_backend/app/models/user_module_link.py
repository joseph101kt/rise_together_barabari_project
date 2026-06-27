from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.link import Link
    from app.models.module_link import ModuleLink
    from app.models.user import User


class UserModuleLink(Base):
    __tablename__ = "user_module_links"

    # PK: one row per user per module-link slot
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id"), primary_key=True
    )
    module_link_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("module_links.id"), primary_key=True
    )

    # The link the user actually submitted for this slot
    link_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("links.id"), nullable=False
    )

    completed: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="false"
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="link_progress")
    module_link: Mapped["ModuleLink"] = relationship(
        "ModuleLink", back_populates="user_module_links"
    )
    link: Mapped["Link"] = relationship("Link", back_populates="user_module_links")

    __table_args__ = (
        Index("ix_user_module_links_user_id", "user_id"),
        Index("ix_user_module_links_module_link_id", "module_link_id"),
        Index("ix_user_module_links_link_id", "link_id"),
        # Enforce one submission per user per slot at the DB level
        UniqueConstraint("user_id", "module_link_id", name="uq_user_module_links"),
    )