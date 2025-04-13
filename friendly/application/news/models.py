import uuid
from datetime import datetime
from enum import Enum
from typing import List

from application.core.model_types import id_pk, userId_fk
from application.storage.models import File
from database import Base
from sqlalchemy import Enum as AlchemyEnum
from sqlalchemy import ForeignKey, String, UniqueConstraint, text
from sqlalchemy.orm import Mapped, MappedColumn, relationship


class NewsFiles(Base):
    __tablename__ = "news_files"

    id: Mapped[id_pk]  # пришлось оставить для универсальности метода массовой вставки данных
    news_id: Mapped[uuid.UUID] = MappedColumn(
        ForeignKey("news.id", ondelete="CASCADE"), nullable=False
    )
    file_id: Mapped[uuid.UUID] = MappedColumn(
        ForeignKey("file.id", ondelete="CASCADE"), nullable=False
    )


class News(Base):
    __tablename__ = "news"

    id: Mapped[id_pk]
    topic: Mapped[str | None] = MappedColumn(String(50), nullable=True)
    main_text: Mapped[str | None] = MappedColumn(String(2200), nullable=False)
    created_at: Mapped[datetime] = MappedColumn(
        server_default=text("TIMEZONE('utc', now())"), nullable=False
    )
    updated_at: Mapped[datetime | None] = MappedColumn(nullable=True)
    user_id: Mapped[userId_fk]
    attachments: Mapped[List[File]] = relationship(
        "File", secondary="news_files", backref="news", lazy="subquery"
    )


class ReactionType(str, Enum):
    LIKE = "LIKE"
    LOVE = "LOVE"
    FIRE = "FIRE"
    SAD = "SAD"

    def convert_letter_type_to_emoji(self) -> str:
        emoji_converter = {
            ReactionType.LIKE: "👍",
            ReactionType.LOVE: "❤️",
            ReactionType.FIRE: "🔥",
            ReactionType.SAD: "😢",
        }
        return emoji_converter.get(self, "😢")


class Reaction(Base):
    __tablename__ = "reactionType"

    id: Mapped[id_pk]
    type: Mapped[ReactionType] = MappedColumn(
        AlchemyEnum(ReactionType, name="reaction_type_enum"), nullable=False, unique=True
    )


class UserNewsReaction(Base):
    __tablename__ = "news_reaction"
    __table_args__ = (UniqueConstraint("news_id", "user_id"),)

    id: Mapped[id_pk]
    news_id: Mapped[uuid.UUID] = MappedColumn(
        ForeignKey("news.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[userId_fk]
    reaction_type_id: MappedColumn[uuid.UUID] = MappedColumn(
        ForeignKey("reactionType.id", ondelete="CASCADE"), nullable=False
    )


# TODO у всех таблиц идентификаторы с id поменять на @<table_name>
