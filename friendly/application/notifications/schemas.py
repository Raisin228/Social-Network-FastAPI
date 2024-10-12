from application.notifications.request_body import DeviceTokenFCM


class FCMTokenSavedSuccess(DeviceTokenFCM):
    """Токен устройства успешно добавлен в бд"""

    msg: str = "This device is saved. Notifications will also be sent to him now."
