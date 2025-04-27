from typing import Dict, List, Tuple, Union

from application.core.exceptions import DataDoesNotExist
from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession


class BaseDAO:
    model = None

    @classmethod
    async def find_by_filter(
        cls, session: AsyncSession, find_by: Dict, *, return_models: bool = False
    ) -> None | Dict | model | List[Dict] | List[model]:
        """
        Search for records in the database by filters.

        Args:
            session (AsyncSession): The SQLAlchemy async session.
            find_by (Union[Dict, None]): Filters for record search.
            return_models (bool): If True, return ORM models instead of dicts.

        Returns:
            Union[None, Dict, List]:
                - Method returns None, if nothing was found.
                - Only one dict, if one record was found.
                - List of dict / model, if more than one record was found.

            Item type depends on `return_models` flag: dicts or model instances.

        Raises:
            SQLAlchemyError: If the database operation fails.
            TypeError: If `find_by` is not a dictionary or has invalid keys.
        """
        query = select(cls.model).filter_by(**find_by)
        data = await session.execute(query)
        result = data.scalars().all()

        if not return_models:
            result = [obj.to_dict() for obj in result]

        if len(result) == 0:
            return None
        if len(result) == 1:
            return result[0]
        return result

    @classmethod
    async def add(
        cls, session: AsyncSession, values: Union[Dict, List[Dict]]
    ) -> Union[model, List[model]]:
        """
        Adds one or multiple objects to the database.

        If a single dictionary is provided, inserts one record.
        If a list of dictionaries is provided, performs a bulk insert.

        Args:
            session (AsyncSession): The SQLAlchemy async session.
            values (Union[Dict, List[Dict]]):
                - A dictionary with field values for inserting a single object.
                - A list of dictionaries for bulk insertion.

        Returns:
            Union[model, List[model]]:
                - A single model instance if one object is inserted.
                - A list of model instances if multiple objects are inserted.

        Raises:
            SQLAlchemyError: If the database operation fails.
        """
        # если пришли пустые данные на вставку - возвращаем []
        if not values or all(not d for d in values):
            return []

        if isinstance(values, dict):
            values = [values]

        stmt = insert(cls.model).values(values).returning(cls.model.id)
        result = await session.execute(stmt)

        inserted_ids = result.scalars().all()
        query = select(cls.model).where(cls.model.id.in_(inserted_ids))
        result = await session.execute(query)

        models = result.scalars().all()
        return models if len(models) > 1 else models[0]

    @classmethod
    async def update_row(
        cls, session: AsyncSession, new_data: Dict, filter_parameters: Dict
    ) -> List[Tuple]:
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
    async def delete_by_filter(cls, session: AsyncSession, find_by: Dict) -> List[Dict]:
        """
        Delete all entries that meet the filtering conditions.

        Args:
            session (AsyncSession): The SQLAlchemy async session.
            find_by (Dict): Filters for selecting entries for deletion.

        Returns:
            List[Dict]:
                - List of deleted rows.

        Raises:
            SQLAlchemyError: If the database operation fails.
            TypeError: If `find_by` is not a dictionary or has invalid keys.
        """
        stmt = delete(cls.model).filter_by(**find_by).returning(*cls.model.__table__.columns)
        result = await session.execute(stmt)
        await session.commit()

        # для простоты используем protected method
        return [dict(row._mapping) for row in result.fetchall()]  # noqa
