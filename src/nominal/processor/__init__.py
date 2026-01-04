"""
Nominal Processor: Rule-based document processing engine.

This package implements a DSL-based processor for extracting information
from tax documents based on configurable rules.
"""

# Enums
from .enums import VariableScope, CriterionType, ActionType

# Variables
from .variable import Variable, GlobalVariable, LocalVariable

# Criteria
from .criterion import (
    Criterion,
    ContainsCriterion,
    RegexCriterion,
    AllCriterion,
    AnyCriterion
)

# Actions
from .action import (
    Action,
    SetAction,
    RegexExtractAction,
    DeriveAction,
    ExtractAction
)

# Rule
from .rule import Rule

# Parser
from .parser import RuleParser

# Main processor
from .processor import NominalProcessor

__all__ = [
    # Enums
    'VariableScope',
    'CriterionType',
    'ActionType',
    # Variables
    'Variable',
    'GlobalVariable',
    'LocalVariable',
    # Criteria
    'Criterion',
    'ContainsCriterion',
    'RegexCriterion',
    'AllCriterion',
    'AnyCriterion',
    # Actions
    'Action',
    'SetAction',
    'RegexExtractAction',
    'DeriveAction',
    'ExtractAction',
    # Rule
    'Rule',
    # Parser
    'RuleParser',
    # Main processor
    'NominalProcessor',
]

