import uuid

import sqlalchemy as sa
from database import Base
from sqlalchemy import Column, ForeignKey, Index, String, func
from sqlalchemy.orm import Mapped, mapped_column


class Relations:
    FRIEND = "FRIEND"  # друзья видят посты друг друга в ленте
    NOT_APPROVE = "NOT_APPROVE"  # А отправил заявку и ожидает ответа


class Friend(Base):
    __tablename__ = "friend"

    user_id: Mapped[uuid.UUID] = Column(ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    friend_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    relationship_type: Mapped[str] = mapped_column(String(11), server_default=Relations.NOT_APPROVE)

    __table_args__ = (
        sa.PrimaryKeyConstraint("user_id", "friend_id"),
        Index(
            "uq_user_id_friend_id_permuted",
            func.least(user_id, friend_id),
            func.greatest(user_id, friend_id),
            unique=True,
        ),
    )
