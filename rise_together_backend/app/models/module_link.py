from typing import TYPE_CHECKING, List

from sqlalchemy import BigInteger, ForeignKey, Index, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.link import Link
    from app.models.module import Module
    from app.models.user_module_link import UserModuleLink


class ModuleLink(Base):
    __tablename__ = "module_links"

    # Surrogate PK — lets user_module_links reference a single column
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    module_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("modules.id"), nullable=False
    )
    link_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("links.id"), nullable=False
    )

    order_index: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default="0"
    )

    # Relationships
    module: Mapped["Module"] = relationship("Module", back_populates="module_links")
    link: Mapped["Link"] = relationship("Link", back_populates="module_links")
    user_module_links: Mapped[List["UserModuleLink"]] = relationship(
        "UserModuleLink", back_populates="module_link", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_module_links_module_id", "module_id"),
        Index("ix_module_links_link_id", "link_id"),
        # A link can only appear once per module
        UniqueConstraint("module_id", "link_id", name="uq_module_links_module_link"),
        # Order must be unique within a module
        UniqueConstraint("module_id", "order_index", name="uq_module_links_order"),
    )