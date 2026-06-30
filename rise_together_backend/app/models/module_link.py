from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import BigInteger, Enum, ForeignKey, Index, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import SubLinkType

if TYPE_CHECKING:
    from app.models.link import Link
    from app.models.module import Module
    from app.models.user_module_link import UserModuleLink


class ModuleLink(Base):
    __tablename__ = "module_links"

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

    # Only meaningful when the slot's link_type == 'submission'.
    # Constrains what kind of URL the user must submit.
    # NULL means any URL is acceptable.
    sub_link_type: Mapped[Optional[SubLinkType]] = mapped_column(
        Enum(SubLinkType, name="sub_link_type"), nullable=True
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
        UniqueConstraint("module_id", "link_id", name="uq_module_links_module_link"),
        UniqueConstraint("module_id", "order_index", name="uq_module_links_order"),
    )