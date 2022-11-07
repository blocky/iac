from enum import Enum, unique, auto


@unique
class IACErrorCode(Enum):
    NO_SUCH_KEY = auto()
    DUPLICATE_KEY = auto()
    KEY_FILE_EXISTS = auto()
    NO_SUCH_KEY_FILE = auto()
    KEY_DELETE_FAIL = auto()
    DUPLICATE_INSTANCE = auto()
    INSTANCE_NAME_COLLISION = auto()
    INSTANCE_NOT_RUNNING = auto()
    INSTANCE_TERMINATION_FAIL = auto()
    NO_SUCH_INSTANCE = auto()
    NO_SUCH_INSTANCE_KIND = auto()
    INVALID_HOST = auto()
    INVALID_DNS_A_RECORD_OPERAION = auto()
    UNEXPECTED_NUMBER_OF_RECORDS = auto()
    DNS_RECORD_NOT_FOUND = auto()


class IACException(Exception):
    def __init__(self, error_code: IACErrorCode, message: str):
        super().__init__(message)
        self.error_code = error_code


class IACWarning(IACException):
    pass


class IACError(IACException):
    pass
