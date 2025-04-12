import uuid

import pytest
from application.auth.models import User
from application.core.exceptions import DataDoesNotExist
from data_access_object.base import BaseDAO
from sqlalchemy import select, text
from sqlalchemy.exc import DBAPIError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from utils import UNIQ_ID, rows


@pytest.fixture(autouse=True)
async def setup_and_teardown(session: AsyncSession):
    """Перед каждым тестом инициализируем работу с User. В конце чистим таблицу"""
    BaseDAO.model = User
    yield
    await session.execute(text('TRUNCATE TABLE "user" RESTART IDENTITY CASCADE;'))
    await session.commit()


class TestFindByFilter:
    async def test_data_does_not_exist(self, session: AsyncSession):
        """Тест. Получить несуществующие данные из бд"""
        result = await BaseDAO.find_by_filter(session, find_by={"id": uuid.uuid4()})
        assert result is None

    async def test_single_data_found(self, _create_standard_user, session: AsyncSession):
        """Тест. Уникальные данные найдены в бд"""
        result = await BaseDAO.find_by_filter(session, find_by={"id": UNIQ_ID})
        assert rows[0] == result

    async def test_multiple_data_found_by_filter(self, session: AsyncSession):
        """Тест. Несколько строк удовлетворяют условиям фильтрации"""
        inform = [User(**us) for us in rows]
        session.add_all(inform)
        await session.commit()
        result = await BaseDAO.find_by_filter(session, find_by={"first_name": "Bog"})
        assert rows == result


class TestAddOne:
    async def test_row(self, session: AsyncSession):
        """Тест. Вставка строки в бд"""
        value = await BaseDAO.add(session, rows[0])
        assert value.to_dict() == User(**rows[0]).to_dict()

    async def test_duplicate_values(self, _create_standard_user, session: AsyncSession):
        """Тест. Добавление повторяющихся данных в уникальное поле"""
        with pytest.raises((IntegrityError, DBAPIError)):
            try:
                await BaseDAO.add(session, rows[0])
            except Exception as e:
                await session.rollback()
                raise e


class TestUpdateRow:
    async def test_upd_without_data(self, _create_standard_user, session: AsyncSession):
        """Тест. Новые данные не указаны"""
        with pytest.raises(DataDoesNotExist, match="Specify the fields with the values to update"):
            await BaseDAO.update_row(session, {}, {"id": rows[0].get("id")})

    async def test_upd_single_row(self, _create_standard_user, session: AsyncSession):
        """Тест. Данные действительно обновляются"""
        upd_data = await BaseDAO.update_row(
            session, {"first_name": "James", "last_name": "Bourne"}, {"id": rows[0].get("id")}
        )
        query = select(User).where(User.id == rows[0].get("id"))
        res = await session.execute(query)
        data_from_rows_with_upd_fields = rows[0]
        data_from_rows_with_upd_fields["first_name"] = "James"
        data_from_rows_with_upd_fields["last_name"] = "Bourne"
        assert res.scalar_one_or_none().to_dict() == data_from_rows_with_upd_fields
        assert upd_data == [tuple(data_from_rows_with_upd_fields.values())]


class TestDeleteByFilter:
    async def test_single_record_remove(self, session: AsyncSession):
        """Тест. Удаление одной записи по фильтру"""
        info = rows[0]
        data = User(**info)
        session.add(data)
        await session.commit()
        del_row = await BaseDAO.delete_by_filter(session, {"id": rows[0].get("id")})
        query = select(User).where(User.id == rows[0].get("id"))
        res = await session.execute(query)
        assert res.scalar_one_or_none() is None
        assert del_row == [info]

    async def test_no_data_on_such_filter(self, session: AsyncSession):
        """Тест. Указали фильтр, которому не соответствуют данные"""
        empty_res = await BaseDAO.delete_by_filter(session, {"first_name": "Alen"})
        assert empty_res == []
