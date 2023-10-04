from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable
from sqlalchemy import String, Boolean, Column, Integer, MetaData
from sqlalchemy.orm import declarative_base


# мета данные следят за разницей между моделью и таблицей в бд -> далее помогает делать ревизию и миграции
metadata = MetaData()
Base = declarative_base(metadata=metadata)


class User(SQLAlchemyBaseUserTable[int], Base):
    """user model in db"""
    # мои поля
    __tablename__ = 'user'
    id: int = Column(Integer, primary_key=True)
    first_name: str = Column(String, nullable=True)
    last_name: str = Column(String, nullable=True)
    username: str = Column(String, unique=True, nullable=False)

    # default поля
    email: str = Column(String(length=320), unique=True, index=True, nullable=False)
    hashed_password: str = Column(String(length=1024), nullable=False)
    is_active: bool = Column(Boolean, default=True, nullable=False)
    is_superuser: bool = Column(Boolean, default=False, nullable=False)
    is_verified: bool = Column(Boolean, default=False, nullable=False)
