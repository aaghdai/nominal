"""
Nominal Processor: Rule-based document processing engine.

This package implements a DSL-based processor for extracting information
from tax documents based on configurable rules.
"""

# Enums
# Logging (imported from parent package)
from nominal.logging_config import configure_logging, get_logger, set_log_level, setup_logger

# Actions
from .action import Action, DeriveAction, ExtractAction, RegexExtractAction, SetAction

# Criteria
from .criterion import AllCriterion, AnyCriterion, ContainsCriterion, Criterion, RegexCriterion
from .enums import ActionType, CriterionType, VariableScope

# Parser
from .parser import RuleParser

# Main processor
from .processor import NominalProcessor

# Rule
from .rule import Rule

# Variables
from .variable import DerivedVariable, GlobalVariable, LocalVariable, Variable

__all__ = [
    # Enums
    "VariableScope",
    "CriterionType",
    "ActionType",
    # Variables
    "Variable",
    "GlobalVariable",
    "LocalVariable",
    "DerivedVariable",
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
    # Logging
    "setup_logger",
    "get_logger",
    "set_log_level",
    "configure_logging",
]
