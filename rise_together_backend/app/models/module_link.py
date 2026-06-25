from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, ForeignKey, Index, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.link import Link
    from app.models.module import Module


class ModuleLink(Base):
    __tablename__ = "module_links"

    module_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("modules.id"), primary_key=True
    )
    link_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("links.id"), primary_key=True
    )

    order_index: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default="0"
    )

    # Relationships
    module: Mapped["Module"] = relationship("Module", back_populates="module_links")
    link: Mapped["Link"] = relationship("Link", back_populates="module_links")

    __table_args__ = (
        Index("ix_module_links_module_id", "module_id"),
        Index("ix_module_links_link_id", "link_id"),
        UniqueConstraint("module_id", "order_index", name="uq_module_links_order"),
    )