class ClientException(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class ResponseException(ClientException):
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        super().__init__(f"[{status_code}] {message}")
