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

### Milestone 2: Process a Batch of PDF Files
- **Goal**: Create the `nominal-processor` component to handle batch processing and variable extraction.
- **Key Features**:
    - Support batch input.
    - Handle variable scope:
        - **Document-specific**: Values differ per file (e.g., SSN).
        - **Batch-level**: Values shared across files in the batch.
- **Inputs**:
    1. Description of variables and parsing rules (e.g., Regex).
    2. Scope definitions for variables.
    3. Content of parsed PDFs (from Reader).
- **Output**:
    - Values of document-specific variables for each file.
    - Values of batch-level variables.

**See detailed documentation:**
- Implementation: `src/nominal/processor/` and `src/nominal/rules/` packages
- API Documentation: `docs/processor.md`
- DSL Specification: `rules/README.md`
- Example Usage: `examples/example_processor.py`

### 🔄 Milestone 3: Implement Orchestrator (NEXT)
- **Goal**: Create the `nominal-orchestrator` to orchestrate the workflow and rename files.
- **Status**: 🔄 Planned
- **Functionality**:
    - Accepts a directory path containing PDFs.
    - Runs `nominal-reader` on files.
    - Runs `nominal-processor` to extract data.
    - Renames files based on extracted variables and output format.
    - Writes files to an output path.
- **Error Handling**:
    - If a file cannot be renamed (e.g., matching failed), write an error log to the output path.

## Summary

### What's Working

1. **Nominal Reader** (Milestone 1)
   - Reads PDF files with text extraction
   - Automatic OCR for image-based PDFs
   - Tested with real sample documents

2. **Nominal Processor** (Milestone 2)
   - YAML-based rule DSL for form identification
   - Pattern matching with regex support
   - Variable extraction and transformation
   - Composite criteria (all/any)
   - Batch processing capability
   - 29 tests, all passing

### Next Steps

To complete **Milestone 3 (Orchestrator)**:
1. Create orchestrator module
2. Implement file renaming logic
3. Add batch directory processing
4. Implement error logging
5. Add configuration for output format
6. Create end-to-end tests

### Example Workflow (When Complete)

```bash
# Process a directory of tax documents
nominal process --input ./documents --output ./organized --rules ./rules

# Result:
# documents/scan001.pdf → organized/W2_Smith_6789.pdf
# documents/scan002.pdf → organized/1099-MISC_Johnson_4321.pdf
# documents/scan003.pdf → organized/UNMATCHED_scan003.pdf (with error log)
```
