#!/usr/bin/env python3
"""
Rule Validation Tool

Validates rule files in the rules/ directory to ensure they conform
to the expected schema and structure.

Usage:
    python tools/validate_rules.py [rules_directory]

If no rules directory is specified, defaults to 'rules/' in the project root.

Exit codes:
    0: Validation passed
    1: Validation failed
"""

import argparse
import sys
from pathlib import Path

from nominal.rules import RuleValidator


def main():
    parser = argparse.ArgumentParser(
        description="Validate Nominal rule files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    %(prog)s                    # Validate rules in default location (rules/)
    %(prog)s rules/             # Validate all rules in rules directory
    %(prog)s rules/forms/       # Validate only form rules
    %(prog)s rules/global/      # Validate only global rules
""",
    )

    parser.add_argument(
        "rules_dir",
        nargs="?",
        default=None,
        help="Directory containing rule files (default: rules/)",
    )

    args = parser.parse_args()

    # Determine rules directory
    if args.rules_dir:
        rules_dir = Path(args.rules_dir)
    else:
        # Find project root (look for pyproject.toml)
        current = Path.cwd()
        while current != current.parent:
            if (current / "pyproject.toml").exists():
                break
            current = current.parent
        rules_dir = current / "rules"

    if not rules_dir.exists():
        print(f"Error: Rules directory not found: {rules_dir}")
        sys.exit(1)

    print(f"Validating rules in: {rules_dir}")
    print("=" * 60)

    # Create validator and run validation
    validator = RuleValidator()
    success = validator.validate_directory(str(rules_dir))

    # Print summary
    validator.print_summary()

    # Exit with appropriate code
    sys.exit(0 if success and not validator.errors else 1)


if __name__ == "__main__":
    main()
