from fastapi import HTTPException
from sqlalchemy import delete, insert, inspect, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status


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
        await session.execute(stmt)
        await session.commit()

        return cls.model(**values)

    @classmethod
    async def update_row(cls, session: AsyncSession, new_data: dict, filter_parameters: dict):
        """Выбрать запис(ь|и) и обновить поля"""
        data_without_none = {key: value for key, value in new_data.items() if value is not None}
        if len(data_without_none) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Specify the fields with the values to update"
            )
        stmt = (
            update(cls.model)
            .values(**dict(data_without_none))
            .filter_by(**filter_parameters)
            .returning(*cls.model.__table__.columns)
        )
        temp = await session.execute(stmt)
        await session.commit()
        return temp.fetchall()

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
