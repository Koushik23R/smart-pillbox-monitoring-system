class AppException(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code


class AuthenticationError(AppException):
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, 401)


class AuthorizationError(AppException):
    def __init__(self, message: str = "Not authorized"):
        super().__init__(message, 403)


class UserAlreadyExistsError(AppException):
    def __init__(self, message: str = "User already exists"):
        super().__init__(message, 409)


class UserNotFoundError(AppException):
    def __init__(self, message: str = "User not found"):
        super().__init__(message, 404)


__all__ = [
    "AppException",
    "AuthenticationError",
    "AuthorizationError",
    "UserAlreadyExistsError",
    "UserNotFoundError",
]
