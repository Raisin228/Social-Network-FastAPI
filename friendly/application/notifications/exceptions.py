from application.core.exceptions import BaseCustomException


class SuchDeviceTokenAlreadyExist(BaseCustomException):
    def __init__(
        self,
        msg: str = "The token is already stored in the database for this device. "
        "No need to save it again.",
    ):
        super().__init__(msg)
