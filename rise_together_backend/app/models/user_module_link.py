from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Index, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.link import Link
    from app.models.module import Module
    from app.models.user import User


class UserModuleLink(Base):
    __tablename__ = "user_module_links"

    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id"), primary_key=True
    )
    module_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("modules.id"), primary_key=True
    )
    link_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("links.id"), primary_key=True
    )

    completed: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="false"
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="link_progress")
    module: Mapped["Module"] = relationship("Module", back_populates="link_progress")
    link: Mapped["Link"] = relationship("Link", back_populates="user_module_links")

    __table_args__ = (
        Index("ix_user_module_links_user_id", "user_id"),
        Index("ix_user_module_links_module_id", "module_id"),
        Index("ix_user_module_links_link_id", "link_id"),
        UniqueConstraint("user_id", "module_id", "link_id", name="uq_user_module_links"),
    )