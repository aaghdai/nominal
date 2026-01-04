"""
Rule class for representing form identification rules.
"""

from dataclasses import dataclass
from typing import Any

from nominal.logging_config import setup_logger

from .action import Action
from .criterion import Criterion

logger = setup_logger("nominal.processor.rule")


@dataclass
class Rule:
    """Represents a complete rule for a form type."""

    rule_id: str  # Identifier for this rule (e.g., "W2", "1099-MISC")
    description: str
    global_variables: list[str]  # Batch-level variables (e.g., SSN, FIRST_NAME, LAST_NAME)
    local_variables: list[str]  # Document-level variables (e.g., FORM_NAME)
    derived_variables: list[
        str
    ]  # Variables that can be computed or extracted (e.g., SSN_LAST_FOUR)
    criteria: list[Criterion]
    actions: list[Action]

    @property
    def all_variables(self) -> list[str]:
        """Returns all variable names defined in this rule."""
        return self.global_variables + self.local_variables + self.derived_variables

    def apply(self, text: str) -> dict[str, Any] | None:
        """
        Apply the rule to the given text.
        Returns all extracted variables if all criteria match, None otherwise.
        Scope separation is handled by the processor.
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

        # Execute all actions
        all_variables = {}
        all_variables.update(all_captured_values)

        logger.debug(f"Executing {len(self.actions)} actions")
        for action in self.actions:
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
