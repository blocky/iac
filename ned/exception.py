from enum import Enum, unique, auto


@unique
class NEDErrorCode(Enum):
    KEY_DELETE_FAIL = auto()
    KEY_DUPLICATE = auto()
    KEY_FILE_EXISTS = auto()
    KEY_MISSING = auto()
    INSTANCE_DUPLICATE = auto()
    INSTANCE_NAME_COLLISION = auto()
    INSTANCE_NOT_READY = auto()
    INSTANCE_MISSING = auto()
    INSTANCE_TERMINATION_FAIL = auto()
    INSTANCE_UNKNOWN_KIND = auto()
    DOMAIN_NAME_INVALID = auto()
    DOMAIN_NAME_NOT_FOUND = auto()
    DNS_INVALID_RECORD_OPERATION = auto()
    DNS_RECORD_NOT_FOUND = auto()
    DNS_UNEXPECTED_NUMBER_OF_RECORDS = auto()


class NEDException(Exception):
    def __init__(self, error_code: NEDErrorCode, message: str):
        super().__init__(message)
        self.error_code = error_code


class NEDWarning(NEDException):
    pass


class NEDError(NEDException):
    pass
