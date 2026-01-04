"""
Rule validation for Nominal processor.

Validates rule files to ensure they conform to the expected schema and structure.
"""

from pathlib import Path
from typing import Any

import yaml

from nominal.logging import setup_logger

from .parser import RuleParser

logger = setup_logger()


class RuleValidator:
    """Validates rule files against schema and consistency requirements."""

    def __init__(self, global_vars_schema_path: str | None = None):
        """Initialize validator with optional global variables schema."""
        self.global_vars_schema_path = global_vars_schema_path
        self.global_variables: set[str] = set()
        self.parser = RuleParser()
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def load_global_variables_schema(self) -> None:
        """Load global variables schema from file."""
        if not self.global_vars_schema_path:
            self.warnings.append(
                "No global variables schema specified, " "skipping global var validation"
            )
            return

        schema_path = Path(self.global_vars_schema_path)
        if not schema_path.exists():
            self.errors.append(f"Global variables schema file not found: {schema_path}")
            return

        try:
            with open(schema_path) as f:
                data = yaml.safe_load(f)

            if "global_variables" not in data:
                self.errors.append("Global variables schema missing 'global_variables' key")
                return

            self.global_variables = set(data["global_variables"])
            print(f"✓ Loaded {len(self.global_variables)} global variables from schema")
        except Exception as e:
            self.errors.append(f"Failed to load global variables schema: {e}")

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

        # Validate required fields
        required_fields = ["form_name", "variables", "criteria", "actions"]
        for field in required_fields:
            if field not in data:
                self.errors.append(f"{path.name}: Missing required field: {field}")
                return False

        # Validate rule structure using parser
        try:
            self.parser.parse_dict(data)  # Validate structure, result not needed
        except Exception as e:
            self.errors.append(f"{path.name}: Failed to parse rule: {e}")
            return False

        # Validate global variables against schema
        if self.global_variables:
            rule_global_vars = set(data["variables"].get("global", []))
            invalid_vars = rule_global_vars - self.global_variables
            if invalid_vars:
                invalid_list = ", ".join(invalid_vars)
                self.errors.append(
                    f"{path.name}: Invalid global variables (not in schema): " f"{invalid_list}"
                )

        # Validate variable usage in actions
        self._validate_variable_usage(path.name, data)

        # Validate criteria structure
        self._validate_criteria(path.name, data.get("criteria", []))

        # Validate actions structure
        self._validate_actions(path.name, data.get("actions", []))

        print(f"  ✓ Rule ID: {data['form_name']}")
        print(f"  ✓ Global variables: {len(data['variables'].get('global', []))}")
        print(f"  ✓ Local variables: {len(data['variables'].get('local', []))}")
        print(f"  ✓ Derived variables: {len(data['variables'].get('derived', []))}")
        print(f"  ✓ Criteria: {len(data.get('criteria', []))}")
        print(f"  ✓ Actions: {len(data.get('actions', []))}")

        return True

    def _validate_variable_usage(self, rule_name: str, data: dict[str, Any]) -> None:
        """Validate that variables used in actions are declared."""
        declared_vars = set()
        declared_vars.update(data["variables"].get("global", []))
        declared_vars.update(data["variables"].get("local", []))
        declared_vars.update(data["variables"].get("derived", []))

        for action in data.get("actions", []):
            if "variable" in action:
                var_name = action["variable"]
                if var_name not in declared_vars:
                    self.warnings.append(
                        f"{rule_name}: Action uses undeclared variable: {var_name}"
                    )

            # Check derive action source variable
            if action.get("type") == "derive" and "from" in action:
                source_var = action["from"]
                if source_var not in declared_vars:
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
        """Validate all rule files in a directory."""
        rules_path = Path(rules_dir)
        if not rules_path.exists():
            self.errors.append(f"Rules directory not found: {rules_dir}")
            return False

        # Load global variables schema if provided
        if self.global_vars_schema_path:
            self.load_global_variables_schema()

        # Find all YAML files
        yaml_files = list(rules_path.glob("*.yaml")) + list(rules_path.glob("*.yml"))
        yaml_files = [f for f in yaml_files if f.name != "global-variables.yaml"]

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
