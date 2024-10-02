class DataDoesNotExist(Exception):
    def __init__(self, msg: str = "The requested data is not in the system"):
        super().__init__(msg)
