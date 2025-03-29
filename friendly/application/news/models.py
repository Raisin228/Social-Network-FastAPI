import uuid
from datetime import datetime
from typing import List

from application.core.model_types import id_pk, userId_fk
from application.storage.models import File
from database import Base
from sqlalchemy import ForeignKey, String, text
from sqlalchemy.orm import Mapped, MappedColumn, relationship


class NewsFiles(Base):
    __tablename__ = "news_files"

    id: Mapped[id_pk]  # пришлось оставить для универсальности метода массовой вставки данных
    news_id: Mapped[uuid.UUID] = MappedColumn(
        ForeignKey("news.id", ondelete="CASCADE"), nullable=False, primary_key=True
    )
    file_id: Mapped[uuid.UUID] = MappedColumn(ForeignKey("file.id", ondelete="CASCADE"), nullable=False)


class News(Base):
    __tablename__ = "news"

    id: Mapped[id_pk]
    topic: Mapped[str | None] = MappedColumn(String(50), nullable=True)
    main_text: Mapped[str | None] = MappedColumn(String(2200), nullable=False)
    created_at: Mapped[datetime] = MappedColumn(server_default=text("TIMEZONE('utc', now())"), nullable=False)
    updated_at: Mapped[datetime | None] = MappedColumn(nullable=True)
    user_id: Mapped[userId_fk]
    attachments: Mapped[List[File]] = relationship("File", secondary="news_files", backref="news")


# TODO у всех таблиц идентификаторы с id поменять на @<table_name>
