"""
Enumerations for the rules package.
"""

from enum import StrEnum


class CriterionType(StrEnum):
    """Criterion type enumeration."""

    CONTAINS = "contains"
    REGEX = "regex"
    ALL = "all"
    ANY = "any"


class ActionType(StrEnum):
    """Action type enumeration."""

    SET = "set"
    REGEX_EXTRACT = "regex_extract"
    DERIVE = "derive"
    EXTRACT = "extract"
