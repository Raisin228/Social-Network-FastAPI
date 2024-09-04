from database import Base, int_pk
from sqlalchemy import String
from sqlalchemy.orm import Mapped, MappedColumn


class User(Base):
    __tablename__ = "user"
    id: Mapped[int_pk]
    first_name: Mapped[str | None] = MappedColumn(String(32))
    last_name: Mapped[str | None] = MappedColumn(String(32))
    email: Mapped[str] = MappedColumn(String(100), nullable=False, unique=True)
    password: Mapped[str] = MappedColumn(String(100), nullable=False)
