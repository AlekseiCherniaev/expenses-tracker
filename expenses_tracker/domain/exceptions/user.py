from expenses_tracker.domain.exceptions.base import DomainException


class UserNotFound(DomainException):
    pass


class UserAlreadyExists(DomainException):
    pass
