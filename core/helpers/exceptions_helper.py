from fastapi import HTTPException


class ServiceException(Exception):
    """Base exception for application/service failures."""

    def __init__(self, message: str, status_code: int = 500, error_code: str = "service_error"):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        super().__init__(self.message)


class ValidationServiceException(ServiceException):
    def __init__(self, message: str = "Invalid request data"):
        super().__init__(message=message, status_code=400, error_code="validation_error")


class NotFoundServiceException(ServiceException):
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message=message, status_code=404, error_code="not_found")


class ConflictServiceException(ServiceException):
    def __init__(self, message: str = "Resource conflict"):
        super().__init__(message=message, status_code=409, error_code="conflict")


class InfrastructureServiceException(ServiceException):
    def __init__(self, message: str = "Internal server error"):
        super().__init__(message=message, status_code=500, error_code="infrastructure_error")


def to_http_exception(exc: ServiceException) -> HTTPException:
    return HTTPException(
        status_code=exc.status_code,
        detail={"message": exc.message, "code": exc.error_code},
    )


class AuthException(Exception):
    """Base exception for authentication errors"""

    def __init__(self, message: str, status_code: int = 401):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class SecurityBreachException(AuthException):
    """Exception raised when a potential security breach is detected (e.g., token reuse)"""

    def __init__(
        self,
        message: str = "Refresh token reuse detected. All tokens revoked for security.",
    ):
        super().__init__(message, status_code=403)


class InvalidCredentialsException(AuthException):
    """Exception raised when invalid credentials are provided"""

    def __init__(self, message: str = "Invalid username or password"):
        super().__init__(message, status_code=401)


class TokenRevokedException(AuthException):
    """Exception raised when a revoked token is used"""

    def __init__(self, message: str = "Token has been revoked"):
        super().__init__(message, status_code=401)


class UserNotFoundException(AuthException):
    """Exception raised when a user is not found"""

    def __init__(self, message: str = "User not found"):
        super().__init__(message, status_code=404)
