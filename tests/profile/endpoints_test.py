import datetime

from application.auth.dao import UserDao
from application.auth.schemas import GetUser
from application.core.responses import SUCCESS
from application.profile.schemas import AccountDeleted
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from utils import get_acs_token


async def test_get_existent_user_profile(_create_standard_user, ac: AsyncClient):
    """Пользователь создал аккаунт и хочет получить информацию из своего профиля"""
    user_id = _create_standard_user.id
    response = await ac.get("/profile/get_information", headers={"Authorization": f"Bearer {get_acs_token(user_id)}"})

    assert response.status_code == list(SUCCESS.keys())[0]
    assert GetUser.model_validate(response.json())


async def test_change_profile_with_correct_data(
    _create_standard_user, get_access_token, ac: AsyncClient, session: AsyncSession
):
    """Пользователь вносит корректные данные в свой профиль"""
    new_data = {
        "first_name": "Jason",
        "last_name": "Jr. Borne",
        "birthday": "2004-10-29",
        "sex": "Man",
        "nickname": "bog_at_04",
    }
    result = await ac.patch(
        "/profile/update_information", headers={"Authorization": f"Bearer {get_access_token}"}, json=new_data
    )
    user_id = result.json()["id"]

    assert result.status_code == list(SUCCESS.keys())[0]
    assert GetUser.model_validate(result.json())
    data_in_db = await UserDao.find_by_filter(session, {"id": user_id})
    assert data_in_db["first_name"] == new_data["first_name"]
    assert data_in_db["last_name"] == new_data["last_name"]
    assert data_in_db["birthday"] == datetime.date(2004, 10, 29)
    assert data_in_db["sex"] == new_data["sex"]
    assert data_in_db["nickname"] == new_data["nickname"]


# на завтра дописать тесты на обновление и начать делать forgot_password + change_password
# async def test_change_profile_nickname_already_busy(_create_standard_user, get_access_token, ac: AsyncClient,
#                                                     session: AsyncSession):
#     UserDao.add_one(session, {
#         "id": UNIQ_ID,
#         "nickname": f"id_{UNIQ_ID}",
#         "email": USER_DATA["email"],
#         "password": hash_password(USER_DATA["password"]),
#     })
#     UserDao.update_row(session, {"nickname": "bog_at_04"}, )
#
#     result = await ac.patch('/profile/update_information', headers={"Authorization": f"Bearer {get_access_token}"},
#                             json={"nickname": "bog_at_04"})


async def test_delete_user_profile(_create_standard_user, ac: AsyncClient, session: AsyncSession):
    """Пользователь удаляет аккаунт из системы"""
    user_id = _create_standard_user.id
    response = await ac.delete("/profile/delete_account", headers={"Authorization": f"Bearer {get_acs_token(user_id)}"})

    assert response.status_code == list(SUCCESS.keys())[0]
    assert AccountDeleted.model_validate(response.json())
    assert await UserDao.find_by_filter(session, {"id": user_id}) is None
