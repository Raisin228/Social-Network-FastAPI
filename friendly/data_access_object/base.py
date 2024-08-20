from sqlalchemy import inspect, insert
from sqlalchemy.ext.asyncio import AsyncSession


class BaseDAO:
    model = None

    @classmethod
    async def add_one(cls, session: AsyncSession, values: dict):
        """Добавить один объект"""
        stmt = insert(cls.model).values(**values).returning(cls.model.id)
        result = await session.execute(stmt)
        await session.commit()

        obj_id = result.scalar_one()
        new_instance = cls.model(id=obj_id, **values)
        return new_instance

    @staticmethod
    def object_to_dict(obj) -> dict | None:
        """Преобразовать объект SQLAlchemy в dict"""
        return {c.key: getattr(obj, c.key) for c in inspect(obj).mapper.column_attrs} if obj else None
