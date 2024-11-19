from application.core.responses import BAD_REQUEST, SUCCESS
from application.notifications.exceptions import SuchDeviceTokenAlreadyExist
from httpx import AsyncClient
from utils import get_token_need_type

some_device = (
    "eI8V05b_ZX1eYfXdAs9EuE:APA91bHLObWjb_LNanOwB7D38_mbxudQCE6P27IFzNPYVZLqU_wzolRuOSMh6cRbgs6xZ4mSPTo1Jea"
    "DUyquFxX8ibqcwa-IylJt5_wFUhk7pYEzWTcsmVtLWZhDLa9Yh8VohDW2i3JA"
)


class TestConnectFCM:
    async def test_insert_new_device_token_from_fcm(self, _create_standard_user, ac: AsyncClient):
        """Тест. Отправить валидный токен устройства, которого ещё нет в бд"""
        res = await ac.post(
            "/notify/connect-to-firebase",
            json={"device_token": some_device},
            headers={"Authorization": f"Bearer {get_token_need_type(_create_standard_user.id)}"},
        )
        assert res.status_code == list(SUCCESS.keys())[0]
        assert res.json() == {
            "msg": "This device is saved. Notifications will also be sent to him now.",
            "device_token": some_device,
        }

    async def test_resending_existing_token(self, _create_standard_user, ac: AsyncClient):
        """Тест. Повторно пытаемся сохранить уже существующий токен"""
        await ac.post(
            "/notify/connect-to-firebase",
            json={"device_token": some_device},
            headers={"Authorization": f"Bearer {get_token_need_type(_create_standard_user.id)}"},
        )
        res = await ac.post(
            "/notify/connect-to-firebase",
            json={"device_token": some_device},
            headers={"Authorization": f"Bearer {get_token_need_type(_create_standard_user.id)}"},
        )
        assert res.status_code == list(BAD_REQUEST.keys())[0]
        assert res.json() == {"detail": SuchDeviceTokenAlreadyExist().msg}
