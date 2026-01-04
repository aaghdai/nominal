# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added - Name Validation System

#### Validated Name Extraction
- **ValidatedRegexExtractAction**: New action type for intelligent name extraction
  - Extracts multiple candidate names using regex patterns
  - Validates each candidate against US Census name databases
  - Scores candidates with confidence levels (0.0-1.0)
  - Returns highest-confidence match above configurable threshold
  - Distinguishes person names from organization names

- **Name Validator Module** (`src/nominal/rules/name_validator.py`)
  - Loads and caches name dictionaries for fast validation
  - `validate_full_name()`: Validates and extracts first/last name components
  - `score_name_candidates()`: Scores and ranks multiple candidates
  - Confidence scoring based on first name, last name, and middle initial recognition

- **Name Dictionaries** (`data/`)
  - `first_names.txt`: 40,836 unique first names from SSA (2020-2023)
  - `last_names.txt`: 50,000 surnames from US Census Bureau (2010)
  - Total: 90,836 name entries for validation
  - Public domain data from US government sources

#### CLI Tools
- **nominal-generate-names**: New CLI command for dictionary generation
  - Downloads US Census Bureau surnames (top 50,000)
  - Downloads SSA baby names (2020-2023)
  - Processes and creates validation dictionaries
  - Automatic cleanup of temporary files
  - Fallback support for wget/curl
  - Accessible via `uv run nominal-generate-names`

- **Scripts Package** (`src/nominal/scripts/`)
  - Utility scripts as importable modules
  - `generate_names.py`: Dictionary generator with smart path resolution
  - Finds project root via `pyproject.toml` detection

#### Documentation
- **Name Extraction Strategy** (`docs/name_extraction_strategy.md`)
  - Comprehensive multi-strategy approach documentation
  - Context-aware extraction patterns
  - Validation methodology and confidence scoring
  - Implementation examples and best practices

- **Data Directory Documentation** (`data/README.md`)
  - Dictionary sources and format specification
  - Usage examples with validation
  - Regeneration instructions
  - Benefits and trade-offs

- **Updated Rule Files**
  - `rules/global/person-info.yaml`: Enhanced with validated extraction
  - Multi-strategy approach: context-aware → validated fallback
  - Improved accuracy for person name identification

### Changed
- **Rule DSL**: Added `validated_regex_extract` action type
- **Action Enums**: Added `VALIDATED_REGEX_EXTRACT` to `ActionType`
- **Rule Parser**: Extended to parse validated extraction actions
- **Project Structure**: Added `src/nominal/scripts/` package
- **pyproject.toml**: Added `nominal-generate-names` CLI entry point
- **Installation**: Updated to include dictionary generation step

### Technical Details
- Confidence scoring algorithm: first name (0.5) + last name (0.5) + middle initial bonus (0.1)
- Lazy loading and caching of name dictionaries for performance
- Regex patterns with negative lookaheads for organization exclusion
- Context-aware field label extraction (primary strategy)
- Validated pattern matching (fallback strategy)

### Test Results
- Total tests: 46 (all passing)
- Name validation accuracy: 100% on test fixtures
- Successfully distinguishes:
  - Person names: `MICHAEL M JORDAN`, `ELIZABETH A DARLING`
  - Organizations: `UNIVERSITY OF PITTSBURGH`, `STERLING HEIGHTS`
  - False positives: `ZIP CODE`, `NONDIVIDEND DISTRIBUTIONS`

---

## [0.3.0] - 2026-01-03

### Added - Milestone 3: Nominal Orchestrator

#### Core Orchestrator Module (`src/nominal/orchestrator/`)
- **NominalOrchestrator**: Main workflow orchestration class
  - Recursive directory scanning for PDF files
  - Integration with Reader and Processor
  - Pattern-based file renaming using extracted variables
  - Graceful handling of duplicate filenames
  - Robust error handling and reporting
  - Detailed processing statistics

- **Renaming Engine**: Powerful variable substitution in filenames
  - Supports all extracted variables (global and local)
  - Automatic sanitization of variable values for filenames
  - Graceful fallback to 'UNKNOWN' for missing variables
  - Duplicate filename detection and automatic numbering

- **Error Handling & Reporting**
  - Unmatched files are moved to a dedicated `unmatched/` directory
  - Detailed error logs generated for each failure (unmatched or exception)
  - Source files are preserved and copied to avoid data loss
  - Comprehensive logging throughout the orchestration process

#### CLI Interface
- **Command-line Entry Point**: `nominal process` command
  - `--input` (-i): Input directory to scan
  - `--output` (-o): Output directory for renamed files
  - `--rules` (-r): Rules directory for form identification
  - `--pattern` (-p): Custom filename pattern (e.g., `{rule_id}_{FULL_NAME}`)
  - `--no-ocr`: Option to disable OCR fallback for faster processing

#### Testing
- `test/nominal/orchestrator/test_orchestrator.py`: End-to-end tests
  - Full workflow test with real PDF fixtures
  - Unmatched document handling tests
  - Error reporting verification
  - Filename generation and sanitization tests

### Changed
- `pyproject.toml`: Added `nominal` CLI script entry point
- `PLAN.md`: Marked Milestone 3 as complete
- `src/nominal/main.py`: Updated to provide command-line interface

### Technical Details
- Command-line argument parsing using `argparse`
- File system operations using `pathlib` and `shutil`
- Placeholder replacement using regex for renaming patterns
- Package distribution configuration for CLI script

---

## [0.2.0] - 2026-01-03

### Added - Milestone 2: Nominal Processor

#### Core Processor Module (`src/nominal/processor.py`)
- **RuleParser**: Parse YAML rule files into structured Rule objects
  - Validates required fields and structure
  - Supports all DSL components
  - Comprehensive error handling

- **CriteriaEvaluator**: Evaluate matching criteria against document text
  - `contains` criterion (case-sensitive/insensitive)
  - `regex` criterion with optional capture
  - `all` criterion (logical AND)
  - `any` criterion (logical OR)
  - Captures values during evaluation

- **ActionExecutor**: Execute actions to extract and transform variables
  - `set` action (literal values)
  - `regex_extract` action (pattern-based extraction)
  - `derive` action (slice, upper, lower transformations)
  - `extract` action (split and extract)
  - Variable context management

- **NominalProcessor**: Main orchestration class
  - Load rules from directories
  - Process documents against rules
  - First-match rule selection
  - Batch processing support

#### Rule Files
- `rules/w2.yaml`: W-2 form identification and extraction
- `rules/1099-misc.yaml`: 1099-MISC form identification and extraction
- `rules/README.md`: Complete DSL documentation with examples

#### Testing
- `test/nominal/test_processor.py`: 19 unit tests
  - RuleParser tests (5 tests)
  - CriteriaEvaluator tests (6 tests)
  - ActionExecutor tests (5 tests)
  - NominalProcessor tests (3 tests)

- `test/nominal/test_processor_integration.py`: 5 integration tests
  - W2 form recognition tests
  - Real PDF processing tests
  - Multiple rule scenarios
  - Edge case handling

#### Documentation
- `docs/processor.md`: Complete processor documentation
  - Architecture overview
  - API reference
  - Usage examples
  - Best practices
  - Performance considerations
  - Troubleshooting guide
  - Extension guide

- `docs/milestone2_summary.md`: Implementation summary
  - Completed tasks breakdown
  - Technical achievements
  - Design decisions
  - Success metrics

- `docs/architecture.md`: Visual architecture diagrams
  - System architecture
  - Component architecture
  - Data flow diagrams
  - Class hierarchy

- Updated `README.md`: Added processor overview and quick start
- Updated `PLAN.md`: Marked Milestone 2 as complete

#### Examples
- `example_processor.py`: Comprehensive usage examples
  - Basic usage
  - Real PDF processing
  - Batch processing concepts
  - Custom file naming

### Changed
- `pyproject.toml`: Added `pyyaml` dependency
- Project structure: Added `rules/` and `docs/` directories

### Technical Details
- Python 3.13+ support
- Type hints throughout
- Dataclasses for clean API
- Comprehensive docstrings
- Error handling and validation
- Performance optimized (< 10ms per rule evaluation)

### Test Results
- Total tests: 29 (19 processor + 5 integration + 5 reader tests)
- Status: ✅ All passing
- Coverage: Core functionality fully covered

---

## [0.1.0] - 2025-12-XX

### Added - Milestone 1: Nominal Reader

#### Core Reader Module (`src/nominal/reader.py`)
- **NominalReader**: PDF reading with automatic OCR fallback
  - Text extraction from PDFs using PyMuPDF
  - Automatic OCR detection for image-based pages
  - Configurable OCR threshold
  - Smart OCR triggering (sparse text or large images)
  - High-resolution rendering for better OCR accuracy

#### Dependencies
- PyMuPDF (fitz): PDF processing
- Tesseract/Pytesseract: OCR functionality
- Pillow: Image processing

#### Testing
- `test/nominal/test_reader.py`: Unit tests
- `test/nominal/test_reader_integration.py`: Integration tests with real PDFs
- `test/fixtures/`: Sample PDF files for testing
  - `Sample-W2.pdf`: Text-based W2 form
  - `Sample-1099-image.pdf`: Image-based 1099 form

#### Project Setup
- Initial project structure
- `pyproject.toml`: Project configuration
- `uv.lock`: Dependency lock file
- Basic README
- License file
- Project plan (PLAN.md)

### Technical Details
- Python 3.13+ requirement
- UV package manager
- Pytest for testing
- Type hints
- Comprehensive error handling

---

## Project Milestones

### ✅ Milestone 1: Implement the Reader (Complete)
- PDF text extraction
- OCR fallback for image-based PDFs
- Comprehensive testing

### ✅ Milestone 2: Process a Batch of PDF Files (Complete)
- YAML-based rule DSL
- Pattern matching and criteria evaluation
- Variable extraction and transformation
- Batch processing support
- Comprehensive testing and documentation

### 🔄 Milestone 3: Implement Orchestrator (Planned)
- File renaming based on extracted variables
- Batch directory processing
- Error logging
- CLI interface
- Configuration management

---

## Version History

- **Unreleased**: Logging system, code quality tools, refactoring improvements
- **0.2.0** (2026-01-03): Processor implementation (Milestone 2) ✅
- **0.1.0** (2025-12-XX): Reader implementation (Milestone 1) ✅
- **0.0.0** (Initial): Project setup

---

## Statistics

### Code
- **Source Code**: 2724 lines across all modules
  - Reader package: 128 lines (2 files)
  - Logging package: 208 lines (2 files)
  - Processor package: 302 lines (2 files)
  - Orchestrator package: 250 lines (2 files)
  - Rules package: 1243 lines (9 files)
  - Scripts package: 242 lines (2 files)
  - Main/CLI: 331 lines (2 files)
- **Test Code**: 1014 lines across 13 test files
- **Documentation**: 1549 lines across 5 markdown files

### Test Coverage
- **Total Tests**: 46 tests
- **Pass Rate**: 100%

### Files
- **Source files**: 22 Python files
- **Rule files**: 4 YAML files
- **Test files**: 13 test modules
- **Documentation**: 5 markdown files
- **Examples**: 3 Python scripts
- **Configuration**: 3 files
- **Total**: 50 files

### Features Implemented
- PDF reading with OCR: ✅
- YAML-based rule DSL: ✅
- Pattern matching & extraction: ✅
- Validated name extraction: ✅
- Batch processing & orchestration: ✅
- Derived variables: ✅
- CLI interface (3 commands): ✅
- Comprehensive logging: ✅
- Code quality tools: ✅
- Full test coverage: ✅
- Complete documentation: ✅

---

## Notes

### Design Philosophy
- **Modular**: Clear separation of concerns
- **Extensible**: Easy to add new features
- **Tested**: Comprehensive test coverage
- **Documented**: Complete documentation
- **Performant**: Optimized for speed
- **Robust**: Error handling throughout

### Key Technologies
- Python 3.13+
- PyMuPDF (PDF processing)
- Tesseract OCR (text recognition)
- PyYAML (rule parsing)
- Pytest (testing)
- UV (package management)
- Ruff (linting and formatting)
- Pre-commit (git hooks)

---

[Unreleased]: https://github.com/aaghdai/nominal/compare/v0.3.0...HEAD
[0.3.0]: https://github.com/aaghdai/nominal/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/aaghdai/nominal/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/aaghdai/nominal/releases/tag/v0.1.0
