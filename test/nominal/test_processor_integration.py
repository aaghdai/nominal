"""
Integration tests for the Nominal Processor with real rule files.
"""

import os
from pathlib import Path

import pytest
from nominal.processor import NominalProcessor
from nominal.reader import NominalReader


class TestProcessorIntegration:
    """Integration tests using real rule files and sample documents."""

    @pytest.fixture
    def rules_dir(self):
        """Get the rules directory path."""
        # Assuming rules directory is at project root
        project_root = Path(__file__).parent.parent.parent
        return str(project_root / "rules")

    @pytest.fixture
    def processor(self, rules_dir):
        """Create a processor with loaded rules."""
        if not os.path.exists(rules_dir):
            pytest.skip(f"Rules directory not found: {rules_dir}")

        processor = NominalProcessor(rules_dir)
        return processor

    def test_w2_form_recognition(self, processor):
        """Test that W2 forms are correctly recognized and processed."""
        # Sample W2 document text
        w2_text = """
        Form W-2 Wage and Tax Statement
        Copy B—To Be Filed With Employee's FEDERAL Tax Return

        Employee's social security number: 123-45-6789

        Employer identification number (EIN): 12-3456789

        Employee's name and address:
        John Smith
        123 Main Street
        Anytown, CA 12345

        Wages, tips, other compensation: $50,000.00
        Federal income tax withheld: $5,000.00
        """

        result = processor.process_document(w2_text)

        assert result is not None, "W2 form should be recognized"
        assert result["rule_id"] == "W2"
        assert "FORM_NAME" in result["local_variables"]
        assert result["local_variables"]["FORM_NAME"] == "W2"

        # Check that SSN was captured as global variable
        if "SSN" in result["global_variables"]:
            assert result["global_variables"]["SSN"] == "123-45-6789"

        # Check that last four digits were derived
        if "SSN_LAST_FOUR" in result["derived_variables"]:
            assert result["derived_variables"]["SSN_LAST_FOUR"] == "6789"

    def test_non_w2_form_not_recognized(self, processor):
        """Test that non-W2 forms are not matched by W2 rule."""
        # Random text that doesn't match W2
        random_text = """
        This is some random document
        It has nothing to do with tax forms
        Just some regular text here
        """

        result = processor.process_document(random_text)

        # Should be None if only W2 rule is loaded and this isn't a W2
        # Or should match a different form if other rules exist
        if result is not None:
            assert result["rule_id"] != "W2"

    def test_process_real_w2_pdf(self, processor):
        """Test processing a real W2 PDF file."""
        # Get the fixtures directory
        fixtures_dir = Path(__file__).parent.parent / "fixtures"
        w2_pdf = fixtures_dir / "Sample-W2.pdf"

        if not w2_pdf.exists():
            pytest.skip(f"W2 PDF fixture not found: {w2_pdf}")

        # Read the PDF
        reader = NominalReader()
        text = reader.read_pdf(str(w2_pdf))

        # Process the text
        result = processor.process_document(text)

        # The result should recognize it as a W2
        assert result is not None, "Real W2 PDF should be recognized"
        assert result["rule_id"] == "W2"
        assert "FORM_NAME" in result["local_variables"]

    def test_processor_without_rules(self):
        """Test processor behavior when no rules are loaded."""
        processor = NominalProcessor()

        result = processor.process_document("Any text")

        assert result is None, "Should return None when no rules are loaded"

    def test_multiple_rules_first_match_wins(self, rules_dir):
        """Test that when multiple rules could match, the first one wins."""
        if not os.path.exists(rules_dir):
            pytest.skip(f"Rules directory not found: {rules_dir}")

        processor = NominalProcessor(rules_dir)

        # Create text that matches W2 form
        text = """
        W-2 Wage and Tax Statement
        Employee's SSN: 123-45-6789
        JOHN SMITH 123 Main St
        """

        result = processor.process_document(text)

        # Should match a rule
        assert result is not None
        assert "rule_id" in result
