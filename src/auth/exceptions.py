from src.exceptions import BadRequest, NotFound, NotAuthenticated


class EmailTaken(BadRequest):
    DETAIL = "Email already exists"


class UsernameTaken(BadRequest):
    DETAIL = "Username already exists"


class UserNotFound(NotFound):
    DETAIL = "User not found"


class InvalidToken(NotAuthenticated):
    DETAIL = "Invalid token"


class LoginRequired(NotAuthenticated):
    DETAIL = "Login required"


class InvalidCredentials(NotAuthenticated):
    DETAIL = "Invalid credentials"
