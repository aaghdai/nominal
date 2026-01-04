#!/usr/bin/env python3
"""
Rule validation tool for Nominal processor.

Validates rule files to ensure they conform to the expected schema and structure.
This is a thin wrapper around the RuleValidator class from the nominal package.
"""

import argparse
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from nominal.rules import RuleValidator  # noqa: E402


def main():
    """Main entry point for rule validation."""
    parser = argparse.ArgumentParser(description="Validate Nominal processor rule files")
    parser.add_argument(
        "rules_dir",
        type=str,
        help="Directory containing rule files to validate",
    )
    parser.add_argument(
        "--schema",
        type=str,
        default=None,
        help="Path to global variables schema file (default: rules_dir/global-variables.yaml)",
    )
    parser.add_argument(
        "--file",
        type=str,
        default=None,
        help="Validate a single rule file instead of a directory",
    )

    args = parser.parse_args()

    # Determine schema path
    if args.schema:
        schema_path = args.schema
    else:
        rules_path = Path(args.rules_dir)
        schema_path = str(rules_path / "global-variables.yaml")

    validator = RuleValidator(global_vars_schema_path=schema_path)

    # Validate
    if args.file:
        validator.load_global_variables_schema()
        success = validator.validate_rule_file(args.file)
    else:
        success = validator.validate_directory(args.rules_dir)

    validator.print_summary()

    sys.exit(0 if success and not validator.errors else 1)


if __name__ == "__main__":
    main()
