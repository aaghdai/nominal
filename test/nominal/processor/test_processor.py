"""
Unit tests for the Nominal Processor.
"""

import os
import tempfile

from nominal.processor import NominalProcessor
from nominal.rules import RuleParser


class TestNominalProcessor:
    """Tests for NominalProcessor."""

    def test_process_document_with_form_rule(self):
        """Test processing a document with a form rule (classification)."""
        processor = NominalProcessor()

        # Create a form rule for classification
        rule_data = {
            "rule_id": "W2",
            "description": "Test W2",
            "criteria": [{"type": "contains", "value": "form w-2", "case_sensitive": False}],
            "actions": [
                {"type": "set", "variable": "FORM_NAME", "value": "W2"},
            ],
        }

        parser = RuleParser()
        rule = parser.parse_dict(rule_data)
        processor.form_rules.append(rule)  # Add to form_rules for classification

        # Test document
        document = """
        Form W-2 Wage and Tax Statement
        Employee SSN: 123-45-6789
        """

        result = processor.process_document(document)

        assert result is not None
        assert result["rule_id"] == "W2"
        assert result["local_variables"]["FORM_NAME"] == "W2"

    def test_process_document_with_global_and_form_rules(self):
        """Test processing with both global extraction and form classification."""
        processor = NominalProcessor()
        parser = RuleParser()

        # Create a global rule for variable extraction
        global_rule_data = {
            "rule_id": "ssn-extractor",
            "description": "Extract SSN",
            "criteria": [{"type": "regex", "pattern": "."}],  # Match any document
            "actions": [
                {
                    "type": "regex_extract",
                    "variable": "TIN_LAST_FOUR",
                    "from_text": True,
                    "pattern": r"\b\d{3}-\d{2}-(\d{4})\b",
                    "group": 1,
                },
            ],
        }
        global_rule = parser.parse_dict(global_rule_data)
        processor.global_rules.append(global_rule)

        # Create a form rule for classification
        form_rule_data = {
            "rule_id": "W2",
            "description": "Test W2",
            "criteria": [{"type": "contains", "value": "form w-2", "case_sensitive": False}],
            "actions": [{"type": "set", "variable": "FORM_NAME", "value": "W2"}],
        }
        form_rule = parser.parse_dict(form_rule_data)
        processor.form_rules.append(form_rule)

        # Test document
        document = """
        Form W-2 Wage and Tax Statement
        Employee SSN: 123-45-6789
        """

        result = processor.process_document(document)

        assert result is not None
        assert result["rule_id"] == "W2"
        assert result["local_variables"]["FORM_NAME"] == "W2"
        assert result["global_variables"]["TIN_LAST_FOUR"] == "6789"

    def test_process_document_no_match(self):
        """Test processing a document that doesn't match any form rule."""
        processor = NominalProcessor()

        # Create a rule
        rule_data = {
            "rule_id": "W2",
            "description": "Test W2",
            "criteria": [{"type": "contains", "value": "form w-2", "case_sensitive": False}],
            "actions": [],
        }

        parser = RuleParser()
        rule = parser.parse_dict(rule_data)
        processor.form_rules.append(rule)

        # Test document that doesn't match
        document = "This is not a W2 form"

        result = processor.process_document(document)

        assert result is None
        # Check that unmatched document was logged
        assert len(processor.unmatched_documents) == 1

    def test_load_rule_file(self):
        """Test loading a rule from a YAML file."""
        # Create a temporary rule file
        rule_content = """
rule_id: TEST
description: Test form
criteria:
  - type: contains
    value: test
actions:
  - type: set
    variable: TEST_VAR
    value: test_value
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(rule_content)
            temp_path = f.name

        try:
            processor = NominalProcessor()
            processor.load_rule(temp_path, rule_type="form")

            assert len(processor.form_rules) == 1
            assert processor.form_rules[0].rule_id == "TEST"
        finally:
            os.unlink(temp_path)

    def test_load_global_rule_file(self):
        """Test loading a global rule from a YAML file."""
        rule_content = """
rule_id: test-global
description: Test global rule
criteria:
  - type: regex
    pattern: '.'
actions:
  - type: regex_extract
    variable: TEST_VAR
    from_text: true
    pattern: '([A-Z]+)'
    group: 1
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(rule_content)
            temp_path = f.name

        try:
            processor = NominalProcessor()
            processor.load_rule(temp_path, rule_type="global")

            assert len(processor.global_rules) == 1
            assert processor.global_rules[0].rule_id == "test-global"
        finally:
            os.unlink(temp_path)
