# Nominal Processor Rules

This directory contains rule files that define how different tax forms should be identified and processed.

## Rule File Format

Rule files are written in YAML and define the matching criteria and extraction logic for a specific form type.

### Basic Structure

```yaml
form_name: <FORM_NAME>
description: <DESCRIPTION>

variables:
  global:
    - VAR1
    - VAR2
  local:
    - VAR3

criteria:
  - type: <CRITERION_TYPE>
    # ... criterion-specific fields

actions:
  - type: <ACTION_TYPE>
    # ... action-specific fields
```

## Variables

Variables are the values that will be extracted from documents.

- **global**: Variables that are available globally (e.g., across batches)
- **local**: Variables specific to this form/document

Example:
```yaml
variables:
  global:
    - FIRST_NAME
    - LAST_NAME
    - SSN
  local:
    - FORM_NAME
```

## Criteria

Criteria define the conditions that must be met for a document to match this form type.

### Contains Criterion

Checks if the document contains specific text.

```yaml
- type: contains
  value: "form w-2"
  case_sensitive: false
  description: "Document must contain 'form w-2'"
```

Fields:
- `value`: The text to search for
- `case_sensitive`: Whether the search is case-sensitive (default: true)
- `description`: Optional description of the criterion

### Regex Criterion

Matches text using a regular expression pattern.

```yaml
- type: regex
  pattern: '\b\d{3}-\d{2}-\d{4}\b'
  capture: true
  variable: SSN
  description: "Social Security Number in XXX-XX-XXXX format"
```

Fields:
- `pattern`: The regular expression pattern
- `capture`: If true, captures the matched text (default: false)
- `variable`: Variable name to store the captured value
- `description`: Optional description of the criterion

### Composite Criteria

You can combine multiple criteria using `all` or `any`:

```yaml
- type: all
  criteria:
    - type: contains
      value: "form"
    - type: contains
      value: "w-2"
```

```yaml
- type: any
  criteria:
    - type: contains
      value: "w-2"
    - type: contains
      value: "w2"
```

## Actions

Actions are executed when all criteria match. They extract and transform variables.

### Set Action

Sets a variable to a literal value.

```yaml
- type: set
  variable: FORM_NAME
  value: "W2"
```

### Regex Extract Action

Extracts a value from the document text using regex.

```yaml
- type: regex_extract
  variable: FIRST_NAME
  from_text: true
  pattern: 'Name:\s+(\w+)\s+(\w+)'
  group: 1
```

Fields:
- `variable`: The variable to store the extracted value
- `from_text`: If true, extracts from the document text
- `pattern`: The regex pattern with capture groups
- `group`: Which capture group to use (0 = full match, 1+ = capture groups)

### Derive Action

Derives a value from another variable.

```yaml
- type: derive
  variable: SSN_LAST_FOUR
  from: SSN
  method: slice
  args:
    start: -4
```

Methods:
- `slice`: Extract a substring
  - `start`: Starting index (negative for counting from end)
  - `end`: Ending index (optional)
- `upper`: Convert to uppercase
- `lower`: Convert to lowercase

### Extract Action

Extracts a value from another variable using various methods.

```yaml
- type: extract
  variable: FIRST_NAME
  from: FULL_NAME
  method: split
  args:
    pattern: '\s+'
    index: 0
```

Methods:
- `split`: Split the source value and take a specific part
  - `pattern`: The regex pattern to split on
  - `index`: Which part to take (0-based)

## Complete Example: W2 Form

```yaml
form_name: W2
description: IRS Form W-2 - Wage and Tax Statement

variables:
  global:
    - FIRST_NAME
    - LAST_NAME
    - SSN
    - SSN_LAST_FOUR
  local:
    - FORM_NAME

criteria:
  - type: contains
    value: "form w-2"
    case_sensitive: false
    description: "Document must contain 'form w-2'"

  - type: regex
    pattern: '\b\d{3}-\d{2}-\d{4}\b'
    capture: true
    variable: SSN
    description: "Social Security Number in XXX-XX-XXXX format"

actions:
  - type: set
    variable: FORM_NAME
    value: "W2"

  - type: regex_extract
    variable: FIRST_NAME
    from_text: true
    pattern: '\b([A-Z][a-z]+)\s+([A-Z][a-z]+)\b'
    group: 1

  - type: regex_extract
    variable: LAST_NAME
    from_text: true
    pattern: '\b([A-Z][a-z]+)\s+([A-Z][a-z]+)\b'
    group: 2

  - type: derive
    variable: SSN_LAST_FOUR
    from: SSN
    method: slice
    args:
      start: -4
```

## Tips for Writing Rules

1. **Be Specific**: Make criteria specific enough to avoid false matches
2. **Test Thoroughly**: Test rules against various document formats
3. **Order Matters**: The processor uses the first matching rule
4. **Regex Performance**: Keep regex patterns simple for better performance
5. **Variable Dependencies**: Ensure derived variables depend on variables that were already extracted

## Adding New Rules

To add support for a new form type:

1. Create a new YAML file in this directory (e.g., `1099-misc.yaml`)
2. Define the form structure following the format above
3. Test with sample documents
4. The processor will automatically load all YAML files in this directory
