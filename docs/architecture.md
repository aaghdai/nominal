# Nominal Architecture Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     NOMINAL SYSTEM                           │
└─────────────────────────────────────────────────────────────┘

┌──────────────┐       ┌──────────────┐       ┌──────────────┐
│   INPUT      │       │  PROCESSING  │       │   OUTPUT     │
│              │       │              │       │              │
│  PDF Files   │──────▶│  Components  │──────▶│  Organized   │
│  (Tax Forms) │       │              │       │  Files       │
└──────────────┘       └──────────────┘       └──────────────┘
```

## Component Architecture

```
┌─────────────────────────────────────────────────────────────┐
│ 1. NOMINAL READER (✅ Complete)                              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Input: PDF File                                            │
│     │                                                        │
│     ├─▶ Text Extraction (PyMuPDF)                           │
│     │      │                                                 │
│     │      ├─ Text Found? ─▶ Return Text                    │
│     │      │                                                 │
│     │      └─ Low/No Text? ─▶ OCR (Tesseract)               │
│     │                            │                           │
│     └────────────────────────────┘                           │
│                                                              │
│  Output: Text Content                                       │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ 2. NOMINAL PROCESSOR (✅ Complete)                           │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Input: Text Content + Rule Files                           │
│     │                                                        │
│     ├─▶ Load Rules (RuleParser)                             │
│     │      │                                                 │
│     │      └─▶ Parse YAML ─▶ Rule Objects                   │
│     │                                                        │
│     ├─▶ Match Criteria (CriteriaEvaluator)                  │
│     │      │                                                 │
│     │      ├─ Check: contains, regex, all, any              │
│     │      │                                                 │
│     │      └─ Match Found? ─┐                                │
│     │                       │                                │
│     │                       ├─ Yes ─▶ Execute Actions       │
│     │                       │                                │
│     │                       └─ No ─▶ Try Next Rule          │
│     │                                                        │
│     └─▶ Extract Variables (ActionExecutor)                  │
│            │                                                 │
│            ├─▶ set, regex_extract, derive, extract          │
│            └─▶ validated_regex_extract (with name scoring)  │
│                                                              │
│  Output: {form_name, variables}                             │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ 3. NOMINAL ORCHESTRATOR (✅ Complete)                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Input: Directory of PDFs                                   │
│     │                                                        │
│     ├─▶ For each file:                                      │
│     │      │                                                 │
│     │      ├─▶ Read (Nominal Reader)                        │
│     │      │                                                 │
│     │      ├─▶ Process (Nominal Processor)                  │
│     │      │      │                                          │
│     │      │      └─▶ Extract & Validate Variables          │
│     │      │                                                 │
│     │      ├─▶ Apply Derived Variables                      │
│     │      │      │                                          │
│     │      │      └─▶ Compute: LAST_NAME, FIRST_NAME, etc.  │
│     │      │                                                 │
│     │      ├─▶ Generate Filename                            │
│     │      │      │                                          │
│     │      │      └─▶ Template: {FORM}_{NAME}_{SSN}        │
│     │      │                                                 │
│     │      └─▶ Copy/Rename to Output Directory              │
│     │                                                        │
│     └─▶ Error Handling & Logging                            │
│            │                                                 │
│            └─▶ Unmatched files → unmatched/ directory       │
│                                                              │
│  Output: Organized Files + Logs                             │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ 4. NAME VALIDATION (✅ Complete)                             │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Input: Extracted name candidates                           │
│     │                                                        │
│     ├─▶ Load Name Dictionaries                              │
│     │      │                                                 │
│     │      ├─▶ first_names.txt (40K+ entries)               │
│     │      └─▶ last_names.txt (50K entries)                 │
│     │                                                        │
│     ├─▶ Validate Each Candidate                             │
│     │      │                                                 │
│     │      ├─▶ Check first name against dictionary          │
│     │      ├─▶ Check last name against dictionary           │
│     │      ├─▶ Check for middle initial                     │
│     │      └─▶ Calculate confidence score (0.0-1.0)         │
│     │                                                        │
│     └─▶ Return Best Match Above Threshold                   │
│                                                              │
│  Output: Validated person name (e.g., "MICHAEL M JORDAN")   │
└─────────────────────────────────────────────────────────────┘
```

## Data Flow

```
┌────────────┐
│ Input.pdf  │
└─────┬──────┘
      │
      ▼
┌─────────────────┐
│ Nominal Reader  │
└─────┬───────────┘
      │
      ▼ (text content)
      │
      │   ┌──────────────┐
      │   │ Rule Files   │
      │   │  - w2.yaml   │
      │   │  - 1099.yaml │
      │   └──────┬───────┘
      │          │
      ▼          ▼
┌──────────────────────┐
│ Nominal Processor    │
│                      │
│  ┌────────────────┐  │
│  │ Match Criteria │  │
│  └────────┬───────┘  │
│           │          │
│           ▼          │
│  ┌────────────────┐  │
│  │ Execute Actions│  │
│  └────────┬───────┘  │
└───────────┼──────────┘
            │
            ▼
┌───────────────────────┐
│ Extracted Variables   │
│                       │
│ {                     │
│   form_name: "W2"     │
│   FIRST_NAME: "John"  │
│   LAST_NAME: "Smith"  │https://github.com/aaghdai/nominal/
│ Output: W2_Smith_6789.pdf│
└──────────────────────────┘
```

## Rule Processing Flow

```
┌─────────────┐
│ Document    │
│ Text        │
└──────┬──────┘
       │
       ▼
┌──────────────────┐
│ For Each Rule:   │
└──────┬───────────┘
       │
       ▼
┌────────────────────────┐
│ Evaluate Criteria      │
│                        │
│  ├─ contains          │
│  │   "w-2"?           │
│  │   ✓ Yes            │
│  │                    │
│  ├─ regex             │
│  │   \d{3}-\d{2}-\d{4}│
│  │   ✓ Match: captured│
│  │                    │
│  └─ any/all           │
│      ✓ All Match      │
└────────┬───────────────┘
         │
         ▼ (match found)
┌────────────────────────┐
│ Execute Actions        │
│                        │
│  1. set: FORM_NAME     │
│     FORM_NAME = "W2"   │
│                        │
│  2. regex_extract:     │
│     FIRST_NAME = "..."│
│                        │
│  3. derive:            │
│     SSN_LAST_FOUR = ...│
└────────┬───────────────┘
         │
         ▼
┌────────────────────────┐
│ Return Result          │
│ {form_name, variables} │
└────────────────────────┘
```

## Class Hierarchy

```
NominalReader (src/nominal/reader/)
├─ __init__(ocr_fallback, min_text_length)
├─ read_pdf(file_path) → str
└─ _ocr_page(page) → str

NominalProcessor (src/nominal/processor/)
├─ __init__(rules_dir)
├─ load_rules(rules_dir)
├─ load_rule(rule_path)
├─ process_document(text, document_id) → Dict
└─ get_all_declared_variables() → set

NominalOrchestrator (src/nominal/orchestrator/)
├─ __init__(rules_dir, derived_variables)
├─ process_directory(input_dir, output_dir, filename_pattern) → Stats
├─ _validate_pattern(pattern) → bool
├─ _apply_orchestrator_derivations(variables) → Dict
└─ _generate_filename(pattern, variables, rule_id) → str

RuleParser (src/nominal/rules/)
├─ parse_file(rule_path) → Rule
├─ parse_dict(data) → Rule
├─ _parse_criterion(data) → Criterion
└─ _parse_action(data) → Action

Action Classes (src/nominal/rules/action.py)
├─ SetAction - Assign literal values
├─ RegexExtractAction - Extract using patterns
├─ DeriveAction - Transform variables
├─ ExtractAction - Split and extract
└─ ValidatedRegexExtractAction - Extract with name validation

NameValidator (src/nominal/rules/name_validator.py)
├─ get_first_names() → set
├─ get_last_names() → set
├─ validate_full_name(name) → Dict
└─ score_name_candidates(candidates) → List[Tuple]
```

## File Organization

```
nominal/
│
├── src/nominal/
│   ├── __init__.py
│   ├── main.py                      ← CLI entry point
│   ├── scripts_derived.py           ← Advanced CLI
│   ├── reader/                      ← Milestone 1 ✅
│   │   ├── __init__.py
│   │   └── reader.py
│   ├── logging/                     ← Logging system
│   │   ├── __init__.py
│   │   └── config.py
│   ├── processor/                   ← Milestone 2 ✅
│   │   ├── __init__.py
│   │   └── processor.py
│   ├── orchestrator/                ← Milestone 3 ✅
│   │   ├── __init__.py
│   │   └── orchestrator.py
│   ├── rules/                       ← Rules engine
│   │   ├── __init__.py
│   │   ├── action.py
│   │   ├── criterion.py
│   │   ├── enums.py
│   │   ├── manager.py
│   │   ├── name_validator.py        ← Milestone 4 ✅
│   │   ├── parser.py
│   │   ├── rule.py
│   │   └── validator.py
│   └── scripts/                     ← Utility scripts
│       ├── __init__.py
│       └── generate_names.py
│
├── rules/                           ← Rule Definitions
│   ├── global/
│   │   └── person-info.yaml         ← Enhanced with validation
│   ├── forms/
│   │   ├── w2.yaml
│   │   ├── 1099-div.yaml
│   │   └── 1099-misc.yaml
│   └── README.md
│
├── data/                            ← Name validation data
│   ├── first_names.txt              ← 40K+ first names
│   ├── last_names.txt               ← 50K surnames
│   └── README.md
│
├── test/                            ← 46 tests ✅
│   ├── fixtures/
│   │   ├── Sample-W2.pdf
│   │   └── Sample-1099-image.pdf
│   └── nominal/
│       ├── reader/
│       ├── logging/
│       ├── processor/
│       ├── orchestrator/
│       └── rules/
│
├── docs/
│   ├── architecture.md              ← This file
│   ├── processor.md
│   ├── name_extraction_strategy.md
│   └── milestone2_summary.md
│
├── examples/
│   ├── example_processor.py
│   ├── example_logging.py
│   └── README.md
│
├── scripts/
│   ├── generate_name_dictionaries.py
│   ├── update_changelog_stats.sh
│   └── README.md
│
├── tools/
│   ├── validate_rules.py
│   └── README.md
│
├── PLAN.md
├── README.md
└── CHANGELOG.md
```

## Technology Stack

```
┌─────────────────────────────────────────────────────┐
│              Python 3.13+                           │
└─────────────────────────────────────────────────────┘
                      │
      ┌───────────────┼───────────────┐
      │               │               │
┌─────▼─────┐  ┌──────▼──────┐  ┌────▼────────┐
│  Reader   │  │  Processor  │  │Orchestrator │
└───────────┘  └─────────────┘  └─────────────┘
      │              │                 │
      │              │                 │
┌─────▼─────┐  ┌─────▼─────┐    ┌─────▼─────┐
│ PyMuPDF   │  │  PyYAML   │    │ US Census │
│ Tesseract │  │  re       │    │ SSA Data  │
│ Pillow    │  │ (stdlib)  │    │ (90K+     │
└───────────┘  └───────────┘    │ names)    │
                                └───────────┘
```

## Key Features by Milestone

### ✅ Milestone 1: Reader (Complete)
- PDF text extraction with PyMuPDF
- OCR for image-based PDFs with Tesseract
- Configurable OCR thresholds
- Comprehensive error handling
- 5 tests, all passing

### ✅ Milestone 2: Processor (Complete)
- YAML-based DSL for rule definition
- Pattern matching (contains, regex, all, any)
- Variable extraction (set, regex_extract, derive, extract)
- Global and local variable scoping
- Batch processing capability
- First-match rule selection
- 24 tests, all passing

### ✅ Milestone 3: Orchestrator (Complete)
- Recursive directory scanning
- Pattern-based file renaming
- Variable validation
- Error logging and unmatched file tracking
- CLI interface (`nominal` command)
- Integration with Reader and Processor
- 4 tests, all passing

### ✅ Milestone 4: Advanced Features (Complete)
- **Validated Name Extraction**:
  - US Census and SSA name databases (90K+ entries)
  - Confidence-based scoring (0.0-1.0)
  - Distinguishes person names from organizations
  - `validated_regex_extract` action type
- **Orchestrator-Level Derived Variables**:
  - Programmatic variable derivation
  - Built-in functions (LAST_NAME, FIRST_NAME, etc.)
  - Pattern validation
  - `nominal-derived` CLI command
- **Utility Scripts**:
  - `nominal-generate-names` CLI for dictionary generation
  - Automatic downloads from government sources
- **Documentation**:
  - Name extraction strategy guide
  - Comprehensive examples and usage docs
- 13 additional tests (46 total), all passing

## Current System Capabilities

The complete Nominal system now provides:

1. **✅ Document Reading**: PDFs with automatic OCR fallback
2. **✅ Form Classification**: YAML-based rule engine
3. **✅ Variable Extraction**: Multiple extraction strategies
4. **✅ Name Validation**: Census-data-backed validation
5. **✅ Batch Processing**: Directory-level orchestration
6. **✅ Derived Variables**: Computed values from extracted data
7. **✅ File Organization**: Pattern-based renaming
8. **✅ Error Handling**: Unmatched file tracking and logging
9. **✅ CLI Interface**: 3 commands (nominal, nominal-derived, nominal-generate-names)
10. **✅ Full Test Coverage**: 46 tests across all components
