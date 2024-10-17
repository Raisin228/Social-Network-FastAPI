from typing import List
from uuid import UUID

from application.auth.dependensies import get_current_user_access_token
from application.auth.models import User
from application.core.exceptions import DataDoesNotExist, SuchDeviceTokenAlreadyExist
from application.core.responses import BAD_REQUEST, FORBIDDEN, NOT_FOUND, UNAUTHORIZED
from application.notifications.dao import FirebaseDeviceTokenDao, NotificationDao
from application.notifications.request_body import DeviceTokenFCM
from application.notifications.schemas import (
    FCMTokenSavedSuccess,
    Notification,
    QuantityRemovedNotify,
)
from database import get_async_session
from fastapi import APIRouter, Depends, HTTPException, Query, status
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


@router.get("/notifications", responses=NOT_FOUND | FORBIDDEN | UNAUTHORIZED, response_model=List[Notification])
async def all_notifications(
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=10, le=50),
    user: User = Depends(get_current_user_access_token),
    session: AsyncSession = Depends(get_async_session),
):
    """Список входящих уведомлений"""
    excite = await NotificationDao.get_notifications(offset, limit, user.id, session)
    if not excite:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No incoming notifications.")
    return [Notification(**event.__dict__) for event in excite]


@router.patch("/mark-notify-read/{n_id}", response_model=Notification, responses=NOT_FOUND | UNAUTHORIZED | FORBIDDEN)
async def mark_as_read(
    n_id: UUID, _user: User = Depends(get_current_user_access_token), session: AsyncSession = Depends(get_async_session)
):
    """Пометить сообщение как прочитанное

    **Note:**
    * При повторной отправке уведомление помечается **НЕ**прочитанным
    """
    try:
        r = await NotificationDao.change_notify_status(n_id, session)
    except DataDoesNotExist as ex:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{ex.msg} Notifications with this ID don't exist in the system.",
        )
    return Notification(
        **{"title": r[3], "message": r[4], "created_at": r[5], "status": r[6], "sender": r[1], "id": r[0]}
    )


@router.delete("/clear-notifications", response_model=QuantityRemovedNotify)
async def delete_notifications(
    user: User = Depends(get_current_user_access_token), session: AsyncSession = Depends(get_async_session)
):
    """Удалить все уведомления"""

    removed_notifications = await NotificationDao.delete_by_filter(session, {"recipient": user.id})
    if not removed_notifications:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No incoming notifications.")
    return QuantityRemovedNotify(**{"notify_removed": len(removed_notifications)})
