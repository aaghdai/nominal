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

#### Command Line Interface

Process documents with the simple CLI:

```bash
# Basic processing
uv run nominal process \
  --input ./test_input \
  --output ./output_results \
  --rules ./rules \
  --pattern "{rule_id}_{LAST_NAME}_{TIN_LAST_FOUR}"
```

#### Python API

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

### Advanced: Derived Variables

For advanced use cases, you can compute additional variables from extracted data using **orchestrator-level derived variables**. This is useful for:
- Extracting parts of values (e.g., last name from full name)
- Computing composite values
- Applying custom formatting or business logic

#### Using the Derived Variables CLI

```bash
# Process with built-in derived variables
uv run nominal-derived \
  --input ./test_input \
  --output ./output_results \
  --rules ./rules \
  --pattern "{YEAR}_{LAST_NAME}_{FIRST_NAME}_{rule_id}"
```

**Built-in derived variables:**
- `LAST_NAME` - Extract last name from FULL_NAME
- `FIRST_NAME` - Extract first name from FULL_NAME
- `FULL_TIN` - Format TIN with dashes (XXX-XX-XXXX)
- `NAME_TIN_COMBO` - Combined last name and TIN last 4
- `YEAR` - Document year

#### Programmatic Usage with Custom Derivations

```python
from nominal.orchestrator import NominalOrchestrator

# Define custom derivation functions
def extract_last_name(all_vars):
    """Extract last name from FULL_NAME."""
    full_name = all_vars.get("FULL_NAME", "")
    return full_name.split()[-1] if full_name else "UNKNOWN"

def format_year(all_vars):
    """Extract and format tax year."""
    return all_vars.get("TAX_YEAR", "2024")

# Initialize orchestrator with derived variables
orchestrator = NominalOrchestrator(
    rules_dir="rules/",
    derived_variables={
        "LAST_NAME": extract_last_name,
        "TAX_YEAR": format_year,
    }
)

# Process directory with derived variables in filename pattern
stats = orchestrator.process_directory(
    input_dir="input/",
    output_dir="output/",
    filename_pattern="{TAX_YEAR}_{rule_id}_{LAST_NAME}_{TIN_LAST_FOUR}"
)
```

See `src/nominal/scripts_derived.py` for the complete implementation with detailed documentation.

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
│       ├── __init__.py
│       ├── main.py            # CLI entry point
│       ├── scripts_derived.py # Advanced CLI with derived variables
│       ├── reader/            # PDF reading and OCR package
│       │   ├── __init__.py
│       │   └── reader.py
│       ├── logging/           # Logging configuration package
│       │   ├── __init__.py
│       │   └── config.py
│       ├── processor/         # Rule-based processing package
│       │   ├── __init__.py
│       │   └── processor.py
│       ├── orchestrator/      # Workflow orchestration package
│       │   ├── __init__.py
│       │   └── orchestrator.py
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
│   │   ├── Sample-W2.pdf
│   │   └── Sample-1099-image.pdf
│   └── nominal/               # Test files (mirrors src structure)
│       ├── reader/            # Reader tests
│       ├── logging/           # Logging tests
│       ├── processor/         # Processor tests
│       ├── orchestrator/      # Orchestrator tests
│       └── rules/             # Rules tests
├── examples/                  # Example scripts
│   ├── example_processor.py
│   ├── example_logging.py
│   └── README.md
├── docs/                      # Documentation
│   ├── processor.md
│   ├── architecture.md
│   └── logging/
├── scripts/                   # Utility scripts
│   ├── update_changelog_stats.sh
│   └── README.md
├── tools/                     # Development tools
│   ├── validate_rules.py      # Rule validation tool
│   └── README.md
├── test_input/                # Sample input files for testing
├── .env.example               # Environment variables template
├── CHANGELOG.md               # Project changelog
├── PLAN.md                    # Project roadmap
├── pyproject.toml             # Project configuration
└── uv.lock                    # Dependency lock file
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

### ✅ Milestone 1: Implement the Reader (COMPLETED)
- ✅ PDF text extraction
- ✅ OCR fallback for image-based PDFs
- ✅ Configurable OCR threshold
- ✅ Basic error handling

### ✅ Milestone 2: Process a Batch of PDF Files (COMPLETED)
- ✅ YAML-based rule DSL
- ✅ Pattern matching and criteria evaluation
- ✅ Variable extraction and transformation
- ✅ Batch processing support
- ✅ Global and local variable scoping

### ✅ Milestone 3: Implement Orchestrator (COMPLETED)
- ✅ File renaming based on extracted variables
- ✅ Batch directory processing
- ✅ Error logging and unmatched file tracking
- ✅ Output path management
- ✅ CLI interface (`nominal` command)

### ✅ Milestone 4: Advanced Features (COMPLETED)
- ✅ Orchestrator-level derived variables
- ✅ Pattern validation against declared variables
- ✅ Advanced CLI (`nominal-derived` command)
- ✅ Built-in derivation functions (LAST_NAME, FIRST_NAME, etc.)

**All core features are now complete!** The system can read PDFs, identify forms, extract variables, compute derived values, and automatically rename files. See [PLAN.md](PLAN.md) for detailed implementation notes.

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
