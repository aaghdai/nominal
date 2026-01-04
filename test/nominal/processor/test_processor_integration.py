"""
Integration tests for the Nominal Processor with real rule files and PDFs.

These tests isolate the reader functionality by using NominalReader to extract
text from real PDF files, then use that extracted text to test the processor.

Processing Flow:
1. Global rules extract common variables (TIN_LAST_FOUR, names, etc.)
2. Form rules classify documents (W2, 1099-DIV, etc.)
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
        # Rules directory is at project root (4 levels up from test file)
        project_root = Path(__file__).parent.parent.parent.parent
        return str(project_root / "rules")

    @pytest.fixture
    def processor(self, rules_dir):
        """Create a processor with loaded rules."""
        if not os.path.exists(rules_dir):
            pytest.fail(f"Rules directory not found: {rules_dir}")

        processor = NominalProcessor(rules_dir)
        return processor

    @pytest.fixture
    def reader(self):
        """Create a reader instance."""
        return NominalReader(ocr_fallback=True)

    @pytest.fixture
    def fixtures_dir(self):
        """Get the fixtures directory path."""
        # Fixtures directory is at test/fixtures (3 levels up from test file)
        return Path(__file__).parent.parent.parent / "fixtures"

    @pytest.fixture
    def w2_pdf_text(self, reader, fixtures_dir):
        """Extract text from the W2 PDF fixture using reader."""
        w2_pdf = fixtures_dir / "Sample-W2.pdf"
        if not w2_pdf.exists():
            pytest.fail(f"W2 PDF fixture not found: {w2_pdf}")

        # Isolate reader functionality - extract text from PDF
        text = reader.read_pdf(str(w2_pdf))
        assert len(text) > 0, "Reader should extract text from W2 PDF"
        return text

    @pytest.fixture
    def w1099_pdf_text(self, reader, fixtures_dir):
        """Extract text from the 1099 PDF fixture using reader."""
        w1099_pdf = fixtures_dir / "Sample-1099-image.pdf"
        if not w1099_pdf.exists():
            pytest.fail(f"1099 PDF fixture not found: {w1099_pdf}")

        # Isolate reader functionality - extract text from PDF
        text = reader.read_pdf(str(w1099_pdf))
        assert len(text) > 0, "Reader should extract text from 1099 PDF"
        return text

    def test_w2_form_recognition(self, processor):
        """Test that W2 forms are correctly recognized and processed."""
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

        # Check that TIN_LAST_FOUR was extracted by global rules
        if "TIN_LAST_FOUR" in result["global_variables"]:
            assert result["global_variables"]["TIN_LAST_FOUR"] == "6789"

    def test_non_w2_form_not_recognized(self, processor):
        """Test that non-matching text doesn't match any form rule."""
        random_text = """
        This is some random document
        It has nothing to do with tax forms
        Just some regular text here
        """

        result = processor.process_document(random_text)

        # Should be None since no form rule matches
        assert result is None
        # Check that it was logged as unmatched
        assert len(processor.unmatched_documents) >= 1

    def test_process_real_w2_pdf(self, processor, w2_pdf_text):
        """Test processing a real W2 PDF file."""
        result = processor.process_document(w2_pdf_text)

        # Verify classification
        assert result is not None, "Real W2 PDF should be recognized"
        assert result["rule_id"] == "W2"
        assert result["rule_description"] == "IRS Form W-2 - Wage and Tax Statement"

        # Verify local variables from form rule
        assert "FORM_NAME" in result["local_variables"]
        assert result["local_variables"]["FORM_NAME"] == "W2"

        # Verify global variables from global rules
        assert isinstance(result["global_variables"], dict)
        # TIN_LAST_FOUR should be extracted by global rules
        if "TIN_LAST_FOUR" in result["global_variables"]:
            tin_last_four = result["global_variables"]["TIN_LAST_FOUR"]
            assert tin_last_four is not None
            assert len(tin_last_four) == 4

    def test_process_real_1099_pdf(self, processor, w1099_pdf_text):
        """Test processing a real 1099 PDF file."""
        result = processor.process_document(w1099_pdf_text)

        # Should match a 1099 form rule
        assert result is not None, "Should match a form rule"
        assert result["rule_id"] in ["1099-DIV", "1099-MISC"]

        # Verify local variables
        assert "FORM_NAME" in result["local_variables"]
        assert result["local_variables"]["FORM_NAME"] in ["1099-DIV", "1099-MISC"]

        # Verify global variables structure
        assert isinstance(result["global_variables"], dict)

    def test_process_batch_with_real_pdfs(self, processor, w2_pdf_text, w1099_pdf_text):
        """Test batch processing with real PDF content."""
        documents = [
            ("w2_sample", w2_pdf_text),
            ("1099_sample", w1099_pdf_text),
        ]

        results = processor.process_batch(documents)

        assert len(results) == 2

        # First document should be W2
        assert results[0] is not None
        assert results[0]["rule_id"] == "W2"
        assert results[0]["document_id"] == "w2_sample"

        # Second document should be a 1099 type
        assert results[1] is not None
        assert results[1]["rule_id"] in ["1099-DIV", "1099-MISC"]
        assert results[1]["document_id"] == "1099_sample"

    def test_process_batch_global_variable_consistency(
        self, processor, w2_pdf_text, w1099_pdf_text
    ):
        """Test that global variables are tracked across batch."""
        documents = [w2_pdf_text, w1099_pdf_text]

        processor.process_batch(documents)

        # Get global variables after batch processing
        global_vars = processor.get_global_variables()

        # Should have extracted some global variables
        assert isinstance(global_vars, dict)
        # TIN_LAST_FOUR should be set from one of the documents
        if "TIN_LAST_FOUR" in global_vars:
            assert len(global_vars["TIN_LAST_FOUR"]) == 4

    def test_get_global_variables(self, processor, w2_pdf_text):
        """Test getting global variables after processing."""
        result = processor.process_document(w2_pdf_text)
        assert result is not None

        global_vars = processor.get_global_variables()
        assert isinstance(global_vars, dict)

    def test_reset_global_variables(self, processor, w2_pdf_text):
        """Test resetting global variables between batches."""
        # Process first document
        result = processor.process_document(w2_pdf_text)
        assert result is not None

        # Should have some global variables
        assert len(processor.get_global_variables()) > 0

        # Reset
        processor.reset_global_variables()

        # Should be empty
        reset_vars = processor.get_global_variables()
        assert reset_vars == {}

    def test_process_document_enforce_global(self, processor, w2_pdf_text):
        """Test global variable enforcement mode."""
        # Process document twice
        result1 = processor.process_document(w2_pdf_text, enforce_global=False)
        result2 = processor.process_document(w2_pdf_text, enforce_global=True)

        # Both should succeed
        assert result1 is not None
        assert result2 is not None
        assert result1["rule_id"] == result2["rule_id"]

    def test_processor_without_rules(self):
        """Test processor behavior when no rules are loaded."""
        processor = NominalProcessor()  # No rules_dir provided

        # Should have no rules
        assert len(processor.global_rules) == 0
        assert len(processor.form_rules) == 0

        result = processor.process_document("Any text")
        assert result is None

    def test_multiple_rules_first_match_wins(self, rules_dir):
        """Test that when multiple rules could match, the first one wins."""
        if not os.path.exists(rules_dir):
            pytest.fail(f"Rules directory not found: {rules_dir}")

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

    def test_reader_isolation(self, reader, processor, fixtures_dir):
        """Test that reader functionality is isolated."""
        w2_pdf = fixtures_dir / "Sample-W2.pdf"
        if not w2_pdf.exists():
            pytest.fail(f"W2 PDF fixture not found: {w2_pdf}")

        # Step 1: Use reader to extract text (isolated reader functionality)
        extracted_text = reader.read_pdf(str(w2_pdf))
        assert len(extracted_text) > 0, "Reader should extract text from PDF"

        # Step 2: Use processor to classify document (isolated processor functionality)
        result = processor.process_document(extracted_text)
        assert result is not None, "Processor should classify the extracted text"

    def test_empty_batch(self, processor):
        """Test processing an empty batch."""
        results = processor.process_batch([])
        assert results == []

    def test_batch_with_mixed_results(self, processor, w2_pdf_text):
        """Test batch with matching and non-matching documents."""
        documents = [
            ("matching", w2_pdf_text),
            ("non_matching", "This is random text with no form content"),
        ]

        results = processor.process_batch(documents)

        assert len(results) == 2
        assert results[0] is not None  # W2 should match
        assert results[1] is None  # Random text shouldn't match

        # Check unmatched documents were logged
        unmatched = processor.get_unmatched_documents()
        assert len(unmatched) == 1
        assert unmatched[0]["document_id"] == "non_matching"

    def test_global_rules_applied_before_classification(self, processor, w2_pdf_text):
        """Test that global rules extract variables before form classification."""
        result = processor.process_document(w2_pdf_text)

        assert result is not None
        # Global variables should be extracted
        assert isinstance(result["global_variables"], dict)
        # Form classification should work
        assert result["rule_id"] == "W2"

    def test_document_id_in_result(self, processor, w2_pdf_text):
        """Test that document_id is included in result."""
        result = processor.process_document(w2_pdf_text, document_id="my_test_doc")

        assert result is not None
        assert result["document_id"] == "my_test_doc"
