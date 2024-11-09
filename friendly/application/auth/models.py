import datetime
from typing import List

from application.core.model_types import id_pk
from database import Base
from sqlalchemy import CheckConstraint, String, inspect
from sqlalchemy.orm import Mapped, MappedColumn


class User(Base):
    __tablename__ = "user"
    id: Mapped[id_pk]
    first_name: Mapped[str | None] = MappedColumn(String(32))
    last_name: Mapped[str | None] = MappedColumn(String(32))
    birthday: Mapped[datetime.date | None]
    sex: Mapped[str | None] = MappedColumn(String(6))
    nickname: Mapped[str] = MappedColumn(String(39), nullable=False, unique=True)
    email: Mapped[str] = MappedColumn(String(100), nullable=False, unique=True)
    password: Mapped[str] = MappedColumn(String(60), nullable=False)

    __table_args__ = (
        CheckConstraint("char_length(first_name) >= 2", name="min_first_name_len_2"),
        CheckConstraint("char_length(nickname) >= 5", name="min_nick_len_5"),
        CheckConstraint("birthday >= DATE '1900-01-01' AND birthday <= CURRENT_DATE", name="check_birthday_1900"),
        CheckConstraint("sex IN ('Male', 'Female')", name="check_gender"),
        CheckConstraint("char_length(password) >= 6 OR char_length(password) = 0", name="min_pass_len_6"),
    )

    @classmethod
    def get_column_names(cls) -> List[str]:
        """Получить названия всех столбцов"""
        return [column.name for column in inspect(cls).c]
