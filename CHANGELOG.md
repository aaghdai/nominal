# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Project-level logging system** (`src/nominal/logging_config.py`)
  - Colored logging output (DEBUG, INFO, WARNING, ERROR, CRITICAL)
  - Configurable log levels per component (reader, processor)
  - `configure_logging()` function for centralized configuration
  - Comprehensive logging throughout all components
  - Logging documentation in `docs/logging/README.md`

- **Code quality tools**
  - Ruff linter and formatter integration
  - Pre-commit hooks for automatic code formatting
  - Git hooks that run on every commit
  - Automated import sorting and code style enforcement

- **Examples directory** (`examples/`)
  - `example_processor.py`: Core processor usage examples
  - `example_logging.py`: Logging level demonstrations
  - `example_project_logging.py`: Project-level logging configuration
  - `README.md`: Examples documentation

### Changed
- **Processor refactoring**
  - Split `processor.py` into modular package structure
  - Separated enums, base classes, implementations, parser, and evaluator
  - Improved code organization and maintainability

- **Project organization**
  - Moved example scripts to dedicated `examples/` directory
  - Moved logging documentation to `docs/logging/` directory
  - Updated all path references to work from new locations

- **Test improvements**
  - Removed unnecessary `sys.path` manipulation from test files
  - Removed `# noqa: E402` tags (no longer needed)
  - Cleaner test code following best practices
  - All tests work with package installed in editable mode

- **Code quality**
  - Fixed all linting issues (line length, import ordering, unused imports)
  - Enforced 100-character line length limit
  - Consistent code formatting across entire codebase
  - All code passes ruff checks

### Technical Details
- Ruff configuration in `pyproject.toml`
- Pre-commit hooks configured in `.pre-commit-config.yaml`
- Automatic code formatting on git commit
- Project-level logging configuration

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
- **Source Code**: 1266 lines across all modules
  - Reader module: ~119 lines
  - Processor package: ~937 lines (8 modules: enums, variable, criterion, action, rule, parser, processor, logging_config)
  - Main package: ~210 lines
- **Test Code**: 616 lines across all test files
- **Documentation**: 1280 lines across multiple files
  - Architecture and design docs
  - API reference and usage guides
  - Logging documentation
  - Examples and tutorials

### Test Coverage
- **Unit Tests**: 24 tests
- **Integration Tests**: 5 tests
- **Total**: 29 tests
- **Pass Rate**: 100%

### Files Created/Modified
- **Core modules**: 12 Python files
  - Reader: 1 file
  - Processor package: 8 files (enums, variable, criterion, action, rule, parser, processor, logging_config)
  - Package init: 2 files
  - Main: 1 file
- **Rule files**: 2 YAML files (w2.yaml, 1099-misc.yaml)
- **Test files**: 6 test modules
- **Documentation files**: 4 markdown files
  - Architecture documentation
  - Processor documentation
  - Logging documentation
  - Milestone summaries
- **Example files**: 3 Python scripts + README
- **Configuration files**: 3 files (pyproject.toml, .pre-commit-config.yaml, .gitignore)
- **Total**: 31+ files

### Features Implemented
- PDF reading: ✅
- OCR support: ✅
- Rule parsing: ✅
- Pattern matching: ✅
- Variable extraction: ✅
- Variable derivation: ✅
- Batch processing: ✅
- Logging system: ✅
- Code quality tools: ✅
- Comprehensive testing: ✅
- Full documentation: ✅

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

[Unreleased]: https://github.com/yourusername/nominal/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/yourusername/nominal/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/yourusername/nominal/releases/tag/v0.1.0
