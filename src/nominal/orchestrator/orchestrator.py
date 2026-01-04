"""
Nominal Orchestrator: Orchestrates the workflow of reading, processing, and renaming files.
"""

import re
import shutil
from pathlib import Path
from typing import Any, Callable, Dict, Optional

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
    4. Apply orchestrator-level derived variables
    5. Rename and move files based on extracted variables
    """

    def __init__(
        self,
        rules_dir: str,
        ocr_fallback: bool = True,
        derived_variables: Optional[Dict[str, Callable[[Dict[str, Any]], Any]]] = None,
    ):
        """
        Initialize the orchestrator.

        Args:
            rules_dir: Directory containing rule files
            ocr_fallback: Whether to use OCR if text extraction fails
            derived_variables: Optional dict of orchestrator-level derived variables.
                              Map of variable name to a function that takes all
                              extracted variables and returns the derived value.
        """
        self.reader = NominalReader(ocr_fallback=ocr_fallback)
        self.processor = NominalProcessor(rules_dir)
        self.orchestrator_derived_vars = derived_variables or {}
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
        # 1. Validate filename pattern against declared variables
        self._validate_pattern(filename_pattern)

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

    def _validate_pattern(self, pattern: str) -> None:
        """
        Validate that all placeholders in the pattern refer to existing variables.
        """
        placeholders = re.findall(r"\{(\w+)\}", pattern)
        declared_vars = self.processor.get_all_declared_variables()

        # Add orchestrator-level derived variables to the set of valid variables
        available_vars = declared_vars.union(set(self.orchestrator_derived_vars.keys()))

        invalid_placeholders = [p for p in placeholders if p not in available_vars]
        if invalid_placeholders:
            error_msg = (
                f"Filename pattern references undefined variables: "
                f"{', '.join(invalid_placeholders)}. "
                f"Available variables: {', '.join(sorted(available_vars))}"
            )
            logger.error(error_msg)
            raise ValueError(error_msg)

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

        # 3. Apply orchestrator-level derived variables
        self._apply_orchestrator_derivations(result)

        # 4. Rename and move file
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

    def _apply_orchestrator_derivations(self, result: dict[str, Any]) -> None:
        """
        Compute orchestrator-level derived variables.
        """
        if not self.orchestrator_derived_vars:
            return

        # Combine all existing variables for derivation
        all_vars = {
            "rule_id": result["rule_id"],
            "document_id": result.get("document_id"),
        }
        all_vars.update(result.get("global_variables", {}))
        all_vars.update(result.get("local_variables", {}))

        # Apply derivations
        for var_name, derivation_func in self.orchestrator_derived_vars.items():
            try:
                derived_val = derivation_func(all_vars)
                # Store in local_variables for now as it's document-specific
                if "local_variables" not in result:
                    result["local_variables"] = {}
                result["local_variables"][var_name] = derived_val
                logger.debug(f"Orchestrator derivation: {var_name} = '{derived_val}'")
            except Exception as e:
                logger.warning(f"Failed to derive orchestrator variable {var_name}: {e}")

    def _generate_filename(self, result: dict[str, Any], pattern: str) -> str:
        """
        Generate a new filename based on pattern and extracted variables.
        """
        # Combine all variables for pattern matching
        all_vars = {
            "rule_id": result["rule_id"],
            "document_id": result.get("document_id"),
        }
        all_vars.update(result.get("global_variables", {}))
        all_vars.update(result.get("local_variables", {}))

        # Replace missing variables with 'UNKNOWN'
        # We use a custom formatting approach to handle missing keys gracefully
        filename = pattern

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
