from expenses_tracker.domain.exceptions.base import DomainException


class TokenExpired(DomainException):
    pass


class InvalidToken(DomainException):
    pass


class InvalidCredentials(DomainException):
    pass


class Unauthorized(DomainException):
    pass


class EmailAlreadyVerified(DomainException):
    pass


class EmailSendingError(DomainException):
    pass


class OAuthError(DomainException):
    pass
