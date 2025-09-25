from fastapi import Request, FastAPI
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from starlette import status

from expenses_tracker.domain.exceptions.auth import (
    InvalidCredentials,
    TokenExpired,
    InvalidToken,
    Unauthorized,
    EmailAlreadyVerified,
    EmailSendingError,
)
from expenses_tracker.domain.exceptions.budget import BudgetNotFound
from expenses_tracker.domain.exceptions.category import CategoryNotFound
from expenses_tracker.domain.exceptions.expense import ExpenseNotFound
from expenses_tracker.domain.exceptions.user import (
    UserAlreadyExists,
    UserNotFound,
)

EXCEPTION_STATUS_MAP: dict[type[Exception], int] = {
    UserAlreadyExists: status.HTTP_400_BAD_REQUEST,
    UserNotFound: status.HTTP_404_NOT_FOUND,
    CategoryNotFound: status.HTTP_404_NOT_FOUND,
    ExpenseNotFound: status.HTTP_404_NOT_FOUND,
    BudgetNotFound: status.HTTP_404_NOT_FOUND,
    EmailAlreadyVerified: status.HTTP_400_BAD_REQUEST,
    EmailSendingError: status.HTTP_500_INTERNAL_SERVER_ERROR,
    InvalidCredentials: status.HTTP_401_UNAUTHORIZED,
    Unauthorized: status.HTTP_401_UNAUTHORIZED,
    TokenExpired: status.HTTP_401_UNAUTHORIZED,
    InvalidToken: status.HTTP_401_UNAUTHORIZED,
    RateLimitExceeded: status.HTTP_429_TOO_MANY_REQUESTS,
}


def register_exception_handlers(app: FastAPI) -> None:
    for exc_class, exc_status in EXCEPTION_STATUS_MAP.items():

        @app.exception_handler(exc_class)
        async def handler(_: Request, exc: exc_class, http_status=exc_status):  # type: ignore
            return JSONResponse(
                status_code=http_status,
                content={"detail": str(exc)},
            )
