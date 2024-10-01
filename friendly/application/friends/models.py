import uuid

import sqlalchemy as sa
from database import Base
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column


class Relations:
    FRIEND = "FRIEND"  # друзья видят посты друг друга в ленте
    NOT_APPROVE = "NOT_APPROVE"  # А отправил заявку и ожидает ответа


class Friend(Base):
    __tablename__ = "friend"
    __table_args__ = (sa.PrimaryKeyConstraint("user_id", "friend_id"),)

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("user.id"), nullable=False)
    friend_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("user.id"), nullable=False)
    relationship_type: Mapped[str] = mapped_column(String(11), server_default=Relations.NOT_APPROVE)
