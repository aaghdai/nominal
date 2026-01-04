"""
End-to-end tests for the Nominal Orchestrator.
"""

import shutil
import tempfile
from pathlib import Path

import pytest
from nominal.orchestrator import NominalOrchestrator


class TestOrchestrator:
    """End-to-end tests for NominalOrchestrator."""

    @pytest.fixture
    def rules_dir(self):
        """Get the rules directory path."""
        project_root = Path(__file__).parent.parent.parent.parent
        return str(project_root / "rules")

    @pytest.fixture
    def fixtures_dir(self):
        """Get the fixtures directory path."""
        return Path(__file__).parent.parent.parent / "fixtures"

    @pytest.fixture
    def temp_dirs(self):
        """Create temporary input and output directories."""
        with tempfile.TemporaryDirectory() as input_dir:
            with tempfile.TemporaryDirectory() as output_dir:
                yield Path(input_dir), Path(output_dir)

    def test_orchestrator_e2e(self, rules_dir, fixtures_dir, temp_dirs):
        """Test the full workflow from reading to renaming."""
        input_dir, output_dir = temp_dirs

        # Copy fixtures to input directory
        w2_src = fixtures_dir / "Sample-W2.pdf"
        misc_src = fixtures_dir / "Sample-1099-image.pdf"

        if not w2_src.exists() or not misc_src.exists():
            pytest.fail("PDF fixtures not found")

        shutil.copy2(w2_src, input_dir / "w2.pdf")
        shutil.copy2(misc_src, input_dir / "1099.pdf")

        # Initialize orchestrator
        orchestrator = NominalOrchestrator(rules_dir)

        # Process directory
        pattern = "{rule_id}_{FULL_NAME}_{TIN_LAST_FOUR}"
        stats = orchestrator.process_directory(
            str(input_dir), str(output_dir), filename_pattern=pattern
        )

        # Verify stats
        assert stats["total"] == 2
        assert stats["matched"] == 2
        assert stats["unmatched"] == 0
        assert stats["errors"] == 0

        # Verify output files
        output_files = list(output_dir.glob("*.pdf"))
        assert len(output_files) == 2

        # Check for expected filenames (at least parts of them)
        filenames = [f.name for f in output_files]
        assert any("W2" in f for f in filenames)
        assert any("1099" in f for f in filenames)

    def test_orchestrator_unmatched(self, rules_dir, temp_dirs):
        """Test handling of unmatched files."""
        input_dir, output_dir = temp_dirs

        # Create a dummy PDF that won't match any rules
        # (Just an empty file with .pdf extension for scanning)
        unmatched_file = input_dir / "not_a_tax_form.pdf"
        with open(unmatched_file, "w") as f:
            f.write("This is not a PDF content, but has the extension.")

        # Initialize orchestrator
        orchestrator = NominalOrchestrator(rules_dir)

        # Process directory
        stats = orchestrator.process_directory(str(input_dir), str(output_dir))

        # Verify stats
        assert stats["total"] == 1
        # It should fail reading because it's not a valid PDF
        assert stats["matched"] == 0
        assert stats["errors"] == 1

        # Verify unmatched directory
        unmatched_dir = output_dir / "unmatched"
        assert unmatched_dir.exists()
        assert (unmatched_dir / "error_not_a_tax_form.pdf").exists()

        # Check for error log
        error_logs = list(unmatched_dir.glob("*.log"))
        assert len(error_logs) >= 1
