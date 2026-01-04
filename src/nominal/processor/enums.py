"""
Enumerations for the processor package.
"""

from enum import StrEnum


class VariableScope(StrEnum):
    """Variable scope enumeration."""
    GLOBAL = "global"
    LOCAL = "local"


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

