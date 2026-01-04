import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io
import os

class NominalReader:
    def __init__(self, ocr_fallback: bool = True, min_text_length: int = 50):
        self.ocr_fallback = ocr_fallback
        self.min_text_length = min_text_length

    def read_pdf(self, file_path: str) -> str:
        """
        Reads a PDF file and extracts text.
        If text extraction yields little result and ocr_fallback is True,
        it attempts to OCR the pages.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        text_content = []
        
        try:
            doc = fitz.open(file_path)
            
            for page_num, page in enumerate(doc):
                text = page.get_text()
                
                should_ocr = False
                
                # Condition 1: Text is very sparse
                if len(text.strip()) < self.min_text_length:
                    # Check if there are any images to OCR
                    if page.get_images():
                        should_ocr = True
                
                # Condition 2: Page contains a large image (likely a scan), even if there is some text (e.g. headers)
                if not should_ocr and self.ocr_fallback:
                    page_area = page.rect.width * page.rect.height
                    images_info = page.get_image_info()
                    for img in images_info:
                        bbox = fitz.Rect(img['bbox'])
                        img_area = bbox.width * bbox.height
                        # If an image covers more than 30% of the page, it's a candidate for OCR
                        if img_area > (page_area * 0.3):
                            should_ocr = True
                            break

                if self.ocr_fallback and should_ocr:
                    ocr_text = self._ocr_page(page)
                    # If OCR provides significantly more text, use it
                    # We use a factor of 1.2 to ensure the OCR adds value over the existing text
                    if len(ocr_text.strip()) > len(text.strip()) * 1.2:
                        text = ocr_text
                
                text_content.append(text)
                
            doc.close()
        except Exception as e:
            raise RuntimeError(f"Failed to read PDF: {e}")

        return "\n".join(text_content)

    def _ocr_page(self, page) -> str:
        """
        Renders a PDF page to an image and performs OCR.
        """
        # Render page to an image (pixmap)
        # matrix=fitz.Matrix(2, 2) increases resolution for better OCR (approx 144 DPI -> 288 DPI)
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
        
        # Convert to PIL Image
        img_data = pix.tobytes("png")
        image = Image.open(io.BytesIO(img_data))
        
        # Perform OCR
        text = pytesseract.image_to_string(image)
        return text
