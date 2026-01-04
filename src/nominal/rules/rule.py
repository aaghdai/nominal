"""
Rule class for representing form identification rules.
"""

from dataclasses import dataclass
from typing import Any

from nominal.logging import setup_logger

from .action import Action
from .criterion import Criterion
from .enums import ActionType

logger = setup_logger()


@dataclass
class Rule:
    """Represents a complete rule for a form type."""

    rule_id: str  # Identifier for this rule (e.g., "W2", "1099-MISC")
    description: str
    global_variables: list[str]  # Batch-level variables (e.g., SSN, FIRST_NAME, LAST_NAME)
    local_variables: list[str]  # Document-level variables (e.g., FORM_NAME)
    criteria: list[Criterion]
    actions: list[Action]

    @property
    def all_variables(self) -> list[str]:
        """Returns all variable names defined in this rule."""
        return self.global_variables + self.local_variables

    def apply(self, text: str) -> dict[str, Any] | None:
        """
        Apply the rule to the given text.
        Returns all extracted variables if all criteria match, None otherwise.
        Scope separation is handled by the processor.

        Action execution order:
        1. First phase: Execute all non-derive actions (set, regex_extract, extract)
           to extract global and local variables from the document text.
        2. Second phase: Execute all derive actions to compute derived variables
           from the previously extracted variables.

        This ensures derived variables are computed AFTER all source variables are available.
        """
        logger.info(f"Evaluating rule: {self.rule_id}")
        logger.debug(f"Rule description: {self.description}")

        # Check if all criteria match and collect captured variables
        all_captured_values = {}
        logger.debug(f"Checking {len(self.criteria)} criteria")
        for i, criterion in enumerate(self.criteria, 1):
            matches, captured = criterion.match(text)
            if not matches:
                logger.info(
                    f"✗ Rule {self.rule_id} rejected: criterion {i}/{len(self.criteria)} failed"
                )
                return None
            all_captured_values.update(captured)

        logger.info(f"✓ All criteria passed for rule {self.rule_id}")

        # Initialize variables with captured values from criteria
        all_variables = {}
        all_variables.update(all_captured_values)

        # Separate actions into two phases:
        # Phase 1: Non-derive actions (set, regex_extract, extract) - extract global/local vars
        # Phase 2: Derive actions - compute derived vars from extracted vars
        non_derive_actions = [
            action for action in self.actions if action.get_type() != ActionType.DERIVE
        ]
        derive_actions = [
            action for action in self.actions if action.get_type() == ActionType.DERIVE
        ]

        # Phase 1: Execute non-derive actions to extract global and local variables
        logger.debug(
            f"Phase 1: Executing {len(non_derive_actions)} extraction actions "
            f"(set, regex_extract, extract)"
        )
        for action in non_derive_actions:
            result = action.act(text, all_variables)
            if result is not None:
                all_variables[action.variable] = result

        # Phase 2: Execute derive actions to compute derived variables
        # Derived variables are computed AFTER all source variables are extracted
        logger.debug(
            f"Phase 2: Executing {len(derive_actions)} derivation actions "
            f"(derive - computed from extracted variables)"
        )
        for action in derive_actions:
            result = action.act(text, all_variables)
            if result is not None:
                all_variables[action.variable] = result

        var_count = len(all_variables)
        logger.info(
            f"✓ Rule {self.rule_id} matched successfully with {var_count} variable(s) extracted"
        )

        # Return all extracted variables without scope separation
        # Processor will handle scope separation based on variable lists
        return {
            "rule_id": self.rule_id,
            "variables": all_variables,
            "rule_description": self.description,
        }
