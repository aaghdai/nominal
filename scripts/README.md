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
