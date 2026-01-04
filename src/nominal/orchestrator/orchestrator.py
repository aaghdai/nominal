"""
Nominal Orchestrator: Orchestrates the workflow of reading, processing, and renaming files.
"""

import shutil
from pathlib import Path
from typing import Any

from nominal.logging import setup_logger
from nominal.processor import NominalProcessor
from nominal.reader import NominalReader

logger = setup_logger()


class NominalOrchestrator:
    """
    Orchestrates the workflow:
    1. Scan directory for PDF files
    2. Read files using NominalReader
    3. Process text using NominalProcessor
    4. Rename and move files based on extracted variables
    """

    def __init__(
        self,
        rules_dir: str,
        ocr_fallback: bool = True,
    ):
        """
        Initialize the orchestrator.

        Args:
            rules_dir: Directory containing rule files
            ocr_fallback: Whether to use OCR if text extraction fails
        """
        self.reader = NominalReader(ocr_fallback=ocr_fallback)
        self.processor = NominalProcessor(rules_dir)
        logger.info("NominalOrchestrator initialized")

    def process_directory(
        self,
        input_dir: str,
        output_dir: str,
        filename_pattern: str = "{rule_id}_{LAST_NAME}_{TIN_LAST_FOUR}",
    ) -> dict[str, Any]:
        """
        Process all PDF files in the input directory.

        Args:
            input_dir: Directory containing input PDF files
            output_dir: Directory to save renamed files
            filename_pattern: Pattern for new filenames (uses variable names in braces)

        Returns:
            Dictionary with processing summary
        """
        input_path = Path(input_dir)
        output_path = Path(output_dir)

        if not input_path.exists():
            raise FileNotFoundError(f"Input directory not found: {input_dir}")

        # Create output directory and unmatched subdirectory
        output_path.mkdir(parents=True, exist_ok=True)
        unmatched_dir = output_path / "unmatched"
        unmatched_dir.mkdir(exist_ok=True)

        pdf_files = list(input_path.glob("*.pdf"))
        logger.info(f"Found {len(pdf_files)} PDF files in {input_dir}")

        stats = {
            "total": len(pdf_files),
            "matched": 0,
            "unmatched": 0,
            "errors": 0,
        }

        for pdf_file in pdf_files:
            try:
                result = self._process_file(pdf_file, output_path, filename_pattern)
                if result:
                    stats["matched"] += 1
                else:
                    stats["unmatched"] += 1
                    # Move unmatched file to unmatched directory
                    shutil.copy2(pdf_file, unmatched_dir / pdf_file.name)
                    self._write_error_log(
                        unmatched_dir / f"{pdf_file.stem}_error.log",
                        f"Unmatched: {pdf_file.name} did not match any form rule.",
                    )
            except Exception as e:
                logger.error(f"Error processing {pdf_file.name}: {e}")
                stats["errors"] += 1
                # Copy original to unmatched/error location
                shutil.copy2(pdf_file, unmatched_dir / f"error_{pdf_file.name}")
                self._write_error_log(
                    unmatched_dir / f"error_{pdf_file.stem}_exception.log",
                    f"Exception: {str(e)}",
                )

        logger.info(
            f"Processing complete: {stats['matched']} matched, "
            f"{stats['unmatched']} unmatched, {stats['errors']} errors"
        )
        return stats

    def _write_error_log(self, log_path: Path, message: str):
        """Write an error message to a log file."""
        try:
            with open(log_path, "w") as f:
                f.write(message)
        except Exception as e:
            logger.error(f"Failed to write error log to {log_path}: {e}")

    def _process_file(
        self,
        file_path: Path,
        output_path: Path,
        filename_pattern: str,
    ) -> bool:
        """
        Process a single file: read, process, and rename.

        Returns:
            True if matched and renamed, False otherwise
        """
        logger.info(f"Processing file: {file_path.name}")

        # 1. Read text from PDF
        text = self.reader.read_pdf(str(file_path))
        if not text:
            logger.warning(f"No text extracted from {file_path.name}")
            return False

        # 2. Process text to extract variables
        result = self.processor.process_document(text, document_id=file_path.name)
        if not result:
            return False

        # 3. Rename and move file
        new_filename = self._generate_filename(result, filename_pattern)
        new_path = output_path / f"{new_filename}{file_path.suffix}"

        # Handle duplicate filenames
        if new_path.exists():
            counter = 1
            while new_path.exists():
                new_path = output_path / f"{new_filename}_{counter}{file_path.suffix}"
                counter += 1

        shutil.copy2(file_path, new_path)
        logger.info(f"✓ Renamed {file_path.name} to {new_path.name}")
        return True

    def _generate_filename(self, result: dict[str, Any], pattern: str) -> str:
        """
        Generate a new filename based on pattern and extracted variables.
        """
        # Combine all variables for pattern matching
        all_vars = {
            "rule_id": result["rule_id"],
        }
        all_vars.update(result.get("global_variables", {}))
        all_vars.update(result.get("local_variables", {}))

        # Replace missing variables with 'UNKNOWN'
        # We use a custom formatting approach to handle missing keys gracefully
        filename = pattern
        import re

        placeholders = re.findall(r"\{(\w+)\}", pattern)
        for placeholder in placeholders:
            val = all_vars.get(placeholder, "UNKNOWN")
            # Sanitize value for filename
            val = "".join(c for c in str(val) if c.isalnum() or c in ("-", "_")).strip()
            if not val:
                val = "UNKNOWN"
            filename = filename.replace(f"{{{placeholder}}}", val)

        # Final sanitization of the whole filename
        filename = filename.replace(" ", "_")
        return filename
