from pydantic import BaseModel, Field


class DeviceTokenFCM(BaseModel):
    """Идентификатор устройства, полученный от FCM"""

    device_token: str = Field(
        examples=["eI8V05b_ZX1eYfXdAs9EuE:APA91bHLObWjb_LNanOwB7D38_mbxudQCE6P..."],
        description="The device ID that was received when accessing Firebase on the client side",
        min_length=100,
        max_length=256,
    )
