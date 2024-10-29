import uuid

import pytest
from application.auth.models import User
from data_access_object.base import BaseDAO
from sqlalchemy import text
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
        value = await BaseDAO.add_one(session, rows[0])
        assert value.to_dict() == User(**rows[0]).to_dict()

    async def test_duplicate_values(self, _create_standard_user, session: AsyncSession):
        """Тест. Добавление повторяющихся данных в уникальное поле"""
        with pytest.raises((IntegrityError, DBAPIError)):
            try:
                await BaseDAO.add_one(session, rows[0])
            except Exception as e:
                await session.rollback()
                raise e


class TestUpdateRow:
    async def test_upd_without_data(self, _create_standard_user, session: AsyncSession):
        await BaseDAO.update_row(session, {}, {"id": rows[0].get("id")})

    # дописать интеграционные тесты для basedao
    # async def test_upd_single_row(self, _create_standard_user, session: AsyncSession):
    #     await BaseDAO.update_row(session, {'first_name': 'James', 'last_name': 'Bourne'}, {'id': rows[0].get('id')})
