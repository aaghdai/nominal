# Project Plan: Tax Document Processor

## Architecture

The project consists of three main subprocessors:

### 1. Nominal Reader (`nominal-reader`)
Responsible for reading input files and extracting text content.
- **Input**: PDF files or Images.
- **Functionality**:
    - Reads PDF files and parses their text content.
    - If the input is an image (or image-based PDF), uses an OCR library to parse the content.
- **Output**: Raw text content of the document.

### 2. Nominal Processor (`nominal-processor`)
Analyzes the text content to identify the document type and extract relevant information based on "processor rules".
- **Rules Example**:
    - File contains a form number (e.g., "W2", "1099").
    - File contains a First Name and Last Name.
    - File contains an SSN in `XXX-XX-XXXX` format.
- **Functionality**:
    - Matches files against defined rules.
    - Extracts information into variables:
        - `$FORM_NAME`
        - `$FIRST_NAME`
        - `$LAST_NAME`
        - `$SSN`
        - `$SSN_LAST_FOUR`

### 3. Nominal Orchestrator (`nominal-orchestrator`)
Renames or labels the file based on a specified format and the variables extracted by the processor.
- **Input**: Original file and extracted variables.
- **Functionality**:
    - Generates a new filename based on a labeling rule.
- **Example Rule**: `{$FORM_NAME}_{$LAST_NAME}_{$SSN_LAST_FOUR}`

## Milestones

### ✅ Milestone 1: Implement the Reader (COMPLETED)
- **Goal**: Create the `nominal-reader` component.
- **Status**: ✅ Complete
- **Implementation**:
    - ✅ Selected PyMuPDF for PDF parsing
    - ✅ Selected Tesseract/Pytesseract for OCR
    - ✅ Implemented PDF text extraction
    - ✅ Implemented OCR fallback for image-based PDFs
    - ✅ Added configurable OCR threshold
    - ✅ Created comprehensive tests
- **Location**: `src/nominal/reader/` package

### ✅ Milestone 2: Process a Batch of PDF Files (COMPLETED)
- **Goal**: Create the `nominal-processor` component to handle batch processing and variable extraction.
- **Status**: ✅ Complete
- **Implementation**:
    - ✅ **Phase 1 - Rule Parser**: Implemented YAML rule file parser with validation
    - ✅ **Phase 2 - Criteria Evaluator**: Implemented matching engine with support for:
        - `contains` (case-sensitive/insensitive)
        - `regex` (with optional capture)
        - `all` and `any` composite criteria
    - ✅ **Phase 3 - Action Executor**: Implemented action engine with support for:
        - `set` - literal values
        - `regex_extract` - extract from text
        - `derive` - transform variables (slice, upper, lower)
        - `extract` - split and extract from variables
    - ✅ **Phase 4 - Batch Processor**: Implemented multi-document processing with rule matching
    - ✅ Created comprehensive unit and integration tests (29 tests, all passing)
    - ✅ Created example rule files (W2, 1099-MISC)
    - ✅ Created documentation and examples
- **Location**:
    - Code: `src/nominal/processor/` and `src/nominal/rules/` packages
    - Rules: `rules/` directory
    - Tests: `test/nominal/processor/` and `test/nominal/rules/` directories
    - Docs: `docs/processor.md`, `rules/README.md`
    - Examples: `examples/` directory

**Key Features Implemented:**
- ✅ Support batch input
- ✅ Handle variable scope (global/local)
- ✅ YAML-based DSL for rule definition
- ✅ Pattern matching with regex
- ✅ Variable extraction and transformation
- ✅ Composite criteria support
- ✅ First-match rule selection
- ✅ Comprehensive error handling

### ✅ Milestone 3: Implement Orchestrator (COMPLETED)
- **Goal**: Create the `nominal-orchestrator` to orchestrate the workflow and rename files.
- **Status**: ✅ Complete
- **Implementation**:
    - ✅ **Phase 1 - File Renaming Engine**: Implemented pattern-based renaming using extracted variables
    - ✅ **Phase 2 - Batch Directory Processor**: Implemented recursive directory scanning and processing
    - ✅ **Phase 3 - Workflow Orchestration**: Integrated Reader, Processor, and Renamer
    - ✅ **Phase 4 - Error Handling & Logging**: Implemented unmatched file reporting and error logs
    - ✅ **Phase 5 - CLI Interface**: Created a command-line interface for the orchestrator
- **Functionality**:
    - Accepts a directory path containing PDFs.
    - Runs `nominal-reader` on files.
    - Runs `nominal-processor` to extract data.
    - Renames files based on extracted variables and output format.
    - Writes files to an output path.
- **Error Handling**:
    - If a file cannot be renamed (e.g., matching failed), write an error log to the output path.
- **Location**: `src/nominal/orchestrator/` package
- **CLI**: `nominal` command for basic processing

### ✅ Milestone 4: Advanced Features (COMPLETED)
- **Goal**: Add advanced capabilities for complex use cases
- **Status**: ✅ Complete
- **Implementation**:
    - ✅ **Orchestrator-Level Derived Variables**: Implemented programmatic variable derivation
    - ✅ **Pattern Validation**: Validates filename patterns against declared variables
    - ✅ **CLI Command for Derived Variables**: Created `nominal-derived` command with built-in derivation functions
    - ✅ **Comprehensive Documentation**: Added examples and usage guides
- **Built-in Derived Variables**:
    - `LAST_NAME` - Extract last name from FULL_NAME
    - `FIRST_NAME` - Extract first name from FULL_NAME
    - `FULL_TIN` - Format TIN with dashes (XXX-XX-XXXX)
    - `NAME_TIN_COMBO` - Combined last name and TIN last 4
    - `YEAR` - Document year
- **Location**:
    - Code: `src/nominal/orchestrator/orchestrator.py`
    - CLI: `src/nominal/scripts_derived.py`
    - Documentation: `README.md`, `scripts/README.md`

## Summary

### ✅ All Core Features Complete

**1. Nominal Reader** (Milestone 1)
   - ✅ Reads PDF files with text extraction
   - ✅ Automatic OCR for image-based PDFs
   - ✅ Configurable OCR threshold
   - ✅ Tested with real sample documents

**2. Nominal Processor** (Milestone 2)
   - ✅ YAML-based rule DSL for form identification
   - ✅ Pattern matching with regex support
   - ✅ Variable extraction and transformation
   - ✅ Composite criteria (all/any)
   - ✅ Batch processing capability
   - ✅ Global and local variable scoping
   - ✅ 46 tests, all passing

**3. Nominal Orchestrator** (Milestone 3)
   - ✅ End-to-end workflow orchestration
   - ✅ Pattern-based file renaming
   - ✅ Batch directory processing
   - ✅ Error handling and unmatched file tracking
   - ✅ CLI interface (`nominal` command)
   - ✅ Integration tests

**4. Advanced Features** (Milestone 4)
   - ✅ Orchestrator-level derived variables
   - ✅ Pattern validation against declared variables
   - ✅ Advanced CLI (`nominal-derived` command)
   - ✅ Comprehensive documentation and examples

### Current Capabilities

The system can now:
- ✅ Read PDFs (including image-based with OCR)
- ✅ Identify document types using configurable rules
- ✅ Extract variables from documents (names, SSNs, form types)
- ✅ Process batches of documents
- ✅ Rename files based on extracted variables
- ✅ Handle unmatched documents gracefully
- ✅ Compute derived variables programmatically
- ✅ Validate filename patterns
- ✅ Run via simple or advanced CLI

### Example Workflows

**Basic Processing:**
```bash
# Process a directory of tax documents
uv run nominal process \
  --input ./test_input \
  --output ./output_results \
  --rules ./rules \
  --pattern "{rule_id}_{LAST_NAME}_{TIN_LAST_FOUR}"

# Result:
# test_input/2024 - Amplitude - Form W2.pdf → output_results/W2_UNKNOWN_5149.pdf
# test_input/2024 - Chase - 1099INT.pdf → output_results/unmatched/ (no matching rule)
```

**Advanced Processing with Derived Variables:**
```bash
# Use built-in derived variables for more sophisticated patterns
uv run nominal-derived \
  --input ./test_input \
  --output ./output_results \
  --rules ./rules \
  --pattern "{YEAR}_{LAST_NAME}_{FIRST_NAME}_{rule_id}"

# Result: Uses derived YEAR, LAST_NAME, FIRST_NAME variables
```

**Programmatic API:**
```python
from nominal.orchestrator import NominalOrchestrator

# Define custom derived variable
def extract_year(all_vars):
    return all_vars.get("TAX_YEAR", "2024")

# Create orchestrator with custom derivations
orchestrator = NominalOrchestrator(
    rules_dir="rules/",
    derived_variables={"YEAR": extract_year}
)

# Process with custom variables in pattern
stats = orchestrator.process_directory(
    input_dir="input/",
    output_dir="output/",
    filename_pattern="{YEAR}_{rule_id}_{LAST_NAME}"
)
```

### Future Enhancements (Optional)

Potential areas for expansion:
- 📋 Support for additional document types (1099-INT, 1040, etc.)
- 📋 Machine learning-based form classification
- 📋 GUI interface for rule creation
- 📋 Cloud storage integration
- 📋 Batch statistics and reporting dashboard
- 📋 Support for more file formats (DOCX, images, etc.)
