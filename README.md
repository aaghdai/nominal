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

# Optional: Configure logging level via .env file
cp .env.example .env
# Edit .env to set NOMINAL_LOG_LEVEL (DEBUG, INFO, WARNING, ERROR, CRITICAL)
# Log level is automatically loaded from .env file when package is imported
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
    print(f"Form Type: {result['rule_id']}")
    print(f"Global Variables: {result['global_variables']}")
    print(f"Local Variables: {result['local_variables']}")
```

### Example Output

```
Form Type: W2
Global Variables: {
    'TIN_LAST_FOUR': '6789',
    'FIRST_NAME': 'John',
    'LAST_NAME': 'Smith'
}
Local Variables: {
    'FORM_NAME': 'W2'
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

### 3. Nominal Orchestrator
Orchestrates the complete workflow: reading, processing, and file renaming.

**Features:**
- Batch directory processing
- Pattern-based file renaming
- Variable validation (ensures pattern uses existing variables)
- Orchestrator-level derived variables (e.g., extracting last names)
- Robust error handling and unmatched file tracking

[Learn More](docs/orchestrator.md)

## Rule Files

Rules are organized into two types:

### Global Rules (`rules/global/`)
Extract common variables from all documents (e.g., TIN_LAST_FOUR, names).

### Form Rules (`rules/forms/`)
Classify documents by form type (W2, 1099-DIV, etc.).

Here's an example form rule for W2:

```yaml
form_name: W2
description: IRS Form W-2 - Wage and Tax Statement

criteria:
  - type: regex
    pattern: '(?i)w-?2'
    description: "Document must contain W-2"
  - type: any
    criteria:
      - type: regex
        pattern: '(?i)wage\s+and\s+tax\s+statement'

actions:
  - type: set
    variable: FORM_NAME
    value: "W2"
```

See [rules/README.md](rules/README.md) for complete DSL documentation.

## Project Structure

```
nominal/
├── src/
│   └── nominal/
│       ├── reader/            # PDF reading and OCR package
│       │   ├── __init__.py
│       │   └── reader.py
│       ├── logging/           # Logging configuration package
│       │   ├── __init__.py
│       │   └── config.py
│       ├── processor/         # Rule-based processing package
│       │   ├── __init__.py
│       │   └── processor.py
│       └── rules/             # Rules engine package
│           ├── __init__.py
│           ├── action.py      # Action implementations
│           ├── criterion.py   # Criterion implementations
│           ├── enums.py       # Type enumerations
│           ├── manager.py     # Rules manager
│           ├── parser.py      # YAML parser
│           ├── rule.py        # Rule data structures
│           └── validator.py   # Rule validation
├── rules/                     # Rule definition files
│   ├── global/                # Global extraction rules
│   │   └── person-info.yaml   # Extracts common variables (TIN, names)
│   ├── forms/                 # Form classification rules
│   │   ├── w2.yaml            # W2 form rules
│   │   ├── 1099-div.yaml      # 1099-DIV form rules
│   │   └── 1099-misc.yaml     # 1099-MISC form rules
│   └── README.md              # Rule DSL documentation
├── test/
│   ├── fixtures/              # Test PDF files
│   └── nominal/               # Test files (mirrors src structure)
│       ├── reader/             # Reader tests
│       ├── logging/            # Logging tests
│       ├── processor/         # Processor tests
│       └── rules/              # Rules tests
├── examples/                   # Example scripts
├── docs/                      # Documentation
├── scripts/                   # Utility scripts
├── tools/                     # Development tools
│   └── validate_rules.py      # Rule validation tool
├── .env.example               # Environment variables template
└── PLAN.md                    # Project roadmap
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
uv run python examples/example_processor.py
```

### Running on Test Fixtures

You can run the Nominal CLI on the included test fixtures to see the orchestrator in action:

```bash
# Create an output directory
mkdir -p output_results

# Run the orchestrator
uv run nominal process --input test/fixtures --output output_results --rules rules
```

This will:
1. Scan `test/fixtures/` for PDF files.
2. Apply global rules to extract common variables.
3. Apply form rules to classify each document.
4. Rename and move matched files to `output_results/`.
5. Move unmatched files or those with errors to `output_results/unmatched/` with error logs.

### Updating Changelog Statistics

Before making a commit, update the statistics section in `CHANGELOG.md`:

```bash
# Run the statistics update script
./scripts/update_changelog_stats.sh
```

This script automatically calculates and updates:
- Source code line counts
- Test code line counts
- Documentation line counts
- File counts by category
- Test counts

The script uses `uv` and `pytest` to gather accurate metrics, so ensure dependencies are installed.

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
- python-dotenv (environment configuration)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

See [LICENSE](LICENSE) file for details.

## Acknowledgments

Built with:
- [PyMuPDF](https://pymupdf.readthedocs.io/) for PDF processing
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) for text recognition
- [PyYAML](https://pyyaml.org/) for rule parsing
