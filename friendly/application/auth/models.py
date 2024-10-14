import datetime
from typing import List

from application.core.model_types import id_pk
from database import Base
from sqlalchemy import String, inspect
from sqlalchemy.orm import Mapped, MappedColumn


class User(Base):
    __tablename__ = "user"
    id: Mapped[id_pk]
    first_name: Mapped[str | None] = MappedColumn(String(32))
    last_name: Mapped[str | None] = MappedColumn(String(32))
    birthday: Mapped[datetime.date | None]
    sex: Mapped[str | None] = MappedColumn(String(5))
    nickname: Mapped[str] = MappedColumn(String(39), nullable=False, unique=True)
    email: Mapped[str] = MappedColumn(String(100), nullable=False, unique=True)
    password: Mapped[str] = MappedColumn(String(100), nullable=False)

    @classmethod
    def get_column_names(cls) -> List[str]:
        """Получить названия всех столбцов"""
        return [column.name for column in inspect(cls).c]
