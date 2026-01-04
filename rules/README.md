# Nominal Rules

This directory contains rule definitions for processing tax documents.

## Directory Structure

```
rules/
├── global/          # Global extraction rules (applied to all documents)
│   └── person-info.yaml
└── forms/           # Form classification rules (one per form type)
    ├── w2.yaml
    ├── 1099-div.yaml
    └── 1099-misc.yaml
```

## Rule Types

### Global Rules (`global/`)

Global rules extract common information from all documents:
- Personal identification (names, TIN)
- Variables that are consistent across multiple documents

Global rules use `rule_name` instead of `form_name` and are applied to every document before classification.

### Form Rules (`forms/`)

Form rules classify documents by form type:
- W-2, 1099-DIV, 1099-MISC, etc.
- Each rule defines criteria for matching a specific form type
- Form rules use `form_name` and return classification results

## Processing Flow

1. **Global Extraction**: All global rules are applied to extract common variables
2. **Classification**: Form rules are applied to classify the document
3. **First Match Wins**: The first form rule that matches determines the document type
4. **Unmatched Logging**: Documents that don't match any form are logged as errors

## Rule File Format

### Global Rule Example

```yaml
rule_name: person-info
description: Extracts taxpayer personal information

criteria:
  - type: regex
    pattern: '.'  # Match any document

actions:
  - type: regex_extract
    variable: TIN_LAST_FOUR
    from_text: true
    pattern: '\b\d{3}-\d{2}-(\d{4})\b'
    group: 1
```

### Form Rule Example

```yaml
form_name: W2
description: IRS Form W-2 - Wage and Tax Statement

criteria:
  - type: regex
    pattern: '(?i)w-?2'
  - type: any
    criteria:
      - type: regex
        pattern: '(?i)wage\s+and\s+tax\s+statement'

actions:
  - type: set
    variable: FORM_NAME
    value: "W2"
```

## Validation

Run the validation tool to check all rules:

```bash
python tools/validate_rules.py
```

## Adding New Rules

1. **Form Rule**: Add a new YAML file in `forms/` with `form_name`, `criteria`, and `actions`
2. **Global Rule**: Add a new YAML file in `global/` with `rule_name`, `criteria`, and `actions`
3. Run validation to ensure the rule is correct
4. Run tests to verify behavior
