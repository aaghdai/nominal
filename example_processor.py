#!/usr/bin/env python3
"""
Example script demonstrating how to use the Nominal Processor
to identify and extract information from tax documents.
"""

from nominal.reader import NominalReader
from nominal.processor import NominalProcessor
import sys
from pathlib import Path


def main():
    """Main function demonstrating processor usage."""
    
    # Initialize the reader and processor
    reader = NominalReader(ocr_fallback=True)
    
    # Load rules from the rules directory
    rules_dir = Path(__file__).parent / 'rules'
    processor = NominalProcessor(str(rules_dir))
    
    print(f"Loaded {len(processor.rules)} rule(s):")
    for rule in processor.rules:
        print(f"  - {rule.form_name}: {rule.description}")
    print()
    
    # Example 1: Process a sample W2 PDF
    print("=" * 60)
    print("Example 1: Processing Sample W2 PDF")
    print("=" * 60)
    
    w2_pdf = Path(__file__).parent / 'test' / 'fixtures' / 'Sample-W2.pdf'
    if w2_pdf.exists():
        # Read the PDF
        print(f"Reading: {w2_pdf}")
        text = reader.read_pdf(str(w2_pdf))
        print(f"Extracted {len(text)} characters of text")
        
        # Process the document
        result = processor.process_document(text)
        
        if result:
            print(f"\n✓ Identified as: {result['form_name']}")
            print(f"  Description: {result['rule_description']}")
            print(f"\n  Extracted Variables:")
            for var_name, var_value in result['variables'].items():
                print(f"    {var_name}: {var_value}")
        else:
            print("\n✗ No matching form found")
    else:
        print(f"Sample W2 not found at: {w2_pdf}")
    
    print()
    
    # Example 2: Process a sample text directly
    print("=" * 60)
    print("Example 2: Processing Sample Text")
    print("=" * 60)
    
    sample_text = """
    Form W-2 Wage and Tax Statement
    
    Employee's social security number: 987-65-4321
    
    Employee's name and address:
    Jane Doe
    456 Oak Avenue
    Springfield, IL 62701
    
    Wages, tips, other compensation: $75,000.00
    Federal income tax withheld: $8,500.00
    """
    
    print("Processing sample W2 text...")
    result = processor.process_document(sample_text)
    
    if result:
        print(f"\n✓ Identified as: {result['form_name']}")
        print(f"\n  Extracted Variables:")
        for var_name, var_value in result['variables'].items():
            print(f"    {var_name}: {var_value}")
    else:
        print("\n✗ No matching form found")
    
    print()
    
    # Example 3: Show how to process multiple documents
    print("=" * 60)
    print("Example 3: Batch Processing Concept")
    print("=" * 60)
    
    print("""
The processor can handle batch processing of multiple documents:

1. Load all rules once at the start
2. For each document:
   - Read and extract text using NominalReader
   - Process with NominalProcessor.process_document()
   - Get form type and extracted variables
   - Use variables for file renaming or organization

Example batch workflow:

    processor = NominalProcessor('rules/')
    reader = NominalReader()
    
    for pdf_file in pdf_directory.glob('*.pdf'):
        text = reader.read_pdf(str(pdf_file))
        result = processor.process_document(text)
        
        if result:
            # Rename file based on extracted variables
            form_name = result['variables'].get('FORM_NAME', 'UNKNOWN')
            last_name = result['variables'].get('LAST_NAME', 'UNKNOWN')
            ssn_last_four = result['variables'].get('SSN_LAST_FOUR', 'XXXX')
            
            new_name = f"{form_name}_{last_name}_{ssn_last_four}.pdf"
            # Rename or move file...
    """)


if __name__ == '__main__':
    main()

