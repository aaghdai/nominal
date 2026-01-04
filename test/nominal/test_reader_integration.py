import os
import sys
import unittest

# Add src to sys.path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

from nominal.reader import NominalReader  # noqa: E402


class TestNominalReaderIntegration(unittest.TestCase):
    def setUp(self):
        self.fixtures_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../fixtures"))
        self.w2_path = os.path.join(self.fixtures_dir, "Sample-W2.pdf")
        self.image_1099_path = os.path.join(self.fixtures_dir, "Sample-1099-image.pdf")

    def test_read_text_pdf(self):
        """Test reading a standard text-based PDF."""
        reader = NominalReader(ocr_fallback=False)
        content = reader.read_pdf(self.w2_path)

        # Verify some expected content from a W2
        # Note: We might need to adjust these assertions based on the actual
        # content of Sample-W2.pdf
        self.assertTrue(len(content) > 0, "Content should not be empty")
        content = content.lower()
        # Common W2 keywords
        self.assertTrue(
            "w-2" in content or "wage and tax statement" in content,
            f"Expected W-2 content, got: {content[:100]}...",
        )
        self.assertTrue("elizabeth" in content)
        self.assertTrue("darling" in content)

    def test_read_image_pdf_with_ocr(self):
        """Test reading an image-based PDF using OCR."""
        # Ensure Tesseract is available in the environment for this test to pass
        # If not, we might skip or warn
        try:
            import pytesseract

            pytesseract.get_tesseract_version()
        except Exception:
            self.skipTest("Tesseract not installed or not found in path")

        reader = NominalReader(ocr_fallback=True)
        content = reader.read_pdf(self.image_1099_path).lower()

        self.assertTrue(len(content) > 0, "Content should not be empty")
        # Common 1099 keywords
        self.assertTrue("1099" in content, f"Expected 1099 content, got: {content[:100]}...")
        self.assertTrue("michael" in content)
        self.assertTrue("jordan" in content)


if __name__ == "__main__":
    unittest.main()
