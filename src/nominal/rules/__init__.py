"""
Nominal Rules: Rule definition, parsing, and validation.

This package contains all rule-related functionality including:
- Rule definitions and structure
- Rule parsing from YAML
- Rule validation
- Actions and criteria
- Variables
"""


from .action import (
    Action,
    DeriveAction,
    ExtractAction,
    RegexExtractAction,
    SetAction,
)
from .criterion import (
    AllCriterion,
    AnyCriterion,
    ContainsCriterion,
    Criterion,
    RegexCriterion,
)
from .enums import ActionType, CriterionType, VariableScope
from .manager import RulesManager
from .parser import RuleParser
from .rule import Rule
from .validator import RuleValidator
from .variable import (
    DerivedVariable,
    GlobalVariable,
    LocalVariable,
    Variable,
)

__all__ = [
    # Manager
    "RulesManager",
    # Rule and parser
    "Rule",
    "RuleParser",
    # Validator
    "RuleValidator",
    # Variables
    "Variable",
    "GlobalVariable",
    "LocalVariable",
    "DerivedVariable",
    "VariableScope",
    # Criteria
    "Criterion",
    "ContainsCriterion",
    "RegexCriterion",
    "AllCriterion",
    "AnyCriterion",
    "CriterionType",
    # Actions
    "Action",
    "SetAction",
    "RegexExtractAction",
    "DeriveAction",
    "ExtractAction",
    "ActionType",
]
