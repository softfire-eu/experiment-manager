class BaseException(Exception):
    def __init__(self, message=None):
        self.message = message


class ManagerNotFound(BaseException):
    pass


class RpcFailedCall(BaseException):
    pass


class ExperimentValidationError(BaseException):
    pass


class ResourceNotFound(BaseException):
    pass


class ResourceAlreadyBooked(BaseException):
    pass


class ExperimentNotFound(BaseException):
    pass
