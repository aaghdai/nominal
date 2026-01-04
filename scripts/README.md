# Scripts

Utility scripts for maintaining the Nominal project.

## generate_name_dictionaries.py

Generates name validation dictionaries from US Census and SSA data sources.

### Usage

```bash
# From project root
python scripts/generate_name_dictionaries.py

# Or using uv
uv run python scripts/generate_name_dictionaries.py
```

### What it does

1. **Downloads US Census Bureau surnames** (2010)
   - URL: https://www2.census.gov/topics/genealogy/2010surnames/names.zip
   - Extracts top 50,000 surnames
   - Creates `data/last_names.txt`

2. **Downloads SSA baby names** (2020-2023)
   - URL: https://www.ssa.gov/oact/babynames/names.zip
   - Processes 4 years of data
   - Extracts ~40,836 unique first names
   - Creates `data/first_names.txt`

3. **Cleans up automatically**
   - Uses temporary directory for downloads
   - Removes intermediate files

### Requirements

- `wget` or `curl` must be installed
- Python 3.8+ with standard library (no extra dependencies)

### When to run

- Initial project setup (if name dictionaries are missing)
- To update dictionaries with newer data sources
- After modifying the extraction logic

### Output

```
data/
├── first_names.txt    # ~40,836 names, ~287 KB
└── last_names.txt     # 50,000 surnames, ~374 KB
```

These files enable the `validated_regex_extract` action type to distinguish person names from organization names with high accuracy.

---

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
