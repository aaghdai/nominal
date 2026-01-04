#!/usr/bin/env python3
"""
Generate name dictionaries from US Census and SSA data.

Downloads and processes:
- US Census Bureau 2010 surnames (top 50,000)
- US Social Security Administration baby names (2020-2023)

Creates:
- data/first_names.txt (40K+ unique first names)
- data/last_names.txt (50K surnames)

Usage:
    # As a CLI command (recommended)
    uv run nominal-generate-names

    # Or directly
    python scripts/generate_name_dictionaries.py
    uv run python scripts/generate_name_dictionaries.py
"""

import csv
import subprocess
import sys
import tempfile
from pathlib import Path


def download_file(url: str, output_path: Path) -> bool:
    """Download a file using wget or curl."""
    print(f"📥 Downloading {url}...")

    # Try wget first
    try:
        subprocess.run(
            ["wget", "-q", "-O", str(output_path), url],
            check=True,
            capture_output=True,
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    # Fallback to curl
    try:
        subprocess.run(
            ["curl", "-sL", "-o", str(output_path), url],
            check=True,
            capture_output=True,
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Error: Neither wget nor curl found. Please install one of them.")
        return False


def extract_zip(zip_path: Path, extract_to: Path, files: list[str] | None = None) -> bool:
    """Extract specific files from a zip archive."""
    try:
        import zipfile

        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            if files:
                for file in files:
                    try:
                        zip_ref.extract(file, extract_to)
                    except KeyError:
                        print(f"⚠️  Warning: {file} not found in archive")
            else:
                zip_ref.extractall(extract_to)
        return True
    except Exception as e:
        print(f"❌ Error extracting {zip_path}: {e}")
        return False


def generate_last_names(temp_dir: Path, output_file: Path) -> bool:
    """Generate last names dictionary from US Census data."""
    print("\n📊 Processing US Census surnames...")

    census_url = "https://www2.census.gov/topics/genealogy/2010surnames/names.zip"
    zip_path = temp_dir / "census.zip"

    if not download_file(census_url, zip_path):
        return False

    if not extract_zip(zip_path, temp_dir, ["Names_2010Census.csv"]):
        return False

    csv_path = temp_dir / "Names_2010Census.csv"
    if not csv_path.exists():
        print(f"❌ Error: Expected file {csv_path} not found after extraction")
        return False

    # Extract top 50,000 surnames
    surnames = []
    try:
        with open(csv_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                surnames.append(row["name"].strip().upper())
                if len(surnames) >= 50000:
                    break

        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n".join(surnames))
            f.write("\n")

        print(f"✅ Generated {len(surnames):,} surnames → {output_file}")
        return True

    except Exception as e:
        print(f"❌ Error processing census data: {e}")
        return False


def generate_first_names(temp_dir: Path, output_file: Path) -> bool:
    """Generate first names dictionary from SSA data."""
    print("\n📊 Processing SSA baby names...")

    ssa_url = "https://www.ssa.gov/oact/babynames/names.zip"
    zip_path = temp_dir / "ssa.zip"

    if not download_file(ssa_url, zip_path):
        return False

    # Extract only recent years (2020-2023)
    files_to_extract = [f"yob{year}.txt" for year in range(2020, 2024)]
    if not extract_zip(zip_path, temp_dir, files_to_extract):
        return False

    # Collect unique first names across all years
    first_names = set()
    years_processed = 0

    for year in range(2020, 2024):
        year_file = temp_dir / f"yob{year}.txt"
        if not year_file.exists():
            print(f"⚠️  Warning: {year_file} not found, skipping")
            continue

        try:
            with open(year_file, encoding="utf-8") as f:
                for line in f:
                    name = line.split(",")[0].strip().upper()
                    first_names.add(name)
            years_processed += 1
        except Exception as e:
            print(f"⚠️  Warning: Error processing {year_file}: {e}")

    if years_processed == 0:
        print("❌ Error: No SSA data files could be processed")
        return False

    # Write sorted first names
    try:
        sorted_names = sorted(first_names)
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n".join(sorted_names))
            f.write("\n")

        print(f"✅ Generated {len(sorted_names):,} first names → {output_file}")
        return True

    except Exception as e:
        print(f"❌ Error writing first names: {e}")
        return False


def main():
    """Main entry point."""
    print("=" * 70)
    print("Name Dictionary Generator")
    print("=" * 70)
    print()
    print("This script will download and process name data from:")
    print("  • US Census Bureau (surnames)")
    print("  • US Social Security Administration (first names)")
    print()

    # Determine project root and data directory
    # When installed as a package, __file__ is in src/nominal/scripts/
    # We need to go up to find the actual project root with data/
    script_dir = Path(__file__).parent

    # Try to find project root by looking for pyproject.toml
    current = script_dir
    project_root = None
    for _ in range(5):  # Search up to 5 levels
        if (current / "pyproject.toml").exists():
            project_root = current
            break
        current = current.parent

    # Fallback: assume we're in src/nominal/scripts, go up 3 levels
    if project_root is None:
        project_root = script_dir.parent.parent.parent

    data_dir = project_root / "data"

    # Create data directory if it doesn't exist
    data_dir.mkdir(exist_ok=True)

    output_first = data_dir / "first_names.txt"
    output_last = data_dir / "last_names.txt"

    print(f"Output directory: {data_dir}")
    print()

    # Create temporary directory for downloads
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Generate dictionaries
        success_last = generate_last_names(temp_path, output_last)
        success_first = generate_first_names(temp_path, output_first)

    # Summary
    print()
    print("=" * 70)
    if success_last and success_first:
        print("✅ SUCCESS: Name dictionaries generated successfully!")
        print()
        print("📁 Files created:")
        print(f"   • {output_first} ({output_first.stat().st_size:,} bytes)")
        print(f"   • {output_last} ({output_last.stat().st_size:,} bytes)")
        print()
        print("These files are now available for validated name extraction.")
        return 0
    else:
        print("❌ FAILED: Some dictionaries could not be generated.")
        print()
        if not success_first:
            print(f"   ✗ {output_first} - generation failed")
        if not success_last:
            print(f"   ✗ {output_last} - generation failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
