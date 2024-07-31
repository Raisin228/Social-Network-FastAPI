from typing import Annotated

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import MappedColumn

from config import settings

async_engine = create_async_engine(
    url=settings.db_url_asyncpg,
    echo=True,
    pool_size=5,
    max_overflow=10
)

session_factory = async_sessionmaker(async_engine)

int_pk = Annotated[int, MappedColumn(primary_key=True)]


class Base(DeclarativeBase):
    __abstract__ = True


async def get_async_session():
    async with session_factory() as session:
        yield session
