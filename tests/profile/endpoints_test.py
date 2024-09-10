import datetime
import uuid

from application.auth.dao import UserDao
from application.auth.schemas import GetUser
from application.core.responses import SUCCESS, UNAUTHORIZED
from application.profile.schemas import AccountDeleted
from auth.hashing_password import hash_password
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from utils import USER_DATA, get_acs_token


class TestProfileAPI:
    async def test_get_existent_user_profile(self, _create_standard_user, ac: AsyncClient):
        """Пользователь создал аккаунт и хочет получить информацию из своего профиля"""
        user_id = _create_standard_user.id
        response = await ac.get(
            "/profile/get_information", headers={"Authorization": f"Bearer {get_acs_token(user_id)}"}
        )

        assert response.status_code == list(SUCCESS.keys())[0]
        assert GetUser.model_validate(response.json())

    async def test_change_profile_with_correct_data(
        self, _create_standard_user, get_access_token, ac: AsyncClient, session: AsyncSession
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

    async def test_change_nickname_which_occupied(
        self, _create_standard_user, get_access_token, ac: AsyncClient, session: AsyncSession
    ):
        """Пользователь меняет ник на уже существующий в системе"""
        id_fake_user = uuid.uuid4()
        await UserDao.add_one(
            session,
            {
                "id": str(id_fake_user),
                "nickname": "some_interest_nick",
                "email": f'other_{USER_DATA["email"]}',
                "password": hash_password(USER_DATA["password"]),
            },
        )
        response = await ac.patch(
            "/profile/update_information",
            headers={"Authorization": f"Bearer {get_access_token}"},
            json={"nickname": "some_interest_nick"},
        )

        assert response.status_code == list(UNAUTHORIZED.keys())[0]
        assert response.json() == {"detail": "user with this nickname already exists"}

        await UserDao.delete_by_filter(session, {"id": id_fake_user})

    async def test_delete_user_profile(self, _create_standard_user, ac: AsyncClient, session: AsyncSession):
        """Пользователь удаляет аккаунт из системы"""
        user_id = _create_standard_user.id
        response = await ac.delete(
            "/profile/delete_account", headers={"Authorization": f"Bearer {get_acs_token(user_id)}"}
        )

        assert response.status_code == list(SUCCESS.keys())[0]
        assert AccountDeleted.model_validate(response.json())
        assert await UserDao.find_by_filter(session, {"id": user_id}) is None
