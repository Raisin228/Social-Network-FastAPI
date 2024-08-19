from sqlalchemy import select, inspect
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession


class BaseDAO:
    model = None

    @classmethod
    async def find_all(cls, session: AsyncSession):
        """Получить все записи"""
        query = select(cls.model)
        all_data = await session.execute(query)
        return all_data.scalars().all()

    @classmethod
    async def add_one(cls, session: AsyncSession, values: dict):
        """Добавить один объект"""
        new_instance = cls.model(**values)
        session.add(new_instance)
        try:
            await session.commit()
        except SQLAlchemyError as e:
            await session.rollback()
            raise e
        return new_instance

    @staticmethod
    def object_to_dict(obj) -> dict | None:
        """Преобразовать объект SQLAlchemy в dict"""
        return {c.key: getattr(obj, c.key) for c in inspect(obj).mapper.column_attrs} if obj else None
