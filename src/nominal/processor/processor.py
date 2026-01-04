"""
Main processor class for orchestrating rule matching and variable extraction.

Processing Flow:
1. Apply global rules to each document to extract common variables
   (e.g., TIN_LAST_FOUR, FIRST_NAME, LAST_NAME)
2. Apply form rules to classify each document (e.g., W2, 1099-DIV)
3. Return the first matching form rule for classification
4. Log unmatched documents as errors
"""

from typing import Any

from nominal.logging import setup_logger
from nominal.rules import Rule, RuleParser, RulesManager

logger = setup_logger()


class NominalProcessor:
    """Main processor class that orchestrates rule matching and variable extraction."""

    def __init__(self, rules_dir: str | None = None):
        """
        Initialize the processor.

        Args:
            rules_dir: Directory containing rule files (with global/ and forms/ subdirs).
                      If None, rules must be loaded manually.
        """
        self.global_rules: list[Rule] = []
        self.form_rules: list[Rule] = []
        self.parser = RuleParser()
        self.global_variables: dict[str, str] = {}  # Batch-level global variables
        self.unmatched_documents: list[dict[str, Any]] = []  # Track unmatched docs

        logger.info("NominalProcessor initialized")

        if rules_dir:
            self.load_rules(rules_dir)

    def load_rules(self, rules_dir: str):
        """
        Load all rule files from a directory.

        Args:
            rules_dir: Root directory containing rules (with global/ and forms/ subdirs)
        """
        logger.info(f"Loading rules from directory: {rules_dir}")

        rules_manager = RulesManager(rules_dir)

        # Load global rules
        global_rule_files = rules_manager.get_global_rule_files()
        for rule_file in global_rule_files:
            try:
                rule = self.parser.parse_file(str(rule_file))
                self.global_rules.append(rule)
                logger.info(f"✓ Loaded global rule: {rule.rule_id} from {rule_file.name}")
            except Exception as e:
                logger.error(f"Failed to load global rule from {rule_file}: {e}")
                raise

        # Load form rules
        form_rule_files = rules_manager.get_form_rule_files()
        for rule_file in form_rule_files:
            try:
                rule = self.parser.parse_file(str(rule_file))
                self.form_rules.append(rule)
                logger.info(f"✓ Loaded form rule: {rule.rule_id} from {rule_file.name}")
            except Exception as e:
                logger.error(f"Failed to load form rule from {rule_file}: {e}")
                raise

        logger.info(
            f"Loaded {len(self.global_rules)} global rule(s), "
            f"{len(self.form_rules)} form rule(s)"
        )

    def load_rule(self, rule_path: str, rule_type: str = "form"):
        """
        Load a single rule file.

        Args:
            rule_path: Path to a single rule file
            rule_type: Type of rule - 'global' or 'form' (default: 'form')
        """
        logger.info(f"Loading single {rule_type} rule: {rule_path}")

        try:
            rule = self.parser.parse_file(rule_path)
            if rule_type == "global":
                self.global_rules.append(rule)
            else:
                self.form_rules.append(rule)
            logger.info(f"✓ Loaded {rule_type} rule: {rule.rule_id}")
        except Exception as e:
            logger.error(f"Failed to load rule from {rule_path}: {e}")
            raise

    def _apply_global_rules(self, text: str) -> dict[str, Any]:
        """
        Apply all global rules to extract variables from a document.

        Args:
            text: The document text

        Returns:
            Dict of extracted variables from all global rules
        """
        extracted_vars: dict[str, Any] = {}

        for rule in self.global_rules:
            result = rule.apply(text)
            if result:
                # Merge all extracted variables
                all_vars = result.get("variables", {})
                for key, value in all_vars.items():
                    if value and key not in extracted_vars:
                        extracted_vars[key] = value
                        logger.debug(f"Global extraction: {key} = '{value}'")

        return extracted_vars

    def _classify_document(self, text: str) -> tuple[Rule | None, dict[str, Any] | None]:
        """
        Classify a document by finding the first matching form rule.

        Args:
            text: The document text

        Returns:
            Tuple of (matching rule, result dict) or (None, None) if no match
        """
        for rule in self.form_rules:
            result = rule.apply(text)
            if result:
                logger.debug(f"Document matched form rule: {rule.rule_id}")
                return rule, result

        return None, None

    def process_document(
        self,
        text: str,
        document_id: str | None = None,
        enforce_global: bool = False,
    ) -> dict[str, Any] | None:
        """
        Process a single document: extract global variables, then classify.

        Args:
            text: The document text to process
            document_id: Optional identifier for the document (for error logging)
            enforce_global: If True, check that global variables match existing values

        Returns:
            Dict with 'rule_id', 'global_variables', 'local_variables'
            if classified. None if unmatched.
        """
        doc_id = document_id or f"doc_{len(self.unmatched_documents) + 1}"
        logger.info(f"Processing document: {doc_id} ({len(text)} characters)")

        # Step 1: Apply global rules to extract variables
        extracted_global_vars = self._apply_global_rules(text)
        logger.debug(f"Extracted {len(extracted_global_vars)} global variable(s) from document")

        # Step 2: Classify document using form rules
        matched_rule, classification_result = self._classify_document(text)

        if matched_rule is None:
            # Document didn't match any form rule
            error_entry = {
                "document_id": doc_id,
                "text_preview": text[:200] + "..." if len(text) > 200 else text,
                "extracted_vars": extracted_global_vars,
            }
            self.unmatched_documents.append(error_entry)
            logger.error(f"✗ Document '{doc_id}' did not match any form rule")
            return None

        # Step 3: Combine global and local variables
        local_vars = classification_result.get("variables", {})

        # Check global variable consistency if enforcing
        if enforce_global:
            conflicts = []
            for var_name, var_value in extracted_global_vars.items():
                if var_name in self.global_variables:
                    if self.global_variables[var_name] != var_value:
                        conflicts.append(
                            f"{var_name}: '{self.global_variables[var_name]}' " f"vs '{var_value}'"
                        )

            if conflicts:
                logger.warning(
                    f"Global variable conflict in '{doc_id}'. " f"Conflicts: {', '.join(conflicts)}"
                )
                # Keep first values (don't override)

        # Update batch-level global variables (first value wins)
        for key, value in extracted_global_vars.items():
            if key not in self.global_variables:
                self.global_variables[key] = value

        logger.info(f"✓ Document '{doc_id}' classified as: {matched_rule.rule_id}")
        logger.info(
            f"  Global: {len(extracted_global_vars)} var(s), " f"Local: {len(local_vars)} var(s)"
        )

        return {
            "rule_id": matched_rule.rule_id,
            "document_id": doc_id,
            "global_variables": extracted_global_vars,
            "local_variables": local_vars,
            "rule_description": matched_rule.description,
        }

    def process_batch(
        self,
        documents: list[str] | list[tuple[str, str]],
        enforce_global: bool = True,
    ) -> list[dict[str, Any] | None]:
        """
        Process a batch of documents.

        Args:
            documents: List of document texts, or list of (doc_id, text) tuples
            enforce_global: If True, enforce global variable consistency across batch

        Returns:
            List of results, one per document. None for unmatched documents.
        """
        logger.info(f"Processing batch of {len(documents)} document(s)")

        # Reset state for new batch
        self.reset_global_variables()
        self.unmatched_documents = []

        results = []
        for i, item in enumerate(documents, 1):
            if isinstance(item, tuple):
                doc_id, text = item
            else:
                doc_id = f"doc_{i}"
                text = item

            logger.info(f"Processing document {i}/{len(documents)}: {doc_id}")
            result = self.process_document(text, document_id=doc_id, enforce_global=enforce_global)
            results.append(result)

        # Report summary
        matched_count = sum(1 for r in results if r is not None)
        unmatched_count = len(self.unmatched_documents)

        logger.info(f"Batch complete: {matched_count} matched, {unmatched_count} unmatched")

        if unmatched_count > 0:
            logger.error(f"Unmatched documents ({unmatched_count}):")
            for entry in self.unmatched_documents:
                logger.error(f"  • {entry['document_id']}")

        return results

    def get_global_variables(self) -> dict[str, str]:
        """Get the current batch-level global variables."""
        return self.global_variables.copy()

    def get_unmatched_documents(self) -> list[dict[str, Any]]:
        """Get list of documents that didn't match any form rule."""
        return self.unmatched_documents.copy()

    def reset_global_variables(self):
        """Reset the batch-level global variables."""
        logger.debug("Resetting global variables")
        self.global_variables = {}

    # Legacy compatibility - expose combined rules list
    @property
    def rules(self) -> list[Rule]:
        """Get all rules (global + form) for backward compatibility."""
        return self.global_rules + self.form_rules
