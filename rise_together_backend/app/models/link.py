from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import BigInteger, DateTime, Enum, ForeignKey, Index, Text, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import LinkType

if TYPE_CHECKING:
    from app.models.link_review import LinkReview
    from app.models.module_link import ModuleLink
    from app.models.user import User
    from app.models.user_module_link import UserModuleLink
    from app.models.user_profile_link import UserProfileLink


class Link(Base):
    __tablename__ = "links"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    url: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    link_type: Mapped[LinkType] = mapped_column(
        Enum(LinkType, name="link_type"), nullable=False
    )

    og_title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    og_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    og_image: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    og_fetched_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    created_by: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("users.id"), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    creator: Mapped[Optional["User"]] = relationship("User", back_populates="created_links")
    module_links: Mapped[List["ModuleLink"]] = relationship(
        "ModuleLink", back_populates="link", cascade="all, delete-orphan"
    )
    profile_links: Mapped[List["UserProfileLink"]] = relationship(
        "UserProfileLink", back_populates="link", cascade="all, delete-orphan"
    )
    user_module_links: Mapped[List["UserModuleLink"]] = relationship(
        "UserModuleLink", back_populates="link", cascade="all, delete-orphan"
    )
    reviews: Mapped[List["LinkReview"]] = relationship(
        "LinkReview", back_populates="link", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_links_created_by", "created_by"),
        Index("ix_links_link_type", "link_type"),
    )