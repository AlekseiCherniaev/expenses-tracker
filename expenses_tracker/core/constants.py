from enum import Enum


class BudgetPeriod(Enum):
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"
    YEARLY = "YEARLY"


class Environment(Enum):
    TEST = "TEST"
    DEV = "DEV"
    PROD = "PROD"
