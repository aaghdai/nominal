"""
Unit tests for the Nominal Processor.
"""

import os
import tempfile

from nominal.processor import NominalProcessor
from nominal.rules import RuleParser


class TestNominalProcessor:
    """Tests for NominalProcessor."""

    def test_process_document_with_rule(self):
        """Test processing a document with a loaded rule."""
        processor = NominalProcessor()

        # Create a rule
        rule_data = {
            "form_name": "W2",
            "description": "Test W2",
            "variables": {
                "global": ["TIN_LAST_FOUR"],
                "local": ["FORM_NAME"],
            },
            "criteria": [{"type": "contains", "value": "form w-2", "case_sensitive": False}],
            "actions": [
                {"type": "set", "variable": "FORM_NAME", "value": "W2"},
                {
                    "type": "regex_extract",
                    "variable": "TIN_LAST_FOUR",
                    "from_text": True,
                    "pattern": r"\b\d{3}-\d{2}-(\d{4})\b",
                    "group": 1,
                },
            ],
        }

        parser = RuleParser()
        rule = parser.parse_dict(rule_data)
        processor.rules.append(rule)

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
        """Test processing a document that doesn't match any rule."""
        processor = NominalProcessor()

        # Create a rule
        rule_data = {
            "form_name": "W2",
            "description": "Test W2",
            "variables": {"global": [], "local": [], "derived": []},
            "criteria": [{"type": "contains", "value": "form w-2", "case_sensitive": False}],
            "actions": [],
        }

        parser = RuleParser()
        rule = parser.parse_dict(rule_data)
        processor.rules.append(rule)

        # Test document that doesn't match
        document = "This is not a W2 form"

        result = processor.process_document(document)

        assert result is None

    def test_load_rule_file(self):
        """Test loading a rule from a YAML file."""
        # Create a temporary rule file
        rule_content = """
form_name: TEST
description: Test form
variables:
  global: []
  local: []
  derived: []
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
            processor.load_rule(temp_path)

            assert len(processor.rules) == 1
            assert processor.rules[0].rule_id == "TEST"
        finally:
            os.unlink(temp_path)
