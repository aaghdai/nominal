"""
Nominal Processor: Rule-based document processing engine.

This module provides backward compatibility imports from the processor package.
All functionality has been moved to the processor package for better organization.
"""

# Import everything from the processor package for backward compatibility
from .processor import (
    # Actions
    Action,
    ActionType,
    AllCriterion,
    AnyCriterion,
    ContainsCriterion,
    # Criteria
    Criterion,
    CriterionType,
    DeriveAction,
    ExtractAction,
    GlobalVariable,
    LocalVariable,
    # Main processor
    NominalProcessor,
    RegexCriterion,
    RegexExtractAction,
    # Rule
    Rule,
    # Parser
    RuleParser,
    SetAction,
    # Variables
    Variable,
    # Enums
    VariableScope,
)

__all__ = [
    # Enums
    "VariableScope",
    "CriterionType",
    "ActionType",
    # Variables
    "Variable",
    "GlobalVariable",
    "LocalVariable",
    # Criteria
    "Criterion",
    "ContainsCriterion",
    "RegexCriterion",
    "AllCriterion",
    "AnyCriterion",
    # Actions
    "Action",
    "SetAction",
    "RegexExtractAction",
    "DeriveAction",
    "ExtractAction",
    # Rule
    "Rule",
    # Parser
    "RuleParser",
    # Main processor
    "NominalProcessor",
]
