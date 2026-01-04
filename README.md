# nominal
Because a file by any other name is a headache. Automated document renaming based on internal truth.

## Overview

Nominal is a Python library for processing tax documents. It can read PDF files (including image-based PDFs with OCR), identify document types using configurable rules, and extract relevant information for automated file organization.

## Features

- **PDF Reading**: Extract text from PDF files with automatic OCR fallback for image-based documents
- **Rule-Based Processing**: Define custom rules using a simple YAML-based DSL
- **Form Identification**: Automatically identify tax forms (W2, 1099, etc.)
- **Variable Extraction**: Extract key information like names, SSNs, form types
- **Batch Processing**: Process multiple documents efficiently
- **Extensible**: Easy to add support for new form types

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/nominal.git
cd nominal

# Install dependencies
uv sync
```

### Basic Usage

```python
from nominal.reader import NominalReader
from nominal.processor import NominalProcessor

# Initialize
reader = NominalReader()
processor = NominalProcessor('rules/')

# Process a document
text = reader.read_pdf('tax_document.pdf')
result = processor.process_document(text)

if result:
    print(f"Form Type: {result['form_name']}")
    print(f"Variables: {result['variables']}")
```

### Example Output

```
Form Type: W2
Variables: {
    'FORM_NAME': 'W2',
    'SSN': '123-45-6789',
    'FIRST_NAME': 'John',
    'LAST_NAME': 'Smith',
    'SSN_LAST_FOUR': '6789'
}
```

## Components

### 1. Nominal Reader
Reads PDF files and extracts text content. Automatically uses OCR for image-based PDFs.

**Features:**
- Text extraction from PDF files
- Automatic OCR fallback for scanned documents
- Configurable OCR threshold

[Learn More](docs/reader.md)

### 2. Nominal Processor
Identifies document types and extracts information using rule files.

**Features:**
- YAML-based rule definition (DSL)
- Pattern matching with regex support
- Variable extraction and transformation
- Composite criteria (all/any)

[Learn More](docs/processor.md)

### 3. Nominal Orchestrator *(Coming Soon)*
Orchestrates the complete workflow: reading, processing, and file renaming.

## Rule Files

Rules are defined in YAML format. Here's a simple example for W2 forms:

```yaml
form_name: W2
description: IRS Form W-2 - Wage and Tax Statement

variables:
  global:
    - SSN
    - FIRST_NAME
    - LAST_NAME
    - SSN_LAST_FOUR
  local:
    - FORM_NAME

criteria:
  - type: regex
    pattern: '(?i)w-?2'
    description: "Document must contain W-2"
  
  - type: regex
    pattern: '\b\d{3}-\d{2}-\d{4}\b'
    capture: true
    variable: SSN

actions:
  - type: set
    variable: FORM_NAME
    value: "W2"
  
  - type: derive
    variable: SSN_LAST_FOUR
    from: SSN
    method: slice
    args:
      start: -4
```

See [rules/README.md](rules/README.md) for complete DSL documentation.

## Project Structure

```
nominal/
├── src/
│   └── nominal/
│       ├── reader.py          # PDF reading and OCR
│       └── processor.py       # Rule-based processing
├── rules/
│   ├── w2.yaml               # W2 form rules
│   ├── 1099-misc.yaml        # 1099-MISC form rules
│   └── README.md             # Rule DSL documentation
├── test/
│   ├── fixtures/             # Sample PDFs for testing
│   └── nominal/              # Test files
├── docs/                     # Documentation
├── example_processor.py      # Example usage script
└── PLAN.md                   # Project roadmap
```

## Development

### Running Tests

```bash
# All tests
uv run pytest

# Specific component
uv run pytest test/nominal/test_processor.py -v

# With coverage
uv run pytest --cov=nominal --cov-report=html
```

### Running Examples

```bash
# Run the processor example
uv run python example_processor.py
```

## Roadmap

### ✅ Milestone 1: Implement the Reader
- PDF text extraction
- OCR fallback for image-based PDFs
- Basic error handling

### ✅ Milestone 2: Process a Batch of PDF Files
- YAML-based rule DSL
- Pattern matching and criteria evaluation
- Variable extraction and transformation
- Batch processing support

### 🔄 Milestone 3: Implement Orchestrator *(In Progress)*
- File renaming based on extracted variables
- Batch directory processing
- Error logging
- Output path management

## Requirements

- Python >= 3.13
- PyMuPDF (PDF reading)
- Tesseract OCR (for image-based PDFs)
- PyYAML (rule file parsing)
- Pillow (image processing)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

See [LICENSE](LICENSE) file for details.

## Acknowledgments

Built with:
- [PyMuPDF](https://pymupdf.readthedocs.io/) for PDF processing
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) for text recognition
- [PyYAML](https://pyyaml.org/) for rule parsing
