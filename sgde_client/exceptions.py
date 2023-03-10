class ClientException(Exception):
    def __init__(self, message):
        self.message = message
        super(ClientException, self).__init__(self.message)


class ResponseException(ClientException):
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        super(ResponseException, self).__init__(f"[{status_code}] {message}")
