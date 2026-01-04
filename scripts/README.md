# Scripts

Utility scripts for maintaining the Nominal project.

## update_changelog_stats.sh

Automatically updates the statistics section in `CHANGELOG.md` with current project metrics.

### Usage

```bash
./scripts/update_changelog_stats.sh
```

### What it updates

- **Source code line counts**: Total lines across all Python modules, broken down by component
- **Test code line counts**: Total lines in test files
- **Documentation line counts**: Total lines in markdown documentation files
- **File counts**: Number of files in each category (source, tests, docs, rules, examples, config)
- **Test counts**: Total number of tests (via pytest collection)

### Requirements

- `uv` must be installed and configured
- Project dependencies must be installed (`uv sync`)
- `pytest` must be available for test counting

### When to run

Run this script before making commits that add or modify code, tests, or documentation. This ensures the changelog statistics remain accurate.

### How it works

1. Calculates line counts using `wc -l` on relevant file patterns
2. Counts files using `find` commands
3. Collects test counts using `pytest --collect-only`
4. Uses `awk` to replace the statistics section in `CHANGELOG.md` while preserving the rest of the file

---

## CLI Commands

The following scripts are available as CLI commands via `uv run`:

### nominal-derived

Advanced document processing with orchestrator-level derived variables. This command provides built-in derivation functions for common use cases like extracting first/last names from full names, formatting TINs, and computing composite values.

**Location:** `src/nominal/scripts_derived.py`

**Usage:**
```bash
# Basic usage with default pattern
uv run nominal-derived \
  --input ./test_input \
  --output ./output_results \
  --rules ./rules

# Custom pattern using derived variables
uv run nominal-derived \
  -i ./test_input \
  -o ./output_results \
  -r ./rules \
  --pattern "{YEAR}_{LAST_NAME}_{FIRST_NAME}_{rule_id}"
```

**Built-in Derived Variables:**
- `LAST_NAME` - Extract last name from FULL_NAME
- `FIRST_NAME` - Extract first name from FULL_NAME
- `FULL_TIN` - Format TIN with dashes (XXX-XX-XXXX)
- `NAME_TIN_COMBO` - Combined last name and TIN last 4
- `YEAR` - Document year (extracted or current year)

**Options:**
- `--input, -i` - Input directory containing PDF files
- `--output, -o` - Output directory for renamed files
- `--rules, -r` - Directory containing rule YAML files
- `--pattern, -p` - Filename pattern (default: `{rule_id}_{LAST_NAME}_{TIN_LAST_FOUR}`)
- `--no-ocr` - Disable OCR fallback for image-based PDFs

See the script source code for implementation details and to understand how to create custom derived variables programmatically.
