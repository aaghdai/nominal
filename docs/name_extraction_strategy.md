# Name Extraction Strategy

## ✅ Implemented Solution (January 2026)

The system now uses a **validated multi-strategy approach** combining:

1. **Context-Aware Field Extraction** (Strategies 1-3 in `person-info.yaml`)
   - Looks for explicit field labels: "Employee's name", "RECIPIENT'S name", etc.
   - Most reliable for standard form layouts

2. **Validated Pattern Matching** (Strategy 4 - Fallback)
   - Uses the new `validated_regex_extract` action type
   - Extracts ALL candidate names matching the pattern
   - Validates each against US Census name databases
   - Returns the highest-confidence match above threshold

### How Validation Works

```yaml
# In rules/global/person-info.yaml
- type: validated_regex_extract
  variable: FULL_NAME
  from_text: true
  pattern: '\b([A-Z][A-Z]+(?:\s+[A-Z]\.?)?\s+[A-Z][A-Z]+)(?=...)'
  group: 1
  min_confidence: 0.5  # 50% threshold
```

**Confidence scoring:**
- First name in database: +0.5
- Last name in database: +0.5
- Has middle initial: +0.1
- **Total**: 0.0-1.0 (capped at 1.0)

**Example results:**
- `MICHAEL M JORDAN`: 1.0 (both names + middle initial)
- `ELIZABETH A DARLING`: 1.0 (both names + middle initial)
- `STERLING HEIGHTS`: 0.0 (neither in database)
- `UNIVERSITY OF PITTSBURGH`: 0.0 (not valid names)

### Data Files

Located in `data/`:
- `first_names.txt`: 40,836 first names from SSA (2020-2023)
- `last_names.txt`: 50,000 surnames from US Census (2010)

See `data/README.md` for regeneration instructions.

---

## Original Problem Analysis (Historical)

The initial regex-based name extraction was brittle:
- Over-fitted to specific document layouts
- No validation that extracted text is actually a name
- Incomplete organization keyword exclusion
- Context-blind (doesn't use field labels)

## Solution Design (Multi-Strategy Approach)

### Strategy 1: Context-Aware Field Extraction (PRIMARY) ✅

**Use field labels to guide extraction** - most reliable approach.

Tax forms have explicit field labels:
- W2: "Employee's name", "Employer's name"
- 1099: "PAYER'S name", "RECIPIENT'S name"
- Common patterns: "Taxpayer name:", "Recipient:", etc.

**Implementation:**
```yaml
# Extract name by looking for field label + name pattern
- type: regex_extract
  variable: EMPLOYEE_NAME
  pattern: '(?i)employee.*?name.*?[:>\s]+([A-Z][a-z]+(?:\s+[A-Z]\.?)?\s+[A-Z][a-z]+)'
  group: 1

- type: regex_extract
  variable: RECIPIENT_NAME
  pattern: '(?i)recipient.*?name.*?[:>\s]+([A-Z][a-z]+(?:\s+[A-Z]\.?)?\s+[A-Z][a-z]+)'
  group: 1
```

**Advantages:**
- Robust across different layouts
- Self-documenting (uses actual form field names)
- Less prone to false matches

### Strategy 2: Name Dictionary Validation (SECONDARY) ✅

**Validate extracted names against common name databases.**

Use US Census name data (public domain):
- [US Census First Names](https://www.ssa.gov/oact/babynames/limits.html) - 150K+ names
- [US Census Last Names](https://www.census.gov/topics/population/genealogy/data/2010_surnames.html) - 150K+ surnames

**Implementation approach:**
1. Extract candidate names using patterns
2. Split into first/last name components
3. Validate first name against first name dictionary
4. Validate last name against surname dictionary
5. Rank candidates by validation score

**Pseudo-code:**
```python
def validate_name(full_name: str, first_names: set, last_names: set) -> float:
    """Return confidence score 0-1 for name validity."""
    parts = full_name.split()
    if len(parts) < 2:
        return 0.0

    first = parts[0].title()
    last = parts[-1].title()

    first_match = 1.0 if first in first_names else 0.0
    last_match = 1.0 if last in last_names else 0.0

    # Middle initial handling
    if len(parts) == 3 and len(parts[1]) <= 2:
        return (first_match + last_match) / 2

    return (first_match + last_match) / 2
```

**Trade-offs:**
- ✅ Very accurate validation
- ✅ Catches obvious errors (extracting "STERLING HEIGHTS" as a name)
- ❌ Requires external data files (~2-5MB)
- ❌ May reject uncommon/ethnic names
- ❌ Adds complexity

### Strategy 3: Multiple Pattern Matching with Ranking (FALLBACK) ⚡

**Try multiple extraction patterns and rank by confidence.**

Patterns to try:
1. Field label + name (highest confidence)
2. Name + address pattern
3. Name + dollar amount pattern
4. Standalone capitalized name pattern

**Implementation:**
```python
candidates = []

# Try pattern 1: Field labels
match1 = extract_with_label(text)
if match1:
    candidates.append((match1, 1.0, "field_label"))

# Try pattern 2: Name + address
match2 = extract_name_before_address(text)
if match2:
    candidates.append((match2, 0.8, "address_pattern"))

# Try pattern 3: Name + $ amount
match3 = extract_name_before_amount(text)
if match3:
    candidates.append((match3, 0.6, "amount_pattern"))

# Validate against name dictionary if available
for name, confidence, source in candidates:
    if name_validator:
        confidence *= name_validator.validate(name)

# Return highest confidence match
return max(candidates, key=lambda x: x[1])[0]
```

### Strategy 4: Organization Name Exclusion Database (ENHANCEMENT) 📋

Instead of hardcoded keywords, use a comprehensive list:
- Common org suffixes: Inc, LLC, Corp, Ltd, LLP, Foundation, Trust, etc.
- Org indicators: University, College, Bank, Company, Corporation, Department, Agency, Bureau, etc.
- Location indicators: City, County, State, Township, District, etc.

Could be maintained as a separate YAML file for easy updates.

## Recommended Implementation Plan

### Phase 1: Immediate (Context-Aware Extraction)
1. Update `person-info.yaml` to use field-label-based extraction
2. Add multiple extraction actions prioritizing field labels
3. Test with existing fixtures

### Phase 2: Short-term (Name Validation - Optional)
1. Add US Census name data to `data/` directory
2. Create name validator utility class
3. Integrate validation into extraction logic
4. Make it optional (graceful degradation if data missing)

### Phase 3: Medium-term (Multi-Strategy)
1. Implement candidate ranking system
2. Add confidence scores to extraction results
3. Log which strategy succeeded for debugging

## Example: Improved Rule File

```yaml
rule_id: person-info
description: Extract person information using multiple strategies

variables:
  global:
    - FULL_NAME
    - FIRST_NAME
    - LAST_NAME

criteria:
  - type: regex
    pattern: '.'

actions:
  # Strategy 1: Employee name from W2 forms
  - type: regex_extract
    variable: FULL_NAME
    pattern: '(?i)employee.*?name[^:]*?[:>\s]+\s*([A-Z][A-Z\s]+(?:[A-Z]\.?\s*)?[A-Z][A-Z]+)(?=\s*\n)'
    group: 1
    required: false

  # Strategy 2: Recipient name from 1099 forms
  - type: regex_extract
    variable: FULL_NAME
    pattern: '(?i)recipient.*?name[^:]*?[:>\s]+\s*([A-Z][A-Z\s]+(?:[A-Z]\.?\s*)?[A-Z][A-Z]+)(?=\s*\n)'
    group: 1
    required: false

  # Strategy 3: Payer name (for 1099 payer section)
  - type: regex_extract
    variable: PAYER_NAME
    pattern: '(?i)payer.*?name[^:]*?[:>\s]+\s*([A-Z][A-Z\s]+(?:[A-Z]\.?\s*)?[A-Z][A-Z]+)(?=\s*\$|\s*\n)'
    group: 1
    required: false

  # Strategy 4: Fallback - uppercase name followed by address
  # Only matches if FULL_NAME not already set
  - type: regex_extract
    variable: FULL_NAME
    pattern: '\b((?!(?:UNIVERSITY|COMPANY|CORPORATION|INC|LLC|DEPT|BANK|TRUST|CITY|COUNTY)\b)[A-Z][A-Z]+(?:\s+[A-Z]\.?)?(?:\s+[A-Z][A-Z]+))(?=\s*\n\s*\d{3,})'
    group: 1
    required: false
```

## Conclusion

The most robust approach combines:
1. **Primary**: Field-label-aware extraction (most reliable)
2. **Secondary**: Name dictionary validation (optional enhancement)
3. **Fallback**: Pattern matching with organization exclusion

This provides:
- ✅ High accuracy on standard forms
- ✅ Graceful degradation for non-standard layouts
- ✅ Maintainability (clear strategies, not magic regex)
- ✅ Debuggability (know which strategy succeeded)
