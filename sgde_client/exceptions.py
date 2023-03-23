from sgde_client.config import settings


class ClientException(Exception):
    def __init__(self, message):
        self.message = message
        super(ClientException, self).__init__(self.message)


class ResponseException(ClientException):
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        super(ResponseException, self).__init__(f"[{status_code}] {message}")


class MissingAuthorization(ClientException):
    def __init__(self):
        super(MissingAuthorization, self).__init__("You must login first")


class ServerUnreachable(ClientException):
    def __init__(self):
        super(ServerUnreachable, self).__init__(
            f"Server unreachable ({settings.API_IP}:{settings.API_PORT})"
        )
