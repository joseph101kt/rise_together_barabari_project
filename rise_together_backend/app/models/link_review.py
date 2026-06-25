from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import BigInteger, DateTime, Enum, ForeignKey, Index, Integer, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import LinkReviewStatus

if TYPE_CHECKING:
    from app.models.link import Link
    from app.models.user import User


class LinkReview(Base):
    __tablename__ = "link_reviews"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    link_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("links.id"), nullable=False
    )
    reviewer_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id"), nullable=False
    )

    rating: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    status: Mapped[LinkReviewStatus] = mapped_column(
        Enum(LinkReviewStatus, name="link_review_status"),
        nullable=False,
        default=LinkReviewStatus.pending,
        server_default=LinkReviewStatus.pending.value,
    )

    review_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    link: Mapped["Link"] = relationship("Link", back_populates="reviews")
    reviewer: Mapped["User"] = relationship("User")

    __table_args__ = (
        Index("ix_link_reviews_link_id", "link_id"),
        Index("ix_link_reviews_reviewer_id", "reviewer_id"),
        Index("ix_link_reviews_status", "status"),
    )