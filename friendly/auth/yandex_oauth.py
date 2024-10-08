import json
from typing import Dict

import httpx
from config import settings


async def change_code_to_access_token(code: str) -> str:
    """Обменять код подтверждения на OAuth-токен"""
    token_url = "https://oauth.yandex.ru/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "client_id": settings.YDEX_CLIENT_ID,
        "client_secret": settings.YDEX_CLIENT_SECRET,
    }
    async with httpx.AsyncClient() as client:
        token_response = await client.post(token_url, headers=headers, data=data)
        token_data = token_response.json()
    return token_data.get("access_token")


async def change_token_to_user_info(token: str) -> Dict | None:
    """Получить данные пользователя передав OAuth токен"""
    user_info_url = "https://login.yandex.ru/info"
    async with httpx.AsyncClient() as client:
        user_info_response = await client.get(
            user_info_url, params={"format": "json"}, headers={"Authorization": f"OAuth {token}"}
        )
        try:
            return user_info_response.json()
        except json.decoder.JSONDecodeError:
            return None
