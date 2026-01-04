#!/usr/bin/env python3
"""
Advanced Document Processing with Derived Variables

This script demonstrates how to use orchestrator-level derived variables
to compute additional values from extracted variables for filename generation.

Derived variables are useful when you need to:
- Transform extracted values (e.g., extract last name from full name)
- Compute new values based on multiple extracted fields
- Apply custom formatting or business logic
- Add context that isn't directly in the document

Usage:
    uv run nominal-derived --input INPUT_DIR --output OUTPUT_DIR --rules RULES_DIR

    Or run directly:
    uv run python scripts/process_with_derived_vars.py \\
        --input INPUT_DIR --output OUTPUT_DIR --rules RULES_DIR
"""

import argparse
import sys
from pathlib import Path
from typing import Any

from nominal.orchestrator import NominalOrchestrator

# ============================================================================
# Derived Variable Functions
# ============================================================================
# Each function takes a dictionary of all extracted variables and returns
# a single derived value. Functions should handle missing keys gracefully.
# ============================================================================


def derive_last_name(all_vars: dict[str, Any]) -> str:
    """
    Extract last name from FULL_NAME variable.

    Example: "JOHN SMITH" -> "SMITH"
    """
    full_name = all_vars.get("FULL_NAME", "")
    if full_name:
        parts = full_name.strip().split()
        return parts[-1] if parts else "UNKNOWN"
    return "UNKNOWN"


def derive_first_name(all_vars: dict[str, Any]) -> str:
    """
    Extract first name from FULL_NAME variable.

    Example: "JOHN SMITH" -> "JOHN"
    """
    full_name = all_vars.get("FULL_NAME", "")
    if full_name:
        parts = full_name.strip().split()
        return parts[0] if parts else "UNKNOWN"
    return "UNKNOWN"


def derive_full_tin(all_vars: dict[str, Any]) -> str:
    """
    Format TIN (Tax Identification Number) with dashes.

    If we have SSN, EIN, or TIN variables, format them nicely.
    Example: "123456789" -> "123-45-6789"
    """
    # Try to get TIN from various possible variable names
    tin = all_vars.get("SSN") or all_vars.get("EIN") or all_vars.get("TIN", "")

    if tin:
        # Remove any existing dashes or spaces
        tin_digits = "".join(c for c in tin if c.isdigit())

        # Format as SSN if 9 digits
        if len(tin_digits) == 9:
            return f"{tin_digits[:3]}-{tin_digits[3:5]}-{tin_digits[5:]}"

    return "UNKNOWN"


def derive_name_tin_combo(all_vars: dict[str, Any]) -> str:
    """
    Create a composite identifier from last name and TIN last 4.

    Example: "SMITH_6789"
    """
    last_name = derive_last_name(all_vars)
    tin_last_four = all_vars.get("TIN_LAST_FOUR", "XXXX")
    return f"{last_name}_{tin_last_four}"


def derive_document_year(all_vars: dict[str, Any]) -> str:
    """
    Extract year from document or use current year as fallback.

    This is a placeholder - in practice, you'd extract from document text
    or filename.
    """
    # Try to get from various year-related fields
    year = all_vars.get("TAX_YEAR") or all_vars.get("YEAR")

    if year:
        # Extract 4-digit year
        year_str = str(year)
        if len(year_str) >= 4:
            return year_str[:4]

    # Fallback: could use current year or "UNKNOWN"
    from datetime import datetime

    return str(datetime.now().year)


# ============================================================================
# Main Script
# ============================================================================


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Process tax documents with derived variables for advanced filename patterns.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process with default derived variables
  %(prog)s --input ./input --output ./output --rules ./rules

  # Use custom filename pattern with derived variables
  %(prog)s -i ./input -o ./output -r ./rules \\
    --pattern "{YEAR}_{LAST_NAME}_{FIRST_NAME}_{rule_id}_{TIN_LAST_FOUR}"

Available Derived Variables:
  LAST_NAME         - Last name extracted from FULL_NAME
  FIRST_NAME        - First name extracted from FULL_NAME
  FULL_TIN          - Formatted TIN with dashes (XXX-XX-XXXX)
  NAME_TIN_COMBO    - Combined last name and TIN last 4
  YEAR              - Document year (extracted or current year)

Note: Derived variables are computed AFTER document processing and can
reference any variables extracted by rules (FULL_NAME, TIN_LAST_FOUR, etc.)
        """,
    )

    parser.add_argument(
        "--input",
        "-i",
        required=True,
        help="Input directory containing PDF files to process",
    )
    parser.add_argument(
        "--output",
        "-o",
        required=True,
        help="Output directory for renamed files",
    )
    parser.add_argument(
        "--rules",
        "-r",
        required=True,
        help="Directory containing rule YAML files",
    )
    parser.add_argument(
        "--pattern",
        "-p",
        default="{rule_id}_{LAST_NAME}_{TIN_LAST_FOUR}",
        help="Filename pattern (default: {rule_id}_{LAST_NAME}_{TIN_LAST_FOUR})",
    )
    parser.add_argument(
        "--no-ocr",
        action="store_true",
        help="Disable OCR fallback for image-based PDFs",
    )

    args = parser.parse_args()

    # Validate paths
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input directory not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    rules_path = Path(args.rules)
    if not rules_path.exists():
        print(f"Error: Rules directory not found: {args.rules}", file=sys.stderr)
        sys.exit(1)

    # Define derived variables
    # These functions will be applied after document processing
    derived_variables = {
        "LAST_NAME": derive_last_name,
        "FIRST_NAME": derive_first_name,
        "FULL_TIN": derive_full_tin,
        "NAME_TIN_COMBO": derive_name_tin_combo,
        "YEAR": derive_document_year,
    }

    print("=" * 70)
    print("Nominal: Advanced Document Processing with Derived Variables")
    print("=" * 70)
    print(f"\nInput:   {args.input}")
    print(f"Output:  {args.output}")
    print(f"Rules:   {args.rules}")
    print(f"Pattern: {args.pattern}")
    print("\nDerived Variables Available:")
    for var_name, func in derived_variables.items():
        doc = func.__doc__.strip().split("\n")[0] if func.__doc__ else "No description"
        print(f"  - {var_name:20} {doc}")
    print("\n" + "=" * 70 + "\n")

    try:
        # Initialize orchestrator with derived variables
        orchestrator = NominalOrchestrator(
            rules_dir=args.rules,
            ocr_fallback=not args.no_ocr,
            derived_variables=derived_variables,
        )

        # Process directory
        stats = orchestrator.process_directory(
            input_dir=args.input,
            output_dir=args.output,
            filename_pattern=args.pattern,
        )

        # Print results
        print("\n" + "=" * 70)
        print("Processing Summary")
        print("=" * 70)
        print(f"  Total Files:     {stats['total']}")
        print(f"  ✓ Matched:       {stats['matched']}")
        print(f"  ✗ Unmatched:     {stats['unmatched']}")
        print(f"  ⚠ Errors:        {stats['errors']}")
        print("=" * 70 + "\n")

        if stats["errors"] > 0 or stats["unmatched"] > 0:
            print(
                f"⚠ Some files were not processed correctly.\n"
                f"  Check: {args.output}/unmatched/\n"
            )
            sys.exit(1)
        else:
            print("✓ All files processed successfully!\n")
            sys.exit(0)

    except Exception as e:
        print(f"\n✗ Error: {e}\n", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
