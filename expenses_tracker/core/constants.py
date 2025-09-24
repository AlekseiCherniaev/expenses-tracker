from enum import Enum


class BudgetPeriod(Enum):
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"
    YEARLY = "YEARLY"


class Environment(Enum):
    TEST = "TEST"
    DEV = "DEV"
    PROD = "PROD"


class TokenType(Enum):
    ACCESS = "access"
    REFRESH = "refresh"
    EMAIL_VERIFICATION = "email_verification"
    RESET_PASSWORD = "password_reset"
