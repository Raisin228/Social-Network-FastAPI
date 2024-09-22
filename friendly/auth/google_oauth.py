from authlib.integrations.base_client import OAuthError
from authlib.integrations.starlette_client import OAuth
from authlib.oidc.core import UserInfo
from config import settings
from fastapi import Request
from starlette.config import Config

GOOGLE_CLIENT_ID = settings.GOOGLE_CLIENT_ID
GOOGLE_CLIENT_SECRET = settings.GOOGLE_CLIENT_SECRET

config_data = {"GOOGLE_CLIENT_ID": GOOGLE_CLIENT_ID, "GOOGLE_CLIENT_SECRET": GOOGLE_CLIENT_SECRET}
starlette_config = Config(environ=config_data)
oauth = OAuth(starlette_config)
oauth.register(
    name="google",
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)


async def get_data_from_authorize_token(request: Request) -> None | UserInfo:
    """Получить данные пользователя из token выданного Google Auth Server"""
    try:
        access_token = await oauth.google.authorize_access_token(request)
    except OAuthError:
        return None

    nonce = request.session.get("nonce")
    user_data = await oauth.google.parse_id_token(nonce=nonce, token=access_token)
    del request.session["nonce"]
    return user_data
