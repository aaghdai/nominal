# Examples

This directory contains example scripts demonstrating how to use the Nominal tax document processing system.

## Example Scripts

### `example_processor.py`
Demonstrates the core functionality of the Nominal Processor:
- Reading PDF files using `NominalReader`
- Loading and applying rules using `NominalProcessor`
- Extracting variables (global, local, and derived)
- Processing both PDF files and text directly
- Batch processing concepts

**Usage:**
```bash
python examples/example_processor.py
```

### `example_logging.py`
Demonstrates different logging levels and their output:
- INFO level (default): Shows actionable information
- DEBUG level: Shows detailed debugging information
- WARNING level: Shows only warnings and errors
- ERROR level: Shows error conditions

**Usage:**
```bash
python examples/example_logging.py
```

### `example_project_logging.py`
Demonstrates project-level logging configuration:
- Configuring all components at once
- Configuring specific components (processor, reader)
- Component-specific log level control

**Usage:**
```bash
python examples/example_project_logging.py
```

## Running Examples

All examples can be run from the project root directory:

```bash
# From project root
python examples/example_processor.py
python examples/example_logging.py
python examples/example_project_logging.py
```

Or using `uv`:

```bash
uv run python examples/example_processor.py
uv run python examples/example_logging.py
uv run python examples/example_project_logging.py
```

## Requirements

Examples require:
- The `rules/` directory with rule files (W2, 1099-MISC, etc.)
- The `test/fixtures/` directory with sample PDFs (for `example_processor.py`)
- All Nominal dependencies installed

All examples automatically adjust paths to work from the `examples/` directory.

