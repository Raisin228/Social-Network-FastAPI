class BaseCustomException(Exception):
    def __init__(self, msg: str):
        self.msg = msg
        super().__init__(msg)


class DataDoesNotExist(BaseCustomException):
    def __init__(self, msg: str = "The requested data is not in the system."):
        super().__init__(msg)
