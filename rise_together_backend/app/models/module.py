from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import (
    BigInteger,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    Text,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import ModuleType

if TYPE_CHECKING:
    from app.models.module_link import ModuleLink
    from app.models.module_skill import ModuleSkill
    from app.models.module_star import ModuleStar
    from app.models.user import User
    from app.models.user_module import UserModule
    from app.models.user_module_link import UserModuleLink


class Module(Base):
    __tablename__ = "modules"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    parent_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("modules.id"), nullable=True
    )

    module_type: Mapped[ModuleType] = mapped_column(
        Enum(ModuleType, name="module_type"), nullable=False
    )

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    estimated_completion_time: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_by: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id"), nullable=False
    )

    order_index: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")

    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    # Self-referential relationship
    parent: Mapped[Optional["Module"]] = relationship(
        "Module", back_populates="children", remote_side="Module.id"
    )
    children: Mapped[List["Module"]] = relationship(
        "Module", back_populates="parent", order_by="Module.order_index"
    )

    # Other relationships
    creator: Mapped["User"] = relationship(
        "User", back_populates="created_modules", foreign_keys=[created_by]
    )
    module_links: Mapped[List["ModuleLink"]] = relationship(
        "ModuleLink", back_populates="module", cascade="all, delete-orphan",
        order_by="ModuleLink.order_index"
    )
    module_skills: Mapped[List["ModuleSkill"]] = relationship(
        "ModuleSkill", back_populates="module", cascade="all, delete-orphan"
    )
    user_progress: Mapped[List["UserModule"]] = relationship(
        "UserModule", back_populates="module", cascade="all, delete-orphan"
    )
    link_progress: Mapped[List["UserModuleLink"]] = relationship(
        "UserModuleLink", back_populates="module", cascade="all, delete-orphan"
    )
    stars: Mapped[List["ModuleStar"]] = relationship(
        "ModuleStar", back_populates="module", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_modules_parent_id", "parent_id"),
        Index("ix_modules_created_by", "created_by"),
        Index("ix_modules_module_type", "module_type"),
        UniqueConstraint("parent_id", "order_index", name="uq_modules_parent_order"),
    )