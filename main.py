"""
Nominal CLI: Command-line interface for the Tax Document Processor.
"""

import argparse
import sys
from typing import Optional

from nominal.orchestrator import NominalOrchestrator


def main(args: Optional[list[str]] = None):
    """Main entry point for the nominal CLI."""
    parser = argparse.ArgumentParser(
        description="Nominal: Automated tax document processing and renaming."
    )
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # 'process' command
    process_parser = subparsers.add_parser("process", help="Process a directory of PDF files")
    process_parser.add_argument(
        "--input", "-i", required=True, help="Input directory containing PDF files"
    )
    process_parser.add_argument(
        "--output", "-o", required=True, help="Output directory for renamed files"
    )
    process_parser.add_argument(
        "--rules", "-r", required=True, help="Directory containing rule files"
    )
    process_parser.add_argument(
        "--pattern",
        "-p",
        default="{rule_id}_{LAST_NAME}_{TIN_LAST_FOUR}",
        help="Pattern for new filenames (default: {rule_id}_{LAST_NAME}_{TIN_LAST_FOUR})",
    )
    process_parser.add_argument("--no-ocr", action="store_true", help="Disable OCR fallback")

    parsed_args = parser.parse_args(args)

    if parsed_args.command == "process":
        try:
            orchestrator = NominalOrchestrator(
                rules_dir=parsed_args.rules, ocr_fallback=not parsed_args.no_ocr
            )
            stats = orchestrator.process_directory(
                input_dir=parsed_args.input,
                output_dir=parsed_args.output,
                filename_pattern=parsed_args.pattern,
            )

            print("\nProcessing Summary:")
            print(f"  Total:     {stats['total']}")
            print(f"  Matched:   {stats['matched']}")
            print(f"  Unmatched: {stats['unmatched']}")
            print(f"  Errors:    {stats['errors']}")

            if stats["errors"] > 0 or stats["unmatched"] > 0:
                print(
                    f"\nSome files were not processed correctly."
                    f" Check {parsed_args.output}/unmatched/"
                )
                sys.exit(1)
            else:
                print("\nAll files processed successfully!")
                sys.exit(0)

        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(0)


if __name__ == "__main__":
    main()
