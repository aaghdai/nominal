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

To update or regenerate the name dictionaries:

```bash
cd data/

# Download and extract surnames (top 50,000)
wget https://www2.census.gov/topics/genealogy/2010surnames/names.zip
unzip names.zip
python3 -c "
import csv
with open('Names_2010Census.csv', 'r') as f:
    reader = csv.DictReader(f)
    surnames = [row['name'].strip().upper() for row in reader][:50000]
with open('last_names.txt', 'w') as f:
    f.write('\n'.join(surnames))
"

# Download and extract first names (2020-2023)
wget https://www.ssa.gov/oact/babynames/names.zip
unzip -o names.zip yob2020.txt yob2021.txt yob2022.txt yob2023.txt
python3 -c "
first_names = set()
for year in [2020, 2021, 2022, 2023]:
    with open(f'yob{year}.txt', 'r') as f:
        for line in f:
            first_names.add(line.split(',')[0].strip().upper())
with open('first_names.txt', 'w') as f:
    f.write('\n'.join(sorted(first_names)))
"

# Clean up
rm -f yob*.txt Names_2010Census.* names.zip
```
