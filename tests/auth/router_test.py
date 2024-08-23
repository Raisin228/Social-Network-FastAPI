import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from application.auth.dao import UserDao
from application.core.responses import CONFLICT, SUCCESS


@pytest.mark.asyncio(loop_scope='session')
async def test_register_uniq_user(ac: AsyncClient, session: AsyncSession):
    """Регистрация аккаунта на почту, которая ещё не использовалась в системе"""
    user_data = {
        'email': 'fake_email@gmail.com',
        'password': 'very_strong_user_password123'
    }
    response = await ac.post('/auth/registration', json=user_data)

    assert response.status_code == list(SUCCESS.keys())[0]
    assert response.json() == {
        'msg': 'Account successfully created',
        'detail': {
            'id': 1,
            'first_name': None,
            'last_name': None,
            'email': 'fake_email@gmail.com'
        }
    }

    user_record = await UserDao.find_by_filter(session, {'email': 'fake_email@gmail.com'})
    assert user_record['id'] == 1
    assert user_record['email'] == user_data['email']
    assert user_record['first_name'] is None
    assert user_record['last_name'] is None


@pytest.mark.asyncio(loop_scope='session')
async def test_register_user_occupied_email(ac: AsyncClient, session: AsyncSession):
    """Регистрация пользователя на уже занятую почту"""
    user_data = {
        'email': 'fake_email@gmail.com',
        'password': 'very_strong_user_password123'
    }
    response = await ac.post('/auth/registration', json=user_data)

    assert response.status_code == list(CONFLICT.keys())[0]
    assert response.json() == {"detail": "User with that email already exist"}

    user_record = await UserDao.find_by_filter(session, {'email': 'fake_email@gmail.com'})
    assert user_record['id'] == 1
    assert user_record['email'] == user_data['email']
    assert user_record['first_name'] is None
    assert user_record['last_name'] is None


