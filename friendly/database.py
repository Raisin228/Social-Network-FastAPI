from typing import AsyncGenerator, Dict

from config import settings
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

async_engine = create_async_engine(
    url=settings.db_url_asyncpg, echo=False, pool_size=5, max_overflow=10
)

session_factory = async_sessionmaker(async_engine)


class Base(DeclarativeBase):
    __abstract__ = True

    def to_dict(self) -> Dict:
        """Преобразование объекта SQLAlchemy в dict"""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Генератор асинхронных подключений к бд (сессий)"""
    async with session_factory() as session:
        yield session


class Transaction:
    def __init__(self):
        self.session: AsyncSession | None = None

    async def __aenter__(self):
        self.session = session_factory()
        self.session = await self.session.__aenter__()
        await self.session.begin()
        return self.session

    async def __aexit__(self, exception_type, exception, traceback):
        if exception:
            await self.session.rollback()
        else:
            await self.session.commit()
        await self.session.__aexit__(exception_type, exception, traceback)
