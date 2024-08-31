# import pytest
# from httpx import AsyncClient
#
# from application.auth.schemas import AccessTokenInfo
# from application.core.responses import SUCCESS
#
#
# @pytest.mark.asyncio(loop_scope='session')
# async def test_refresh_access_token(get_refresh_token, ac: AsyncClient):
#     """Получить обновлённый access token по заданному refresh token"""
#     response = await ac.post('/auth/refresh_access_token', headers={'Authorization': f'Bearer {get_refresh_token}'})
#     assert response.status_code == list(SUCCESS.keys())[0]
#     assert len(list(response.json().keys())) == 2
#     assert AccessTokenInfo(**response.json())
