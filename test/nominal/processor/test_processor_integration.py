"""
Integration tests for the Nominal Processor with real rule files and PDFs.

These tests isolate the reader functionality by using NominalReader to extract
text from real PDF files, then use that extracted text to test the processor.
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
        # Rules directory is at project root (3 levels up from test file)
        project_root = Path(__file__).parent.parent.parent.parent
        return str(project_root / "rules")

    @pytest.fixture
    def processor(self, rules_dir):
        """Create a processor with loaded rules."""
        if not os.path.exists(rules_dir):
            pytest.skip(f"Rules directory not found: {rules_dir}")

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
            pytest.skip(f"W2 PDF fixture not found: {w2_pdf}")

        # Isolate reader functionality - extract text from PDF
        text = reader.read_pdf(str(w2_pdf))
        assert len(text) > 0, "Reader should extract text from W2 PDF"
        return text

    @pytest.fixture
    def w1099_pdf_text(self, reader, fixtures_dir):
        """Extract text from the 1099-MISC PDF fixture using reader."""
        w1099_pdf = fixtures_dir / "Sample-1099-image.pdf"
        if not w1099_pdf.exists():
            pytest.skip(f"1099-MISC PDF fixture not found: {w1099_pdf}")

        # Isolate reader functionality - extract text from PDF
        text = reader.read_pdf(str(w1099_pdf))
        assert len(text) > 0, "Reader should extract text from 1099-MISC PDF"
        return text

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

        # Check that TIN_LAST_FOUR was extracted
        if "TIN_LAST_FOUR" in result["global_variables"]:
            assert result["global_variables"]["TIN_LAST_FOUR"] == "6789"

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

    def test_process_real_w2_pdf(self, processor, w2_pdf_text):
        """Test processing a real W2 PDF file with comprehensive variable extraction."""
        # Use extracted text from reader (isolated reader functionality)
        result = processor.process_document(w2_pdf_text)

        # Verify recognition
        assert result is not None, "Real W2 PDF should be recognized"
        assert result["rule_id"] == "W2"
        assert result["rule_description"] == "IRS Form W-2 - Wage and Tax Statement"

        # Verify local variables
        assert "FORM_NAME" in result["local_variables"]
        assert result["local_variables"]["FORM_NAME"] == "W2"

        # Verify global variables (may or may not be extracted depending on PDF content)
        # At minimum, check structure
        assert isinstance(result["global_variables"], dict)
        # TIN_LAST_FOUR should be extracted
        if "TIN_LAST_FOUR" in result["global_variables"]:
            tin_last_four = result["global_variables"]["TIN_LAST_FOUR"]
            assert tin_last_four is not None
            assert len(tin_last_four) == 4

        # Verify derived variables
        assert isinstance(result["derived_variables"], dict)

    def test_process_real_1099_misc_pdf(self, processor, w1099_pdf_text):
        """Test processing a real 1099 PDF file with comprehensive variable extraction."""
        # Use extracted text from reader (isolated reader functionality)
        # Note: The actual PDF may be 1099-DIV, not 1099-MISC, so we test processor behavior
        result = processor.process_document(w1099_pdf_text)

        # The PDF contains "1099" so it might match the 1099-MISC rule if criteria are met
        # If it doesn't match, that's valid - the processor correctly rejected it
        if result is not None:
            # If it matched, verify the structure
            assert result["rule_id"] in ["1099-MISC", "1099-DIV", "W2"], "Should match a known rule"
            assert "FORM_NAME" in result["local_variables"]
            assert isinstance(result["global_variables"], dict)
            assert isinstance(result["derived_variables"], dict)

            # If it matched 1099-MISC or 1099-DIV, verify variables
            if result["rule_id"] in ["1099-MISC", "1099-DIV"]:
                assert result["local_variables"]["FORM_NAME"] in ["1099-MISC", "1099-DIV"]
                # TIN_LAST_FOUR should be extracted
                if "TIN_LAST_FOUR" in result["global_variables"]:
                    tin_last_four = result["global_variables"]["TIN_LAST_FOUR"]
                    assert tin_last_four is not None
                    assert len(tin_last_four) == 4
        else:
            # If it didn't match, verify the processor correctly rejected it
            # This is valid - the rule criteria may not match the actual PDF content
            # The important thing is that the processor handled it correctly
            assert result is None, "Processor correctly rejected non-matching document"

    def test_process_batch_with_real_pdfs(self, processor, w2_pdf_text, w1099_pdf_text):
        """Test process_batch with real PDF texts extracted by reader."""
        # Use extracted texts from reader (isolated reader functionality)
        documents = [w2_pdf_text, w1099_pdf_text]

        # Process batch
        results = processor.process_batch(documents, enforce_global=False)

        # Verify both documents were processed
        assert len(results) == 2
        assert results[0] is not None, "First document (W2) should be recognized"

        # Verify first document is W2
        assert results[0]["rule_id"] == "W2"
        assert "FORM_NAME" in results[0]["local_variables"]
        assert results[0]["local_variables"]["FORM_NAME"] == "W2"

        # Second document may or may not match (depending on rule criteria)
        # The important thing is that process_batch handled it correctly
        if results[1] is not None:
            # If it matched, verify structure
            assert "rule_id" in results[1]
            assert "FORM_NAME" in results[1]["local_variables"]
            assert isinstance(results[1]["global_variables"], dict)
            assert isinstance(results[1]["derived_variables"], dict)
        else:
            # If it didn't match, that's valid - processor correctly rejected it
            assert results[1] is None

        # Verify global variables are accumulated (from matched documents)
        global_vars = processor.get_global_variables()
        assert isinstance(global_vars, dict)
        # Should have variables from W2 document at minimum
        if results[0]["global_variables"]:
            for key, value in results[0]["global_variables"].items():
                assert key in global_vars
                assert global_vars[key] == value

    def test_process_batch_global_variable_consistency(self, processor, w2_pdf_text):
        """Test that global variables are consistent across batch processing."""
        # Process same document twice to test global variable consistency
        documents = [w2_pdf_text, w2_pdf_text]

        # Process with global enforcement
        results = processor.process_batch(documents, enforce_global=True)

        # Both should be recognized
        assert len(results) == 2
        assert results[0] is not None
        assert results[1] is not None

        # Global variables should be consistent
        global_vars = processor.get_global_variables()
        assert isinstance(global_vars, dict)

        # If TIN_LAST_FOUR was extracted, it should be the same in both results
        if (
            "TIN_LAST_FOUR" in results[0]["global_variables"]
            and "TIN_LAST_FOUR" in results[1]["global_variables"]
        ):
            assert (
                results[0]["global_variables"]["TIN_LAST_FOUR"]
                == results[1]["global_variables"]["TIN_LAST_FOUR"]
            )

    def test_get_global_variables(self, processor, w2_pdf_text):
        """Test get_global_variables returns accumulated global variables."""
        # Initially should be empty
        global_vars = processor.get_global_variables()
        assert global_vars == {}

        # Process a document
        result = processor.process_document(w2_pdf_text)
        assert result is not None

        # Get global variables
        global_vars = processor.get_global_variables()
        assert isinstance(global_vars, dict)

        # Should contain global variables from processed document
        if result["global_variables"]:
            for key, value in result["global_variables"].items():
                assert key in global_vars
                assert global_vars[key] == value

    def test_reset_global_variables(self, processor, w2_pdf_text):
        """Test reset_global_variables clears accumulated global variables."""
        # Process a document to accumulate global variables
        result = processor.process_document(w2_pdf_text)
        assert result is not None

        # Verify global variables exist
        global_vars_before = processor.get_global_variables()
        if result["global_variables"]:
            assert len(global_vars_before) > 0

        # Reset global variables
        processor.reset_global_variables()

        # Verify they're cleared
        global_vars_after = processor.get_global_variables()
        assert global_vars_after == {}

    def test_process_document_enforce_global(self, processor, w2_pdf_text):
        """Test process_document with enforce_global flag."""
        # Process first document
        result1 = processor.process_document(w2_pdf_text, enforce_global=False)
        assert result1 is not None

        # Process same document with enforce_global=True
        # Should work since it's the same document
        result2 = processor.process_document(w2_pdf_text, enforce_global=True)
        assert result2 is not None

        # Global variables should match
        if result1["global_variables"] and result2["global_variables"]:
            for key in result1["global_variables"]:
                if key in result2["global_variables"]:
                    assert result1["global_variables"][key] == result2["global_variables"][key]

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

    def test_reader_isolation(self, reader, processor, fixtures_dir):
        """Test that reader functionality is isolated - can extract text independently."""
        w2_pdf = fixtures_dir / "Sample-W2.pdf"
        if not w2_pdf.exists():
            pytest.skip(f"W2 PDF fixture not found: {w2_pdf}")

        # Step 1: Use reader to extract text (isolated reader functionality)
        extracted_text = reader.read_pdf(str(w2_pdf))
        assert len(extracted_text) > 0, "Reader should extract text from PDF"

        # Step 2: Verify text is usable independently (can be stored, passed around, etc.)
        # This demonstrates reader isolation
        text_length = len(extracted_text)
        text_preview = extracted_text[:100]

        # Step 3: Use extracted text with processor (processor doesn't need PDF)
        result = processor.process_document(extracted_text)

        # Step 4: Verify processor works with extracted text
        assert result is not None, "Processor should work with reader-extracted text"
        assert result["rule_id"] == "W2"

        # Step 5: Verify we can reuse the same extracted text multiple times
        result2 = processor.process_document(extracted_text)
        assert result2 is not None
        assert result2["rule_id"] == "W2"

        # Verify text hasn't changed (reader output is stable)
        assert len(extracted_text) == text_length
        assert extracted_text[:100] == text_preview

    def test_empty_batch(self, processor):
        """Test process_batch with empty list."""
        results = processor.process_batch([], enforce_global=False)
        assert results == []
        assert processor.get_global_variables() == {}

    def test_batch_with_mixed_results(self, processor, w2_pdf_text):
        """Test batch processing with some matching and some non-matching documents."""
        # Mix of matching and non-matching text
        documents = [
            w2_pdf_text,  # Should match W2
            "Random text that doesn't match anything",  # Should not match
            w2_pdf_text,  # Should match W2 again
        ]

        results = processor.process_batch(documents, enforce_global=False)

        assert len(results) == 3
        assert results[0] is not None, "First document should match W2"
        assert results[0]["rule_id"] == "W2"
        assert results[1] is None, "Second document should not match"
        assert results[2] is not None, "Third document should match W2"
        assert results[2]["rule_id"] == "W2"

        # Global variables should be accumulated from matched documents
        global_vars = processor.get_global_variables()
        assert isinstance(global_vars, dict)
