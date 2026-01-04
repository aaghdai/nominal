import unittest
from unittest.mock import MagicMock, patch

from nominal.reader import NominalReader


class TestNominalReader(unittest.TestCase):
    @patch("nominal.reader.fitz.open")
    @patch("nominal.reader.os.path.exists")
    def test_read_pdf_text_extraction(self, mock_exists, mock_fitz_open):
        # Setup
        mock_exists.return_value = True

        # Mock PDF document and page
        mock_doc = MagicMock()
        mock_page = MagicMock()
        mock_page.get_text.return_value = "Sample PDF content."

        # Make the doc iterable yielding the page
        mock_doc.__iter__.return_value = [mock_page]
        mock_fitz_open.return_value = mock_doc

        reader = NominalReader(ocr_fallback=False)
        content = reader.read_pdf("dummy.pdf")

        self.assertIn("Sample PDF content.", content)
        mock_fitz_open.assert_called_with("dummy.pdf")

    @patch("nominal.reader.pytesseract.image_to_string")
    @patch("nominal.reader.Image.open")
    @patch("nominal.reader.fitz.open")
    @patch("nominal.reader.os.path.exists")
    def test_read_pdf_ocr_fallback(self, mock_exists, mock_fitz_open, mock_image_open, mock_ocr):
        # Setup
        mock_exists.return_value = True

        # Mock PDF document and page with empty text
        mock_doc = MagicMock()
        mock_page = MagicMock()
        mock_page.get_text.return_value = "   "  # Empty/whitespace text

        # Mock pixmap for OCR
        mock_pix = MagicMock()
        mock_pix.tobytes.return_value = b"fake_image_data"
        mock_page.get_pixmap.return_value = mock_pix

        mock_doc.__iter__.return_value = [mock_page]
        mock_fitz_open.return_value = mock_doc

        # Mock OCR result
        mock_ocr.return_value = "OCR Content"

        reader = NominalReader(ocr_fallback=True)
        content = reader.read_pdf("scan.pdf")

        self.assertIn("OCR Content", content)
        mock_ocr.assert_called()

    def test_file_not_found(self):
        reader = NominalReader()
        with self.assertRaises(FileNotFoundError):
            reader.read_pdf("non_existent.pdf")


if __name__ == "__main__":
    unittest.main()
