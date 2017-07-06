class _BaseException(Exception):
    def __init__(self, message, *args) -> None:
        self.message = message
        super().__init__(*args)


class ManagerNotFound(_BaseException):
    pass


class RpcFailedCall(_BaseException):
    pass


class ExperimentValidationError(_BaseException):
    pass


class ResourceNotFound(_BaseException):
    pass


class ResourceAlreadyBooked(_BaseException):
    pass


class ExperimentNotFound(_BaseException):
    pass
