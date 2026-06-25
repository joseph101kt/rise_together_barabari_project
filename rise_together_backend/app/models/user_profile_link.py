from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.link import Link
    from app.models.user import User


class UserProfileLink(Base):
    __tablename__ = "user_profile_links"

    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id"), primary_key=True
    )
    link_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("links.id"), primary_key=True
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="profile_links")
    link: Mapped["Link"] = relationship("Link", back_populates="profile_links")