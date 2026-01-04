# Tools Directory

This directory contains utility scripts for the Nominal project.

## validate_rules.py

Validates rule files to ensure they conform to the expected schema and structure.

### Usage

```bash
# Validate all rules in a directory
uv run python tools/validate_rules.py rules/

# Validate a single rule file
uv run python tools/validate_rules.py rules/ --file rules/w2.yaml

# Specify a custom global variables schema
uv run python tools/validate_rules.py rules/ --schema path/to/schema.yaml
```

### Features

- Validates YAML syntax
- Checks required fields (form_name, variables, criteria, actions)
- Validates global variables against schema
- Checks variable usage in actions
- Validates criteria and actions structure
- Reports errors and warnings

### Integration

The processor automatically validates rules before loading them when `validate=True` is set (default). Validation can be disabled by passing `validate=False` to `load_rules()`.
