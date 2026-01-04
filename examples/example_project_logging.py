#!/usr/bin/env python3
"""
Example demonstrating project-level logging configuration.
"""

import logging
from pathlib import Path
from nominal import configure_logging
from nominal.reader import NominalReader
from nominal.processor import NominalProcessor


def main():
    print("=" * 60)
    print("Project-Level Logging Configuration Example")
    print("=" * 60)
    
    # Configure logging for all components at once
    print("\n1. Configuring all components to INFO level (default)")
    configure_logging(logging.INFO)
    
    reader = NominalReader()
    rules_dir = Path(__file__).parent.parent / 'rules'
    processor = NominalProcessor(str(rules_dir))
    
    print("\n2. Configuring only processor to DEBUG level")
    configure_logging(logging.DEBUG, component='processor')
    
    # Now processor will show DEBUG logs, but reader stays at INFO
    sample_text = """
    Form W-2 Wage and Tax Statement
    Employee's social security number: 123-45-6789
    """
    
    print("\nProcessing document (processor will show DEBUG, reader will show INFO)...")
    result = processor.process_document(sample_text)
    
    if result:
        print(f"\n✓ Matched: {result['rule_id']}")
    
    print("\n3. Configuring all components to WARNING level")
    configure_logging(logging.WARNING)
    
    print("\nProcessing another document (only warnings/errors will be shown)...")
    result2 = processor.process_document(sample_text)
    
    if result2:
        print(f"\n✓ Matched: {result2['rule_id']}")


if __name__ == "__main__":
    main()

