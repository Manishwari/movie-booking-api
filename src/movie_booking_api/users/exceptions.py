class UserError(Exception):
    """Base exception for user-related errors."""


class UserAlreadyExistsError(UserError):
    """Raised when a user with the given email already exists."""


class UserNotFoundError(UserError):
    """Raised when a user cannot be found."""


class InvalidCredentialsError(UserError):
    """Raised when login credentials are invalid."""
