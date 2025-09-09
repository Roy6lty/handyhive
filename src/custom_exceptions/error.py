from fastapi import HTTPException, status


class NotFoundError(Exception):
    pass


class TokenExpirationError(Exception):
    """Raised when a token has expired."""

    def __init__(self, token_type: str = "Token has expired"):
        super().__init__(f"{token_type} has expired")


class InvalidTokenError(Exception):
    """Raised when a token is invalid."""

    def __init__(self, message: str = "Invalid token"):
        super().__init__(message)


class IncorrectPasswordOrUsernameException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="incorrect username or password",
        )


class IncorrectPassword(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="incorrect old password",
        )


class UserDoesNotExistException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="user Does Not exist",
        )


class UserAlreadyExistsException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="user with email already exists",
        )


class InvalidVerificationCodeException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="invalid or expired verification code ",
        )
