# Data Directory

This directory contains reference data for validation and enhancement.

## Name Dictionaries

For enhanced name extraction validation, this directory contains US Census name data:

### First Names (`first_names.txt`)
- **Source**: US Social Security Administration baby names (2020-2023)
- **Format**: Plain text, one name per line (uppercase)
- **Size**: ~40,836 unique first names
- **URL**: https://www.ssa.gov/oact/babynames/names.zip

### Last Names (`last_names.txt`)
- **Source**: US Census Bureau 2010 surnames
- **Format**: Plain text, one name per line (uppercase)
- **Size**: Top 50,000 surnames
- **URL**: https://www2.census.gov/topics/genealogy/2010surnames/names.zip

### How It's Used

The `validated_regex_extract` action type uses these dictionaries to score potential name matches:

```yaml
# Example: Using validated regex extraction in rules
actions:
  - type: validated_regex_extract
    variable: FULL_NAME
    from_text: true
    pattern: '\b([A-Z][A-Z]+(?:\s+[A-Z]\.?)?\s+[A-Z][A-Z]+)'
    group: 1
    min_confidence: 0.5  # Requires at least 50% confidence
```

**How it works:**
1. Finds all potential name matches using the regex pattern
2. For each candidate, calculates a confidence score:
   - +0.5 if first name is in `first_names.txt`
   - +0.5 if last name is in `last_names.txt`
   - +0.1 bonus for middle initial or middle name
3. Returns the highest-scoring candidate above `min_confidence`

**Example validation:**
```python
from nominal.rules.name_validator import validate_full_name

# Valid person name
result = validate_full_name("MICHAEL M JORDAN")
# {'is_valid': True, 'confidence': 1.0,
#  'first_name': 'MICHAEL', 'last_name': 'JORDAN',
#  'reason': 'First name recognized; Last name recognized; Has middle initial'}

# Organization name (lower confidence)
result = validate_full_name("UNIVERSITY OF PITTSBURGH")
# {'is_valid': False, 'confidence': 0.0, ...}
```

### Benefits

This validation helps distinguish between:
- **Person names**: `MICHAEL M JORDAN`, `ELIZABETH A DARLING`
- **Organization names**: `UNIVERSITY OF PITTSBURGH`, `STERLING HEIGHTS BANK`
- **False positives**: `ZIP CODE`, `NONDIVIDEND DISTRIBUTIONS`

### License

- **US Census Data**: Public domain, no restrictions
- **SSA Data**: Public domain, US government data

### Regenerating the Data

To update or regenerate the name dictionaries, use the CLI command:

```bash
# Using the CLI command (recommended)
uv run nominal-generate-names

# Or run the script directly
python scripts/generate_name_dictionaries.py
```

The script will:
1. Download US Census Bureau surnames (2010)
2. Download SSA baby names (2020-2023)
3. Process and extract unique names
4. Create `data/first_names.txt` and `data/last_names.txt`
5. Clean up temporary files automatically

**Requirements:** `wget` or `curl` must be installed on your system.
