import datetime
import uuid

from application.auth.dao import UserDao
from application.core.responses import BAD_REQUEST, SUCCESS
from auth.hashing_password import hash_password
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from utils import USER_DATA, get_token_need_type


class TestProfileAPI:
    async def test_get_existent_user_profile(self, _create_standard_user, ac: AsyncClient):
        """Пользователь создал аккаунт и хочет получить информацию из своего профиля"""
        response = await ac.get(
            "/profile/get_information",
            headers={"Authorization": f"Bearer {get_token_need_type(_create_standard_user.id)}"},
        )
        assert response.json() == {
            "id": str(_create_standard_user.id),
            "email": _create_standard_user.email,
            "birthday": None,
            "sex": None,
            "nickname": f"id_{_create_standard_user.id}",
            "first_name": _create_standard_user.first_name,
            "last_name": _create_standard_user.last_name,
            "is_admin": False,
        }

    async def test_change_profile_with_correct_data(self, _create_standard_user, get_access_token, ac: AsyncClient):
        """Пользователь вносит корректные данные в свой профиль"""
        new_data = {
            "first_name": "Jason",
            "last_name": "Jr. Borne",
            "birthday": "2004-10-29",
            "sex": "Male",
            "nickname": "bog_at_04",
        }
        result = await ac.patch(
            "/profile/update_information", headers={"Authorization": f"Bearer {get_access_token}"}, json=new_data
        )

        assert result.status_code == list(SUCCESS.keys())[0]
        assert result.json() == {
            "id": str(_create_standard_user.id),
            "email": _create_standard_user.email,
            "birthday": str(datetime.date(2004, 10, 29)),
            "sex": new_data["sex"],
            "nickname": new_data["nickname"],
            "first_name": new_data["first_name"],
            "last_name": new_data["last_name"],
            "is_admin": False,
        }

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

        assert response.status_code == list(BAD_REQUEST.keys())[0]
        assert response.json() == {"detail": "user with this nickname already exists"}
        await UserDao.delete_by_filter(session, {"id": id_fake_user})

    async def test_delete_user_profile(self, _create_standard_user, ac: AsyncClient):
        """Пользователь удаляет аккаунт из системы"""
        user_id = _create_standard_user.id
        response = await ac.delete(
            "/profile/delete_account", headers={"Authorization": f"Bearer {get_token_need_type(user_id)}"}
        )

        assert response.status_code == list(SUCCESS.keys())[0]
        assert response.json() == {
            "msg": "Account successfully deleted",
            "deleted_account_info": {
                "id": str(_create_standard_user.id),
                "email": _create_standard_user.email,
                "birthday": None,
                "sex": None,
                "first_name": _create_standard_user.first_name,
                "last_name": _create_standard_user.last_name,
                "nickname": f"id_{_create_standard_user.id}",
                "is_admin": False,
            },
        }
