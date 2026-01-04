# Data Directory

This directory contains reference data for validation and enhancement.

## Name Dictionaries (Optional)

For enhanced name extraction validation, you can add US Census name data:

### First Names
Download from SSA: https://www.ssa.gov/oact/babynames/limits.html
- File: `first_names.txt` (one name per line)
- Format: Plain text, one name per line
- Source: US Social Security Administration baby names data

### Last Names
Download from Census: https://www.census.gov/topics/population/genealogy/data/2010_surnames.html
- File: `last_names.txt` (one name per line)
- Format: Plain text, one name per line
- Source: US Census Bureau 2010 surnames

### Usage

If these files exist, the name extraction can validate candidates:

```python
from pathlib import Path

def load_names(filename: str) -> set[str]:
    """Load name dictionary if available."""
    path = Path(__file__).parent / 'data' / filename
    if path.exists():
        return {line.strip().title() for line in path.read_text().splitlines()}
    return set()

FIRST_NAMES = load_names('first_names.txt')
LAST_NAMES = load_names('last_names.txt')
```

### License

Census data is public domain. No license restrictions for US government data.

### Note

Name dictionaries are **optional**. The system works without them using pattern-based extraction. They provide enhanced validation when available.
