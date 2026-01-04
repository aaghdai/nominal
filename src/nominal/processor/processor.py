"""
Main processor class for orchestrating rule matching and variable extraction.
"""

from typing import Any

from nominal.logging import setup_logger
from nominal.rules import Rule, RuleParser, RulesManager, RuleValidator

logger = setup_logger()


class NominalProcessor:
    """Main processor class that orchestrates rule matching and variable extraction."""

    def __init__(
        self,
        rules_dir: str | None = None,
        schema_path: str | None = None,
    ):
        """
        Initialize the processor.

        Args:
            rules_dir: Directory containing rule files. If None, rules must be loaded manually.
            schema_path: Optional path to global variables schema file.
                        If None and rules_dir is provided, looks for
                        global-variables.yaml in rules_dir.
        """
        self.rules: list[Rule] = []
        self.parser = RuleParser()
        self.global_variables: dict[str, str] = {}  # Batch-level global variables

        logger.info("NominalProcessor initialized")

        if rules_dir:
            self.load_rules(rules_dir, schema_path=schema_path)

    def load_rules(
        self,
        rules_dir: str,
        schema_path: str | None = None,
        validate: bool = True,
    ):
        """
        Load all rule files from a directory.

        Args:
            rules_dir: Directory containing rule files
            schema_path: Optional path to global variables schema file.
                        If None, looks for global-variables.yaml in rules_dir.
            validate: Whether to validate rules before loading (default: True)
        """
        logger.info(f"Loading rules from directory: {rules_dir}")

        # Use RulesManager to handle rules directory structure
        rules_manager = RulesManager(rules_dir, schema_path=schema_path)

        # Validate rules before loading if requested
        if validate:
            self._validate_rules(rules_manager)

        # Get rule files from manager
        rule_files = rules_manager.get_rule_files()

        if not rule_files:
            logger.warning(f"No rule files (*.yaml or *.yml) found in {rules_dir}")

        for rule_file in rule_files:
            try:
                rule = self.parser.parse_file(str(rule_file))
                self.rules.append(rule)
                logger.info(f"✓ Loaded rule: {rule.rule_id} from {rule_file.name}")
            except Exception as e:
                logger.error(f"Failed to load rule from {rule_file}: {e}")
                raise

        logger.info(f"Successfully loaded {len(self.rules)} rule(s)")

    def _validate_rules(self, rules_manager: RulesManager) -> None:
        """Validate all rules using the rules manager."""
        logger.info("Validating rules before loading...")

        schema_path = rules_manager.get_schema_path()
        validator = RuleValidator(global_vars_schema_path=schema_path)

        # Validate all rules
        try:
            success = validator.validate_directory(str(rules_manager.rules_dir))
            if validator.errors:
                error_msg = f"Rule validation failed with {len(validator.errors)} error(s)"
                logger.error(error_msg)
                for error in validator.errors:
                    logger.error(f"  • {error}")
                raise ValueError(error_msg)

            if validator.warnings:
                logger.warning(
                    f"Rule validation completed with {len(validator.warnings)} " f"warning(s)"
                )
                for warning in validator.warnings:
                    logger.warning(f"  • {warning}")

            if success:
                logger.info("✓ All rules validated successfully")
        except Exception as e:
            logger.error(f"Rule validation failed: {e}")
            raise

    def load_rule(self, rule_path: str, validate: bool = False):
        """
        Load a single rule file.

        Args:
            rule_path: Path to a single rule file
            validate: Whether to validate the rule (requires schema path)
        """
        logger.info(f"Loading single rule: {rule_path}")

        if validate:
            logger.warning("Single rule validation not yet implemented")

        try:
            rule = self.parser.parse_file(rule_path)
            self.rules.append(rule)
            logger.info(f"✓ Loaded rule: {rule.rule_id}")
        except Exception as e:
            logger.error(f"Failed to load rule from {rule_path}: {e}")
            raise

    def process_document(self, text: str, enforce_global: bool = False) -> dict[str, Any] | None:
        """
        Process a single document and extract variables.

        Args:
            text: The document text to process
            enforce_global: If True, check that global variables match existing values

        Returns:
            Dict with 'rule_id', 'global_variables', 'local_variables', 'derived_variables'
            if a match is found. None otherwise.
        """
        logger.info(f"Processing document ({len(text)} characters)")

        if not self.rules:
            logger.warning("No rules loaded, cannot process document")
            return None

        for rule in self.rules:
            result = rule.apply(text)
            if result:
                # Separate variables by scope based on rule definition
                all_vars = result["variables"]
                global_vars = {k: v for k, v in all_vars.items() if k in rule.global_variables}
                local_vars = {k: v for k, v in all_vars.items() if k in rule.local_variables}
                derived_vars = {k: v for k, v in all_vars.items() if k in rule.derived_variables}

                # Check global variable consistency if enforcing
                if enforce_global:
                    conflicts = []
                    for var_name, var_value in global_vars.items():
                        if var_name in self.global_variables:
                            if self.global_variables[var_name] != var_value:
                                conflicts.append(
                                    f"{var_name}: '{self.global_variables[var_name]}' "
                                    f"vs '{var_value}'"
                                )

                    if conflicts:
                        logger.warning(
                            f"Global variable conflict detected, skipping document. "
                            f"Conflicts: {', '.join(conflicts)}"
                        )
                        continue

                # Update batch-level global variables
                for key, value in global_vars.items():
                    if key in self.global_variables:
                        if self.global_variables[key] != value:
                            logger.warning(
                                f"Global variable conflict: {key} = '{self.global_variables[key]}' "
                                f"vs '{value}' (keeping first value)"
                            )
                    else:
                        self.global_variables[key] = value

                logger.info(f"✓ Document matched rule {rule.rule_id}")
                logger.info(
                    f"  Global: {len(global_vars)} var(s), Local: {len(local_vars)} var(s), "
                    f"Derived: {len(derived_vars)} var(s)"
                )

                return {
                    "rule_id": result["rule_id"],
                    "global_variables": global_vars,
                    "local_variables": local_vars,
                    "derived_variables": derived_vars,
                    "rule_description": result["rule_description"],
                }

        logger.info("✗ Document did not match any rules")
        return None

    def process_batch(
        self, documents: list[str], enforce_global: bool = True
    ) -> list[dict[str, Any] | None]:
        """
        Process a batch of documents.

        Args:
            documents: List of document texts to process
            enforce_global: If True, enforce global variable consistency across batch

        Returns:
            List of results, one per document. None for documents that don't match.
        """
        logger.info(f"Processing batch of {len(documents)} document(s)")

        # Reset global variables for new batch
        self.reset_global_variables()

        results = []
        for i, text in enumerate(documents, 1):
            logger.info(f"Processing document {i}/{len(documents)}")
            result = self.process_document(text, enforce_global=enforce_global)
            results.append(result)

            if result is None:
                logger.warning(f"Document {i} did not match any rules")

        matched_count = sum(1 for r in results if r is not None)
        logger.info(
            f"Batch processing complete: {matched_count}/{len(documents)} documents matched"
        )

        return results

    def get_global_variables(self) -> dict[str, str]:
        """Get the current batch-level global variables."""
        return self.global_variables.copy()

    def reset_global_variables(self):
        """Reset the batch-level global variables."""
        logger.debug("Resetting global variables")
        self.global_variables = {}
