from application.auth.constants import ACCESS_TOKEN_TYPE, REFRESH_TOKEN_TYPE
from application.auth.schemas import TokensInfo
from auth.auth import create_jwt_token


def generate_tokens_pair(data_for_payload: dict) -> TokensInfo:
    """Получить пару access | refresh token"""
    access_token = create_jwt_token(data_for_payload, ACCESS_TOKEN_TYPE)
    refresh_token = create_jwt_token(data_for_payload, REFRESH_TOKEN_TYPE)
    return TokensInfo(access_token=access_token, refresh_token=refresh_token, token_type="Bearer")
