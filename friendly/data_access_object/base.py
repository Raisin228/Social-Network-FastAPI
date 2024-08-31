from sqlalchemy import inspect, insert, select, delete
from sqlalchemy.ext.asyncio import AsyncSession


class BaseDAO:
    model = None

    @classmethod
    async def find_by_filter(cls, session: AsyncSession, find_by: dict | None = None) -> None | dict | list[dict]:
        """Поиск по фильтрам или получить все записи"""
        query = select(cls.model).filter_by(**find_by)
        data = await session.execute(query)
        result = data.scalars().all()

        if len(result) == 0:
            return None
        result = [cls.object_to_dict(obj) for obj in result]
        if len(result) == 1:
            return result[0]
        return result

    @classmethod
    async def add_one(cls, session: AsyncSession, values: dict) -> model:
        """Добавить один объект"""
        stmt = insert(cls.model).values(**values).returning(cls.model.id)
        result = await session.execute(stmt)
        await session.commit()

        obj_id = result.scalar_one()
        new_instance = cls.model(id=obj_id, **values)
        return new_instance

    @classmethod
    async def delete_by_filter(cls, session: AsyncSession, find_by: dict) -> None:
        """Удалить все записи, удовлетворяющие условиям фильтрации"""
        stmt = delete(cls.model).filter_by(**find_by)
        await session.execute(stmt)
        await session.commit()

    @staticmethod
    def object_to_dict(obj) -> dict | None:
        """Преобразовать объект SQLAlchemy в dict"""
        return {c.key: getattr(obj, c.key) for c in inspect(obj).mapper.column_attrs} if obj else None
