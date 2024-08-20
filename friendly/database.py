from typing import Annotated

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import MappedColumn

from config import settings

async_engine = create_async_engine(
    url=settings.db_url_asyncpg,
    echo=False,
    pool_size=5,
    max_overflow=10
)

session_factory = async_sessionmaker(async_engine)

int_pk = Annotated[int, MappedColumn(primary_key=True)]


class Base(DeclarativeBase):
    __abstract__ = True

    def to_dict(self) -> dict:
        """Преобразование объекта SQLAlchemy в dict"""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


async def get_async_session() -> AsyncSession:
    async with session_factory() as session:
        yield session
