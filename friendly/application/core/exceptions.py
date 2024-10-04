class DataDoesNotExist(Exception):
    def __init__(self, msg: str = "The requested data is not in the system"):
        self.msg = msg
        super().__init__(msg)


class RequestToYourself(Exception):
    def __init__(self, msg: str = "You can't make a friendship request to yourself"):
        self.msg = msg
        super().__init__(msg)
