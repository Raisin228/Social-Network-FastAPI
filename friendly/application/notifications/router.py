from application.auth.dependensies import get_current_user_access_token
from application.auth.models import User
from application.core.exceptions import SuchDeviceTokenAlreadyExist
from application.core.responses import BAD_REQUEST, FORBIDDEN, UNAUTHORIZED
from application.notifications.dao import FirebaseDeviceTokenDao
from application.notifications.request_body import DeviceTokenFCM
from application.notifications.schemas import FCMTokenSavedSuccess
from database import get_async_session
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/notify", tags=["Notification Server"])


@router.post(
    "/connect-to-firebase", response_model=FCMTokenSavedSuccess, responses=BAD_REQUEST | UNAUTHORIZED | FORBIDDEN
)
async def add_device_token_from_fcm(
    body: DeviceTokenFCM,
    user: User = Depends(get_current_user_access_token),
    session: AsyncSession = Depends(get_async_session),
):
    """Для получения уведомлений необходимо добавить устройство"""
    try:
        await FirebaseDeviceTokenDao.add_token(session, user.id, body.device_token)
        return FCMTokenSavedSuccess(**{"device_token": body.device_token})
    except SuchDeviceTokenAlreadyExist as ex:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ex.msg)
