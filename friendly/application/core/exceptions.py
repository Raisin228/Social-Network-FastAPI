class BaseCustomException(Exception):
    def __init__(self, msg: str):
        self.msg = msg
        super().__init__(msg)


class DataDoesNotExist(BaseCustomException):
    def __init__(self, msg: str = "The requested data is not in the system."):
        super().__init__(msg)


class InvalidAccessRights(BaseCustomException):
    def __init__(
        self,
        msg: str = "You cannot interact with the resource. Maybe if you ask the system administrator nicely, "
        "you’ll get permission.",
    ):
        super().__init__(msg)
