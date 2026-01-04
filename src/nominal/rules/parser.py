"""
Parser for YAML rule files.

Supports two types of rules:
- Global rules: Use 'rule_name' field, extract common variables
- Form rules: Use 'form_name' field, classify documents
"""

from pathlib import Path
from typing import Any

import yaml

from nominal.logging import setup_logger

from .action import Action, DeriveAction, ExtractAction, RegexExtractAction, SetAction
from .criterion import (
    AllCriterion,
    AnyCriterion,
    ContainsCriterion,
    Criterion,
    RegexCriterion,
)
from .enums import ActionType, CriterionType
from .rule import Rule

logger = setup_logger()


class RuleParser:
    """Parses YAML rule files into Rule objects."""

    def parse_file(self, rule_path: str) -> Rule:
        """Parse a YAML rule file."""
        logger.info(f"Parsing rule file: {rule_path}")

        path = Path(rule_path)
        if not path.exists():
            logger.error(f"Rule file not found: {rule_path}")
            raise FileNotFoundError(f"Rule file not found: {rule_path}")

        try:
            with open(path) as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            logger.error(f"Invalid YAML in rule file {rule_path}: {e}")
            raise ValueError(f"Invalid YAML in rule file {rule_path}: {e}")

        return self.parse_dict(data)

    def parse_dict(self, data: dict[str, Any]) -> Rule:
        """Parse a dictionary into a Rule object."""
        # Get rule identifier (form_name for forms, rule_name for global rules)
        rule_id = data.get("form_name") or data.get("rule_name")
        if not rule_id:
            logger.error("Rule must have either 'form_name' or 'rule_name' field")
            raise ValueError("Rule must have either 'form_name' or 'rule_name' field")

        # Validate required fields
        required_fields = ["criteria", "actions"]
        for field in required_fields:
            if field not in data:
                logger.error(f"Missing required field in rule {rule_id}: {field}")
                raise ValueError(f"Missing required field: {field}")

        logger.debug(f"Parsing rule: {rule_id}")

        # Parse variables (optional for global rules)
        variables = data.get("variables", {})
        global_vars = variables.get("global", [])
        local_vars = variables.get("local", [])
        derived_vars = variables.get("derived", [])

        logger.debug(
            f"Rule {rule_id} variables: global={len(global_vars)}, "
            f"local={len(local_vars)}, derived={len(derived_vars)}"
        )

        # Parse criteria
        try:
            criteria = [self._parse_criterion(c) for c in data["criteria"]]
            logger.debug(f"Parsed {len(criteria)} criteria for rule {rule_id}")
        except Exception as e:
            logger.error(f"Error parsing criteria for rule {rule_id}: {e}")
            raise

        # Parse actions
        try:
            actions = [self._parse_action(a) for a in data["actions"]]
            logger.debug(f"Parsed {len(actions)} actions for rule {rule_id}")
        except Exception as e:
            logger.error(f"Error parsing actions for rule {rule_id}: {e}")
            raise

        logger.info(f"✓ Successfully parsed rule: {rule_id}")

        return Rule(
            rule_id=rule_id,
            description=data.get("description", ""),
            global_variables=global_vars,
            local_variables=local_vars,
            derived_variables=derived_vars,
            criteria=criteria,
            actions=actions,
        )

    def _parse_criterion(self, data: dict[str, Any]) -> Criterion:
        """Parse a criterion dictionary."""
        criterion_type = data.get("type")
        if not criterion_type:
            raise ValueError("Criterion must have a 'type' field")

        description = data.get("description", "")

        if criterion_type == CriterionType.CONTAINS:
            return ContainsCriterion(
                value=data.get("value"),
                case_sensitive=data.get("case_sensitive", True),
                description=description,
            )

        elif criterion_type == CriterionType.REGEX:
            return RegexCriterion(
                pattern=data.get("pattern"),
                capture=data.get("capture", False),
                variable=data.get("variable"),
                description=description,
            )

        elif criterion_type == CriterionType.ALL:
            sub_criteria_data = data.get("criteria", [])
            sub_criteria = [self._parse_criterion(c) for c in sub_criteria_data]
            return AllCriterion(sub_criteria=sub_criteria, description=description)

        elif criterion_type == CriterionType.ANY:
            sub_criteria_data = data.get("criteria", [])
            sub_criteria = [self._parse_criterion(c) for c in sub_criteria_data]
            return AnyCriterion(sub_criteria=sub_criteria, description=description)

        else:
            raise ValueError(f"Unknown criterion type: {criterion_type}")

    def _parse_action(self, data: dict[str, Any]) -> Action:
        """Parse an action dictionary."""
        action_type = data.get("type")
        if not action_type:
            raise ValueError("Action must have a 'type' field")

        variable = data.get("variable", "")

        if action_type == ActionType.SET:
            return SetAction(variable=variable, value=data.get("value"))

        elif action_type == ActionType.REGEX_EXTRACT:
            return RegexExtractAction(
                variable=variable,
                pattern=data.get("pattern"),
                group=data.get("group", 0),
                from_text=data.get("from_text", False),
            )

        elif action_type == ActionType.DERIVE:
            return DeriveAction(
                variable=variable,
                from_var=data.get("from"),
                method=data.get("method"),
                args=data.get("args", {}),
            )

        elif action_type == ActionType.EXTRACT:
            return ExtractAction(
                variable=variable,
                from_var=data.get("from"),
                method=data.get("method"),
                args=data.get("args", {}),
            )

        else:
            raise ValueError(f"Unknown action type: {action_type}")
