from enum import Enum


class ErrorClass(str, Enum):
    HARD_FAIL = "HARD_FAIL"
    SOFT_FAIL = "SOFT_FAIL"
    ANOMALY = "ANOMALY"


_HARD = {"FROZEN_UNRECOVERABLE", "DB_WRITE_FAILURE"}
_SOFT = {"STUCK", "OVERDRAINED"}
_ANOMALY = {"NEGATIVE_BALANCE", "REPEATED_RECOVERY", "EARNINGS_SPIKE"}


def classify_error(error_type: str) -> ErrorClass:
    if error_type in _HARD:
        return ErrorClass.HARD_FAIL
    if error_type in _SOFT:
        return ErrorClass.SOFT_FAIL
    return ErrorClass.ANOMALY
