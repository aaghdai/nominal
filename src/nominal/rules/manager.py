"""
Rules management module for Nominal.

This module provides utilities for loading and managing rule files,
separating rule management from the processor logic.

Directory Structure:
    rules/
    ├── global/      # Global extraction rules (applied to all documents)
    │   └── *.yaml
    └── forms/       # Form classification rules (one per form type)
        └── *.yaml
"""

from pathlib import Path

from nominal.logging import setup_logger

logger = setup_logger()


class RulesManager:
    """Manages rule files and schema loading."""

    def __init__(self, rules_dir: str):
        """
        Initialize rules manager.

        Args:
            rules_dir: Root directory containing rules (with global/ and forms/ subdirs)
        """
        self.rules_dir = Path(rules_dir)
        if not self.rules_dir.exists():
            raise FileNotFoundError(f"Rules directory not found: {rules_dir}")

        self.global_dir = self.rules_dir / "global"
        self.forms_dir = self.rules_dir / "forms"

        logger.debug(
            f"RulesManager initialized: rules_dir={self.rules_dir}, "
            f"global_dir={self.global_dir}, forms_dir={self.forms_dir}"
        )

    def get_global_rule_files(self) -> list[Path]:
        """
        Get all global rule files from the global/ subdirectory.

        Returns:
            List of paths to global rule files
        """
        if not self.global_dir.exists():
            logger.warning(f"Global rules directory not found: {self.global_dir}")
            return []

        yaml_files = list(self.global_dir.glob("*.yaml")) + list(self.global_dir.glob("*.yml"))
        return sorted(yaml_files)

    def get_form_rule_files(self) -> list[Path]:
        """
        Get all form rule files from the forms/ subdirectory.

        Returns:
            List of paths to form rule files
        """
        if not self.forms_dir.exists():
            logger.warning(f"Forms rules directory not found: {self.forms_dir}")
            return []

        yaml_files = list(self.forms_dir.glob("*.yaml")) + list(self.forms_dir.glob("*.yml"))
        return sorted(yaml_files)

    def get_rule_files(self) -> list[Path]:
        """
        Get all rule files (both global and form rules).

        Returns:
            List of all rule file paths
        """
        return self.get_global_rule_files() + self.get_form_rule_files()

    def has_global_rules(self) -> bool:
        """Check if global rules directory exists and has rules."""
        return len(self.get_global_rule_files()) > 0

    def has_form_rules(self) -> bool:
        """Check if forms rules directory exists and has rules."""
        return len(self.get_form_rule_files()) > 0
