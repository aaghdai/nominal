# Logging System Documentation

The Nominal project includes a comprehensive colored logging system that provides visibility into all components (reader, processor, and future orchestrator). Logging is configurable at the project level for consistent behavior across all components.

## Features

### 1. Colored Output
- **DEBUG** (cyan): Detailed debugging information
- **INFO** (green): Actionable information about processing steps
- **WARNING** (yellow): Potential issues like global variable conflicts
- **ERROR** (red): Error conditions
- **CRITICAL** (magenta): Critical failures

### 2. Log Levels

#### DEBUG Level
Shows detailed debugging information including:
- Individual criterion checks (regex patterns, contains checks)
- Regex extraction attempts (both successful and failed)
- Variable derivation steps
- Sub-criterion evaluations in composite rules

Example:
```python
import logging
from nominal.processor import NominalProcessor, set_log_level

set_log_level(logging.DEBUG)
processor = NominalProcessor('rules/')
```

#### INFO Level (Default)
Shows actionable information including:
- Rule loading and parsing
- Document processing start
- Rule evaluation results
- Successful variable extractions
- Variable derivations
- Final match results

#### WARNING Level
Shows only warnings and errors:
- Global variable conflicts across documents
- Missing rule files
- Parsing warnings

#### ERROR Level
Shows only errors:
- Invalid regex patterns
- File not found errors
- Parsing failures
- Derivation errors

## Usage

### Project-Level Configuration (Recommended)

The recommended way to configure logging is at the project level using `configure_logging()`:

```python
import logging
from nominal import configure_logging
from nominal.reader import NominalReader
from nominal.processor import NominalProcessor

# Configure all components to DEBUG level
configure_logging(logging.DEBUG)

# Or configure only specific components
configure_logging(logging.DEBUG, component='processor')  # Only processor
configure_logging(logging.WARNING, component='reader')    # Only reader

# Now use the components - they'll all use the configured logging
reader = NominalReader()
processor = NominalProcessor('rules/')
```

### Basic Usage (Default INFO Level)

```python
from nominal.reader import NominalReader
from nominal.processor import NominalProcessor

# Logging is automatically enabled at INFO level for all components
reader = NominalReader()
processor = NominalProcessor('rules/')
result = processor.process_document(text)
```

### Changing Log Level for All Components

```python
import logging
from nominal import configure_logging

# Set all components to DEBUG for detailed information
configure_logging(logging.DEBUG)

# Set all components to WARNING to see only warnings and errors
configure_logging(logging.WARNING)

# Set all components to ERROR to see only errors
configure_logging(logging.ERROR)
```

### Changing Log Level for Specific Components

```python
import logging
from nominal import configure_logging

# Configure only processor to DEBUG
configure_logging(logging.DEBUG, component='processor')

# Configure only reader to WARNING
configure_logging(logging.WARNING, component='reader')
```

### Custom Logger Setup

```python
from nominal import setup_logger
import logging

# Create a custom logger
my_logger = setup_logger('my_app', level=logging.DEBUG)
my_logger.info("Custom log message")
```

### Getting an Existing Logger

```python
from nominal import get_logger

# Get component loggers
reader_logger = get_logger('nominal.reader')
processor_logger = get_logger('nominal.processor')
rule_logger = get_logger('nominal.processor.rule')
```

## Log Output Examples

### INFO Level Output
```
INFO     [nominal.processor] NominalProcessor initialized
INFO     [nominal.processor] Loading rules from directory: rules
INFO     [nominal.processor.parser] Parsing rule file: rules/w2.yaml
INFO     [nominal.processor.parser] ✓ Successfully parsed rule: W2
INFO     [nominal.processor] ✓ Loaded rule: W2 from w2.yaml
INFO     [nominal.processor] Successfully loaded 2 rule(s)
INFO     [nominal.processor] Processing document (8352 characters)
INFO     [nominal.processor.rule] Evaluating rule: W2
INFO     [nominal.processor.rule] ✓ All criteria passed for rule W2
INFO     [nominal.processor.action] Setting variable: FORM_NAME='W2'
INFO     [nominal.processor.action] ✓ Extracted SSN='123-45-6789' using regex
INFO     [nominal.processor.rule] ✓ Rule W2 matched successfully with 5 variable(s) extracted
INFO     [nominal.processor] ✓ Document matched rule W2
INFO     [nominal.processor]   Global: 3 var(s), Local: 1 var(s), Derived: 1 var(s)
```

### DEBUG Level Output (Additional Messages)
```
DEBUG    [nominal.processor.criterion] Checking regex criterion: pattern='(?i)w-?2', capture=False
DEBUG    [nominal.processor.criterion] ✓ Regex criterion matched: '(?i)w-?2'
DEBUG    [nominal.processor.action] Attempting regex extraction for SSN: pattern='\b(\d{3}-\d{2}-\d{4})\b'
DEBUG    [nominal.processor.action] Deriving SSN_LAST_FOUR from SSN='123-45-6789' using method 'slice'
```

### WARNING Level Output
```
WARNING  [nominal.processor] Global variable conflict: SSN = '123-45-6789' vs '987-65-4321' (keeping first value)
WARNING  [nominal.processor] No rule files (*.yaml or *.yml) found in rules/
```

### ERROR Level Output
```
ERROR    [nominal.processor.parser] Rule file not found: rules/missing.yaml
ERROR    [nominal.processor.criterion] Invalid regex pattern '(?P<bad': missing ), unterminated subpattern at position 5
ERROR    [nominal.processor.action] Error deriving SSN_LAST_FOUR from SSN: string index out of range
```

## Logger Hierarchy

The logging system uses a hierarchical structure:

```
nominal                              # Root logger
├── nominal.reader                   # PDF reading and OCR
├── nominal.processor                 # Main processor logger
│   ├── nominal.processor.parser     # Rule parsing
│   ├── nominal.processor.rule       # Rule evaluation
│   ├── nominal.processor.criterion  # Criterion matching
│   ├── nominal.processor.action     # Action execution
│   └── nominal.processor.processor # Document processing orchestration
└── nominal.orchestrator             # Future: File organization
```

Setting the log level on a parent logger affects all child loggers. Using `configure_logging()` with a component name targets that specific branch of the hierarchy.

## Implementation Details

### ColoredFormatter
The logging system uses a custom `ColoredFormatter` that adds ANSI color codes to the output:
- Colors are applied to the log level
- The format includes: `LEVEL [logger_name] message`
- Colors work in most modern terminals

### Logger Setup
Loggers are automatically created when modules are imported using `setup_logger()`:
- Prevents duplicate handlers
- Uses a consistent format across all loggers
- Outputs to stdout for better integration with pipelines

## Best Practices

1. **Default to INFO Level**: Provides good visibility without overwhelming detail
2. **Use DEBUG for Development**: When debugging rule files or investigating why documents don't match
3. **Use WARNING for Production**: Reduces noise while still catching important issues
4. **Use ERROR for Critical Systems**: When you only want to know about failures

## Disabling Logging

To completely disable logging output:

```python
import logging
from nominal import configure_logging

configure_logging(logging.CRITICAL + 1)  # Disable all logs
```

Or use Python's standard logging configuration:

```python
import logging

# Disable all Nominal logging
logging.getLogger('nominal').disabled = True

# Or disable specific components
logging.getLogger('nominal.processor').disabled = True
logging.getLogger('nominal.reader').disabled = True
```

## Component-Specific Logging

### Reader Logging

The reader logs:
- **INFO**: File reading start/completion, OCR usage
- **DEBUG**: Page-by-page extraction details, OCR decisions

### Processor Logging

The processor logs:
- **INFO**: Rule loading, document processing, matches
- **DEBUG**: Criterion checks, action attempts
- **WARNING**: Global variable conflicts
- **ERROR**: Invalid patterns, parsing failures

