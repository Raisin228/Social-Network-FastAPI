from typing import Dict, List, Tuple

from application.core.exceptions import DataDoesNotExist
from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession


class BaseDAO:
    model = None

    @classmethod
    async def find_by_filter(cls, session: AsyncSession, find_by: dict | None = None) -> None | Dict | List[Dict]:
        """Поиск по фильтрам или получить все записи"""
        query = select(cls.model).filter_by(**find_by)
        data = await session.execute(query)
        result = data.scalars().all()

        if len(result) == 0:
            return None
        result = [obj.to_dict() for obj in result]
        if len(result) == 1:
            return result[0]
        return result

    @classmethod
    async def add_one(cls, session: AsyncSession, values: dict) -> model:
        """Добавить один объект"""
        stmt = insert(cls.model).values(**values).returning(cls.model.id)
        col_id = await session.execute(stmt)
        await session.commit()

        query = select(cls.model).where(cls.model.id == col_id.scalar())
        result = await session.execute(query)
        return result.scalar_one_or_none()

    @classmethod
    async def update_row(cls, session: AsyncSession, new_data: dict, filter_parameters: dict) -> List[Tuple]:
        """Выбрать запис(ь|и) и обновить поля"""
        data_without_none = {key: value for key, value in new_data.items() if value is not None}
        if len(data_without_none) == 0:
            raise DataDoesNotExist("Specify the fields with the values to update")
        stmt = (
            update(cls.model)
            .values(**dict(data_without_none))
            .filter_by(**filter_parameters)
            .returning(*cls.model.__table__.columns)
        )
        temp = await session.execute(stmt)
        await session.commit()
        return [tuple(row) for row in temp.fetchall()]

    @classmethod
    async def delete_by_filter(cls, session: AsyncSession, find_by: dict):
        """Удалить все записи, удовлетворяющие условиям фильтрации"""
        stmt = delete(cls.model).filter_by(**find_by).returning(*cls.model.__table__.columns)
        result = await session.execute(stmt)
        await session.commit()
        return result.fetchall()
