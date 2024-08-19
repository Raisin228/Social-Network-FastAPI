from sqlalchemy import String, inspect
from sqlalchemy.orm import MappedColumn, Mapped
from database import Base, int_pk


class User(Base):
    __tablename__ = "user"
    id: Mapped[int_pk]
    first_name: Mapped[str | None] = MappedColumn(String(100))
    last_name: Mapped[str | None] = MappedColumn(String(100))
    login: Mapped[str] = MappedColumn(String(100), nullable=False, unique=True)
    password: Mapped[str] = MappedColumn(String(100), nullable=False)
