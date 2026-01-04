"""
Rules management module for Nominal.

This module provides utilities for loading and managing rule files,
separating rule management from the processor logic.
"""

from pathlib import Path
from typing import Optional

from nominal.logging import setup_logger

logger = setup_logger()


class RulesManager:
    """Manages rule files and schema loading."""

    def __init__(self, rules_dir: str, schema_path: Optional[str] = None):
        """
        Initialize rules manager.

        Args:
            rules_dir: Directory containing rule files
            schema_path: Optional path to global variables schema file.
                        If None, looks for global-variables.yaml in rules_dir.
        """
        self.rules_dir = Path(rules_dir)
        if not self.rules_dir.exists():
            raise FileNotFoundError(f"Rules directory not found: {rules_dir}")

        # Determine schema path
        if schema_path:
            self.schema_path = Path(schema_path)
        else:
            # Default: look for schema in rules directory
            self.schema_path = self.rules_dir / "global-variables.yaml"

        logger.debug(
            f"RulesManager initialized: rules_dir={self.rules_dir}, "
            f"schema_path={self.schema_path}"
        )

    def get_rule_files(self) -> list[Path]:
        """
        Get all rule files from the rules directory.

        Returns:
            List of paths to rule files (excludes global-variables.yaml)
        """
        yaml_files = [
            f
            for f in list(self.rules_dir.glob("*.yaml")) + list(self.rules_dir.glob("*.yml"))
            if f.name != "global-variables.yaml"
        ]
        return sorted(yaml_files)

    def get_schema_path(self) -> Optional[str]:
        """
        Get the path to the global variables schema file.

        Returns:
            Path to schema file if it exists, None otherwise
        """
        if self.schema_path.exists():
            return str(self.schema_path)
        return None

    def validate_schema_exists(self) -> bool:
        """Check if the schema file exists."""
        return self.schema_path.exists()
