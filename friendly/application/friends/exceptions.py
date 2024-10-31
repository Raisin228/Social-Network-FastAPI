from application.core.exceptions import BaseCustomException


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
