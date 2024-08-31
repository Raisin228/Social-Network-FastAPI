import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from application.auth.dao import UserDao
from application.auth.schemas import TokensInfo
from application.core.responses import SUCCESS, UNAUTHORIZED
from auth.conftest import user_data


@pytest.mark.asyncio(loop_scope='session')
async def test_login_exist_user_with_correct_email_and_pass(_create_standard_user, ac: AsyncClient,
                                                            session: AsyncSession):
    """Пользователь существует в системе и пытается сделать вход"""
    response = await ac.post('/auth/login', json=user_data)

    assert response.status_code == list(SUCCESS.keys())[0]
    assert TokensInfo.model_validate(response.json())

    user = await UserDao.find_by_filter(session, {'email': user_data['email']})
    assert user['first_name'] is None
    assert user['last_name'] is None

    await UserDao.delete_by_filter(session, {'id': user['id']})


@pytest.mark.asyncio(loop_scope='session')
async def test_login_by_non_existent_account(ac: AsyncClient, session: AsyncSession):
    """Вход в несуществующий аккаунт"""
    # user_record = await UserDao.find_by_filter(session, {'email': user_data['email']})
    # print(user_record)
    incorrect_data = {
        'email': 'imagine_mail@yandex.ru',
        'password': 'strong_but_useless_pass'
    }
    response = await ac.post('/auth/login', json=incorrect_data)

    assert response.status_code == list(UNAUTHORIZED.keys())[0]
    assert response.json() == {'detail': 'Invalid email or password'}

    user_record = await UserDao.find_by_filter(session, {'email': incorrect_data['email']})
    assert user_record is None
