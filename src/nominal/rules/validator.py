"""
Rule validation for Nominal processor.

Validates rule files to ensure they conform to the expected schema and structure.
Supports both global rules (rule_name) and form rules (form_name).
"""

from pathlib import Path
from typing import Any

import yaml

from nominal.logging import setup_logger

from .parser import RuleParser

logger = setup_logger()


class RuleValidator:
    """Validates rule files against schema and consistency requirements."""

    def __init__(self):
        """Initialize validator."""
        self.parser = RuleParser()
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def validate_rule_file(self, rule_path: str) -> bool:
        """Validate a single rule file."""
        path = Path(rule_path)
        if not path.exists():
            self.errors.append(f"Rule file not found: {rule_path}")
            return False

        print(f"\nValidating: {path.name}")

        # Validate YAML syntax
        try:
            with open(path) as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            self.errors.append(f"{path.name}: Invalid YAML syntax: {e}")
            return False

        # Validate required identifier
        rule_id = data.get("rule_id")
        if not rule_id:
            self.errors.append(f"{path.name}: Missing required field: 'rule_id'")
            return False

        # Validate required fields
        required_fields = ["criteria", "actions", "variables"]
        for field in required_fields:
            if field not in data:
                self.errors.append(f"{path.name}: Missing required field: {field}")
                return False

        # Validate rule structure using parser
        try:
            self.parser.parse_dict(data)
        except Exception as e:
            self.errors.append(f"{path.name}: Failed to parse rule: {e}")
            return False

        # Validate variable usage in actions (if variables are declared)
        if "variables" in data:
            self._validate_variable_usage(path.name, data)

        # Validate criteria structure
        self._validate_criteria(path.name, data.get("criteria", []))

        # Validate actions structure
        self._validate_actions(path.name, data.get("actions", []))

        # Enforce FORM_NAME for form rules
        if "forms" in str(path.parent):
            sets_form_name = any(
                a.get("type") == "set" and a.get("variable") == "FORM_NAME"
                for a in data.get("actions", [])
            )
            if not sets_form_name:
                self.errors.append(f"{path.name}: Form rule must set 'FORM_NAME' variable")
                return False

        print(f"  ✓ Rule ID: {rule_id}")
        if "variables" in data:
            print(f"  ✓ Global variables: {len(data['variables'].get('global', []))}")
            print(f"  ✓ Local variables: {len(data['variables'].get('local', []))}")
            print(f"  ✓ Derived variables: {len(data['variables'].get('derived', []))}")
        print(f"  ✓ Criteria: {len(data.get('criteria', []))}")
        print(f"  ✓ Actions: {len(data.get('actions', []))}")

        return True

    def _validate_variable_usage(self, rule_name: str, data: dict[str, Any]) -> None:
        """Validate that variables used in actions are declared."""
        declared_vars = set()
        if "variables" in data:
            declared_vars.update(data["variables"].get("global", []))
            declared_vars.update(data["variables"].get("local", []))
            declared_vars.update(data["variables"].get("derived", []))

        for action in data.get("actions", []):
            if "variable" in action:
                var_name = action["variable"]
                if declared_vars and var_name not in declared_vars:
                    self.warnings.append(
                        f"{rule_name}: Action uses undeclared variable: {var_name}"
                    )

            # Check derive action source variable
            if action.get("type") == "derive" and "from" in action:
                source_var = action["from"]
                if declared_vars and source_var not in declared_vars:
                    self.warnings.append(
                        f"{rule_name}: Derive action references undeclared "
                        f"source variable: {source_var}"
                    )

    def _validate_criteria(self, rule_name: str, criteria: list[Any]) -> None:
        """Validate criteria structure."""
        for i, criterion in enumerate(criteria, 1):
            if not isinstance(criterion, dict):
                self.errors.append(f"{rule_name}: Criterion {i} is not a dictionary")
                continue

            if "type" not in criterion:
                self.errors.append(f"{rule_name}: Criterion {i} missing 'type' field")

            # Validate nested criteria
            if "criteria" in criterion:
                self._validate_criteria(f"{rule_name} (nested)", criterion["criteria"])

    def _validate_actions(self, rule_name: str, actions: list[Any]) -> None:
        """Validate actions structure."""
        for i, action in enumerate(actions, 1):
            if not isinstance(action, dict):
                self.errors.append(f"{rule_name}: Action {i} is not a dictionary")
                continue

            if "type" not in action:
                self.errors.append(f"{rule_name}: Action {i} missing 'type' field")

            if "variable" not in action and action.get("type") != "extract":
                self.warnings.append(f"{rule_name}: Action {i} missing 'variable' field")

    def validate_directory(self, rules_dir: str) -> bool:
        """
        Validate all rule files in a directory.
        Supports both flat structure and global/forms subdirectories.
        """
        rules_path = Path(rules_dir)
        if not rules_path.exists():
            self.errors.append(f"Rules directory not found: {rules_dir}")
            return False

        # Find all YAML files (including in subdirectories)
        yaml_files = list(rules_path.rglob("*.yaml")) + list(rules_path.rglob("*.yml"))

        if not yaml_files:
            self.errors.append(f"No rule files found in {rules_dir}")
            return False

        print(f"Found {len(yaml_files)} rule file(s) to validate")

        # Validate each file
        all_valid = True
        for rule_file in sorted(yaml_files):
            if not self.validate_rule_file(str(rule_file)):
                all_valid = False

        return all_valid

    def print_summary(self) -> None:
        """Print validation summary."""
        print("\n" + "=" * 60)
        if self.errors:
            print(f"❌ Validation failed with {len(self.errors)} error(s):")
            for error in self.errors:
                print(f"  • {error}")
        else:
            print("✓ Validation passed!")

        if self.warnings:
            print(f"\n⚠️  {len(self.warnings)} warning(s):")
            for warning in self.warnings:
                print(f"  • {warning}")

        print("=" * 60)
