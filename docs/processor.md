# Nominal Processor

The Nominal Processor is a rule-based document processing engine that identifies tax forms and extracts relevant information using a Domain-Specific Language (DSL).

## Overview

The processor uses YAML-based rule files to define:
1. **Criteria** - Conditions to identify specific form types
2. **Actions** - Operations to extract and transform variables

## Quick Start

```python
from nominal.processor import NominalProcessor
from nominal.reader import NominalReader

# Load rules
processor = NominalProcessor('rules/')

# Read and process a document
reader = NominalReader()
text = reader.read_pdf('sample.pdf')
result = processor.process_document(text)

if result:
    print(f"Form: {result['form_name']}")
    print(f"Variables: {result['variables']}")
```

## Architecture

### Core Components

1. **RuleParser** - Parses YAML rule files into internal Rule objects
2. **CriteriaEvaluator** - Evaluates matching criteria against document text
3. **ActionExecutor** - Executes actions to extract and transform variables
4. **NominalProcessor** - Orchestrates the entire processing pipeline

### Data Flow

```
YAML Rule File → RuleParser → Rule Object
                                    ↓
Document Text → CriteriaEvaluator → Match?
                                    ↓ (yes)
                              ActionExecutor → Extracted Variables
```

## Rule File Format

See [rules/README.md](../rules/README.md) for detailed DSL specification.

### Basic Structure

```yaml
form_name: FORM_NAME
description: Form description

variables:
  global: [VAR1, VAR2]  # Available across batches
  local: [VAR3]          # Form-specific

criteria:
  - type: criterion_type
    # ... criterion fields

actions:
  - type: action_type
    # ... action fields
```

## Criteria Types

### contains
Simple text search (case-sensitive or case-insensitive).

```yaml
- type: contains
  value: "form w-2"
  case_sensitive: false
```

### regex
Pattern matching with optional value capture.

```yaml
- type: regex
  pattern: '\b\d{3}-\d{2}-\d{4}\b'
  capture: true
  variable: SSN
```

### all
All sub-criteria must match.

```yaml
- type: all
  criteria:
    - type: contains
      value: "w-2"
    - type: regex
      pattern: '\d{3}-\d{2}-\d{4}'
```

### any
At least one sub-criterion must match.

```yaml
- type: any
  criteria:
    - type: contains
      value: "w-2"
    - type: contains
      value: "w2"
```

## Action Types

### set
Set variable to literal value.

```yaml
- type: set
  variable: FORM_NAME
  value: "W2"
```

### regex_extract
Extract value using regex pattern.

```yaml
- type: regex_extract
  variable: FIRST_NAME
  from_text: true
  pattern: 'Name:\s+(\w+)'
  group: 1
```

### derive
Derive value from another variable.

```yaml
- type: derive
  variable: SSN_LAST_FOUR
  from: SSN
  method: slice
  args:
    start: -4
```

Available methods:
- `slice` - Extract substring
- `upper` - Convert to uppercase
- `lower` - Convert to lowercase

### extract
Extract from variable using various methods.

```yaml
- type: extract
  variable: FIRST_NAME
  from: FULL_NAME
  method: split
  args:
    pattern: '\s+'
    index: 0
```

### validated_regex_extract
Extract and validate person names using US Census data (Milestone 4).

```yaml
- type: validated_regex_extract
  variable: FULL_NAME
  from_text: true
  pattern: '\b([A-Z][A-Z]+(?:\s+[A-Z]\.?)?\s+[A-Z][A-Z]+)'
  group: 1
  min_confidence: 0.5  # Optional, defaults to 0.5
```

**Features:**
- Extracts all candidates matching the pattern
- Validates each against US Census first/last name databases (90K+ entries)
- Scores candidates with confidence levels (0.0-1.0)
- Returns highest-confidence match above threshold
- Distinguishes person names from organization names

**Confidence Scoring:**
- First name in database: +0.5
- Last name in database: +0.5
- Has middle initial: +0.1
- Maximum: 1.0

**Example Results:**
- `MICHAEL M JORDAN`: 1.0 ✅ (both names + middle initial)
- `ELIZABETH A DARLING`: 1.0 ✅ (both names + middle initial)
- `UNIVERSITY OF PITTSBURGH`: 0.0 ❌ (not valid person name)
- `STERLING HEIGHTS`: 0.0 ❌ (city name, not person)

See [docs/name_extraction_strategy.md](name_extraction_strategy.md) for implementation details.

## API Reference

### NominalProcessor

Main processor class.

#### Constructor

```python
processor = NominalProcessor(rules_dir=None)
```

- `rules_dir` (optional): Directory containing rule files. If provided, loads all `.yaml` and `.yml` files.

#### Methods

##### load_rules(rules_dir: str)
Load all rule files from a directory.

```python
processor.load_rules('path/to/rules')
```

##### load_rule(rule_path: str)
Load a single rule file.

```python
processor.load_rule('path/to/rule.yaml')
```

##### process_document(text: str) → Optional[Dict[str, Any]]
Process document text and extract variables.

Returns:
- `None` if no rule matches
- Dict with keys:
  - `form_name`: Identified form name
  - `variables`: Dict of extracted variables
  - `rule_description`: Rule description

```python
result = processor.process_document(text)
if result:
    print(result['form_name'])
    print(result['variables'])
```

### RuleParser

Parses YAML rule files.

```python
from nominal.processor import RuleParser

parser = RuleParser()
rule = parser.parse_file('w2.yaml')
```

## Variable Scopes

### Global Variables
Values available across all documents in a batch.
- Example: FIRST_NAME, LAST_NAME, SSN

### Local Variables
Values specific to a single form/document.
- Example: FORM_NAME

## Best Practices

### Writing Rules

1. **Be Specific**: Make criteria specific enough to avoid false matches
2. **Order Matters**: The first matching rule is used
3. **Test Thoroughly**: Test with various document formats
4. **Keep Regex Simple**: Complex patterns can slow processing

### Processing Performance

1. **Load Rules Once**: Load all rules at initialization, not per document
2. **Reuse Instances**: Create one processor instance and reuse it
3. **Batch Processing**: Process multiple documents with the same processor

```python
# Good: Load once, reuse
processor = NominalProcessor('rules/')
for doc in documents:
    result = processor.process_document(doc)

# Bad: Load for each document
for doc in documents:
    processor = NominalProcessor('rules/')  # Wasteful!
    result = processor.process_document(doc)
```

## Error Handling

### File Not Found
```python
try:
    processor = NominalProcessor('nonexistent/')
except FileNotFoundError as e:
    print(f"Rules directory not found: {e}")
```

### Invalid Rule Format
```python
try:
    rule = parser.parse_file('invalid.yaml')
except ValueError as e:
    print(f"Invalid rule: {e}")
```

### No Match Found
```python
result = processor.process_document(text)
if result is None:
    print("No matching form found")
    # Handle unmatched document
```

## Examples

### Example 1: Simple W2 Processing

```python
from nominal.processor import NominalProcessor
from nominal.reader import NominalReader

reader = NominalReader()
processor = NominalProcessor('rules/')

text = reader.read_pdf('w2.pdf')
result = processor.process_document(text)

if result:
    form = result['variables'].get('FORM_NAME')
    ssn = result['variables'].get('SSN_LAST_FOUR')
    print(f"Form: {form}, SSN: ***-**-{ssn}")
```

### Example 2: Batch Processing

```python
from pathlib import Path
from nominal.processor import NominalProcessor
from nominal.reader import NominalReader

processor = NominalProcessor('rules/')
reader = NominalReader()

pdf_dir = Path('documents/')
for pdf_file in pdf_dir.glob('*.pdf'):
    text = reader.read_pdf(str(pdf_file))
    result = processor.process_document(text)

    if result:
        # Process matched document
        form_name = result['variables'].get('FORM_NAME', 'UNKNOWN')
        print(f"{pdf_file.name} → {form_name}")
    else:
        print(f"{pdf_file.name} → No match")
```

### Example 3: Custom File Naming

```python
def generate_filename(result):
    """Generate filename from extracted variables."""
    if not result:
        return None

    vars = result['variables']
    form = vars.get('FORM_NAME', 'UNKNOWN')
    last_name = vars.get('LAST_NAME', 'UNKNOWN')
    ssn_last_four = vars.get('SSN_LAST_FOUR', 'XXXX')

    return f"{form}_{last_name}_{ssn_last_four}.pdf"

# Usage
result = processor.process_document(text)
new_filename = generate_filename(result)
```

## Testing

Run the test suite:

```bash
# Unit tests
uv run pytest test/nominal/test_processor.py -v

# Integration tests
uv run pytest test/nominal/test_processor_integration.py -v

# All tests
uv run pytest test/nominal/ -v
```

## Extending the Processor

### Adding New Criterion Types

1. Add criterion type to `CriteriaEvaluator`:

```python
def evaluate(self, criterion: Criterion, text: str) -> bool:
    if criterion.type == 'new_type':
        return self._evaluate_new_type(criterion, text)
    # ... existing code

def _evaluate_new_type(self, criterion: Criterion, text: str) -> bool:
    # Implement new criterion logic
    pass
```

2. Update `RuleParser._parse_criterion()` to parse new fields.

### Adding New Action Types

1. Add action type to `ActionExecutor`:

```python
def execute(self, action: Action, captured_values: Dict[str, str] = None):
    if action.type == 'new_action':
        self._execute_new_action(action)
    # ... existing code

def _execute_new_action(self, action: Action):
    # Implement new action logic
    pass
```

2. Update `RuleParser._parse_action()` to parse new fields.

## Troubleshooting

### Rule Not Matching

1. **Check Criteria**: Verify criteria patterns match actual document text
2. **Test Regex**: Use online regex testers to validate patterns
3. **Case Sensitivity**: Check if case-sensitive search is appropriate
4. **Print Text**: Print extracted text to see what the processor sees

```python
text = reader.read_pdf('document.pdf')
print(text)  # Inspect actual text
result = processor.process_document(text)
```

### Variables Not Extracted

1. **Check Actions**: Verify action patterns and variable names
2. **Order Dependencies**: Ensure derived variables come after source variables
3. **Group Numbers**: Verify regex group numbers (0 = full match, 1+ = groups)

### Multiple Rules Matching

The processor returns the first matching rule. To control which rule matches:
1. Order rules by specificity (most specific first)
2. Make criteria more specific
3. Test with various documents to ensure uniqueness

## Performance Considerations

- **Rule Count**: Processor scales linearly with number of rules
- **Regex Complexity**: Complex patterns can slow processing
- **Document Size**: Large documents take longer to process
- **OCR Overhead**: OCR is the slowest operation (when needed)

Typical processing times (on modern hardware):
- Rule loading: < 100ms for ~10 rules
- Text-based PDF: < 50ms per page
- Image-based PDF (with OCR): 1-3s per page
- Criteria evaluation: < 10ms per rule
- Action execution: < 5ms

## See Also

- [Rules DSL Documentation](../rules/README.md)
- [Nominal Reader Documentation](reader.md)
- [Example Script](../example_processor.py)
