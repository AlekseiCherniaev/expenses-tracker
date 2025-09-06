class DomainException(Exception):
    """Base class for domain exceptions."""

    pass


class UserNotFound(DomainException):
    pass


class UserAlreadyExists(DomainException):
    pass
