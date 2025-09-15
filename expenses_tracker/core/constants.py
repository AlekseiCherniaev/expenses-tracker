from enum import Enum


class BudgetPeriod(Enum):
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"


class Environment(Enum):
    TEST = "TEST"
    DEV = "DEV"
    PROD = "PROD"
