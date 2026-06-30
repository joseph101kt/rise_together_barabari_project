from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import DateTime, Enum, Index, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import UserRole

if TYPE_CHECKING:
    from app.models.education import Education
    from app.models.experience import Experience
    from app.models.link import Link
    from app.models.module import Module
    from app.models.module_star import ModuleStar
    from app.models.user_module import UserModule
    from app.models.user_module_link import UserModuleLink
    from app.models.user_profile import UserProfile
    from app.models.user_profile_link import UserProfileLink
    from app.models.skill import UserSkill


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role"),
        nullable=False,
        default=UserRole.learner,
        server_default=UserRole.learner.value,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    profile: Mapped[Optional["UserProfile"]] = relationship(
        "UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    education: Mapped[List["Education"]] = relationship(
        "Education", back_populates="user", cascade="all, delete-orphan"
    )
    experience: Mapped[List["Experience"]] = relationship(
        "Experience", back_populates="user", cascade="all, delete-orphan"
    )
    skills: Mapped[List["UserSkill"]] = relationship(
        "UserSkill", back_populates="user", cascade="all, delete-orphan"
    )
    profile_links: Mapped[List["UserProfileLink"]] = relationship(
        "UserProfileLink", back_populates="user", cascade="all, delete-orphan"
    )
    created_modules: Mapped[List["Module"]] = relationship(
        "Module", back_populates="creator", foreign_keys="Module.created_by"
    )
    created_links: Mapped[List["Link"]] = relationship(
        "Link", back_populates="creator"
    )
    module_progress: Mapped[List["UserModule"]] = relationship(
        "UserModule", back_populates="user", cascade="all, delete-orphan"
    )
    link_progress: Mapped[List["UserModuleLink"]] = relationship(
        "UserModuleLink", back_populates="user", cascade="all, delete-orphan"
    )
    starred_modules: Mapped[List["ModuleStar"]] = relationship(
        "ModuleStar", back_populates="user", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_users_email", "email", unique=True),
        Index("ix_users_role", "role"),
    )