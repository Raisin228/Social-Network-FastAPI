class BaseCustomException(Exception):
    def __init__(self, msg: str):
        self.msg = msg
        super().__init__(msg)


class DataDoesNotExist(BaseCustomException):
    def __init__(self, msg: str = "The requested data is not in the system."):
        super().__init__(msg)


class RequestToYourself(BaseCustomException):
    def __init__(self, msg: str = "You can't make request to yourself."):
        super().__init__(msg)


class YouNotFriends(BaseCustomException):
    def __init__(self, msg: str = "You are not currently friends with this user."):
        super().__init__(msg)


class BlockByUser(BaseCustomException):
    def __init__(self, msg: str = "This user blocked you."):
        super().__init__(msg)


class NotApproveAppeal(BaseCustomException):
    def __init__(self, msg: str = "The application status is different from NOT_APPEAL."):
        super().__init__(msg)


class UserUnblocked(BaseCustomException):
    def __init__(self, msg: str = "The user has been removed from the blacklist."):
        super().__init__(msg)


class SuchDeviceTokenAlreadyExist(BaseCustomException):
    def __init__(
        self, msg: str = "The token is already stored in the database for this device. No need to save it again."
    ):
        super().__init__(msg)
