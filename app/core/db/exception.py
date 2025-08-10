class ApiHTTPException(Exception):
    def __init__(self, code: int, error: str):
        self.code = code
        self.error = error     