from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import DeclarativeMeta

Base: DeclarativeMeta = declarative_base()
metadata = Base.metadata


class User(Base):
    """Таблица пользователя в бд"""
    __tablename__ = "user"
    id: int = Column(Integer, primary_key=True)
    first_name: str = Column(String, nullable=True)
    last_name: str = Column(String, nullable=True)
    username: str = Column(String, unique=True, nullable=False)

    email: str = Column(String(length=320), unique=True, index=True, nullable=False)
    hashed_password: str = Column(String(length=1024), nullable=False)
    is_active: bool = Column(Boolean, default=True, nullable=False)
    is_superuser: bool = Column(Boolean, default=False, nullable=False)
    is_verified: bool = Column(Boolean, default=False, nullable=False)
