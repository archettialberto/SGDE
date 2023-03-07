class APIException(Exception):
    def __init__(self, status_code: int, msg: str):
        self.msg = msg
        self.status_code = status_code
        super().__init__(self.msg)


class MissingFieldException(APIException):
    def __init__(self, field_name: str):
        super().__init__(400, f"'{field_name}' is required")


class InvalidFormatException(APIException):
    TOO_SHORT = "too short"
    TOO_LONG = "too long"
    MUST_START_WITH_CHAR = "must start with a letter"
    USR_CHARS = "must contain only letters, numbers, and underscores"
    PWD_CONTAIN_L_CHAR = "must contain at least one lowercase letter"
    PWD_CONTAIN_U_CHAR = "must contain at least one uppercase letter"
    PWD_CONTAIN_NUMBER = "must contain at least one number"
    PWD_CONTAIN_SYMBOL = "must contain at least one symbol"

    def __init__(self, field_name: str, comment: str):
        super().__init__(400, f"Invalid format for '{field_name}': {comment}")


class IncorrectPasswordException(APIException):
    def __init__(self):
        super().__init__(400, f"Incorrect password")


class AlreadyExistsException(APIException):
    def __init__(self, field_name: str):
        super().__init__(400, f"The provided '{field_name}' already exists")


class DoesNotExistException(APIException):
    def __init__(self, field_name: str):
        super().__init__(400, f"The provided '{field_name}' does not exist")
