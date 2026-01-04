#!/usr/bin/env python3
"""
Example script demonstrating different logging levels.
"""

import logging
from pathlib import Path
from nominal.processor import NominalProcessor
from nominal.reader import NominalReader
from nominal import configure_logging


def main():
    print("=" * 60)
    print("Example 1: INFO Level (default)")
    print("Shows actionable information")
    print("=" * 60)
    
    # INFO is the default level
    processor = NominalProcessor()
    rules_dir = Path(__file__).parent.parent / 'rules'
    processor.load_rules(str(rules_dir))
    
    sample_text = """
    Form W-2 Wage and Tax Statement
    Employee's social security number: 123-45-6789
    Employee's name and address:
    Jane Doe
    123 Main Street
    """
    
    print("\nProcessing document...")
    result = processor.process_document(sample_text)
    
    if result:
        print(f"\n✓ Matched: {result['rule_id']}")
    
    print("\n" + "=" * 60)
    print("Example 2: DEBUG Level")
    print("Shows detailed debugging information")
    print("=" * 60)
    
    # Reset and enable DEBUG level
    configure_logging(logging.DEBUG)
    processor = NominalProcessor()
    rules_dir = Path(__file__).parent.parent / 'rules'
    processor.load_rules(str(rules_dir))
    
    print("\nProcessing document with DEBUG logging...")
    result = processor.process_document(sample_text)
    
    if result:
        print(f"\n✓ Matched: {result['rule_id']}")
    
    print("\n" + "=" * 60)
    print("Example 3: WARNING Level")
    print("Shows only warnings and errors")
    print("=" * 60)
    
    # Set to WARNING level
    configure_logging(logging.WARNING)
    processor = NominalProcessor()
    rules_dir = Path(__file__).parent.parent / 'rules'
    processor.load_rules(str(rules_dir))
    
    print("\nProcessing document (only warnings/errors will be shown)...")
    result = processor.process_document(sample_text)
    
    if result:
        print(f"\n✓ Matched: {result['rule_id']}")
    
    # Process another document to trigger a global variable conflict warning
    sample_text2 = """
    Form W-2 Wage and Tax Statement
    Employee's social security number: 999-88-7777
    Employee's name and address:
    John Smith
    456 Oak Avenue
    """
    
    print("\nProcessing another document with different SSN...")
    result2 = processor.process_document(sample_text2)
    
    if result2:
        print(f"\n✓ Matched: {result2['rule_id']}")
    
    print("\n" + "=" * 60)
    print("Example 4: Demonstrating ERROR logging")
    print("Shows error conditions")
    print("=" * 60)
    
    # Reset to INFO level for this example
    configure_logging(logging.INFO)
    processor = NominalProcessor()
    rules_dir = Path(__file__).parent.parent / 'rules'
    processor.load_rules(str(rules_dir))
    
    # Process a document that won't match any rules
    bad_text = "This is just some random text with no tax form content."
    
    print("\nProcessing invalid document...")
    result = processor.process_document(bad_text)
    
    if not result:
        print("\n✗ No rules matched (as expected)")


if __name__ == "__main__":
    main()

