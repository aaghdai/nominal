"""Name validation utility using US Census and SSA data."""

from pathlib import Path
from typing import Optional

# Cache for loaded names
_FIRST_NAMES: Optional[set[str]] = None
_LAST_NAMES: Optional[set[str]] = None


def _load_names_from_file(filename: str) -> set[str]:
    """Load names from a text file (one name per line)."""
    data_dir = Path(__file__).parent.parent.parent.parent / "data"
    filepath = data_dir / filename

    if not filepath.exists():
        return set()

    with open(filepath, encoding="utf-8") as f:
        return {line.strip().upper() for line in f if line.strip()}


def get_first_names() -> set[str]:
    """Get the set of known first names (cached)."""
    global _FIRST_NAMES
    if _FIRST_NAMES is None:
        _FIRST_NAMES = _load_names_from_file("first_names.txt")
    return _FIRST_NAMES


def get_last_names() -> set[str]:
    """Get the set of known last names (cached)."""
    global _LAST_NAMES
    if _LAST_NAMES is None:
        _LAST_NAMES = _load_names_from_file("last_names.txt")
    return _LAST_NAMES


def is_valid_first_name(name: str) -> bool:
    """Check if a name is a known first name."""
    return name.upper() in get_first_names()


def is_valid_last_name(name: str) -> bool:
    """Check if a name is a known last name."""
    return name.upper() in get_last_names()


def validate_full_name(full_name: str) -> dict[str, any]:
    """
    Validate a full name and extract first/last name components.

    Returns a dict with:
        - is_valid: bool (whether this appears to be a valid person name)
        - first_name: str (extracted first name)
        - last_name: str (extracted last name)
        - confidence: float (0-1, confidence score)
        - reason: str (explanation of the validation result)
    """
    parts = full_name.strip().split()

    if len(parts) < 2:
        return {
            "is_valid": False,
            "first_name": "",
            "last_name": "",
            "confidence": 0.0,
            "reason": "Name must have at least 2 parts (first and last)",
        }

    # Basic strategy: first word is first name, last word is last name
    first_name = parts[0]
    last_name = parts[-1]

    # Check validity
    first_valid = is_valid_first_name(first_name)
    last_valid = is_valid_last_name(last_name)

    # Calculate confidence score
    confidence = 0.0
    reasons = []

    if first_valid:
        confidence += 0.5
        reasons.append("First name recognized")
    else:
        reasons.append("First name not in database")

    if last_valid:
        confidence += 0.5
        reasons.append("Last name recognized")
    else:
        reasons.append("Last name not in database")

    # Bonus: check for middle initial or middle name
    if len(parts) == 3:
        middle = parts[1]
        if len(middle) == 1 or (len(middle) == 2 and middle.endswith(".")):
            confidence += 0.1
            reasons.append("Has middle initial")
        elif is_valid_first_name(middle):
            confidence += 0.1
            reasons.append("Has middle name")

    # Cap confidence at 1.0
    confidence = min(confidence, 1.0)

    # Consider valid if confidence > 0.5
    is_valid = confidence > 0.5

    return {
        "is_valid": is_valid,
        "first_name": first_name,
        "last_name": last_name,
        "confidence": confidence,
        "reason": "; ".join(reasons),
    }


def score_name_candidates(candidates: list[str]) -> list[tuple[str, dict]]:
    """
    Score multiple name candidates and return them sorted by confidence.

    Args:
        candidates: List of potential full names

    Returns:
        List of tuples (name, validation_result) sorted by confidence (highest first)
    """
    scored = [(name, validate_full_name(name)) for name in candidates]
    return sorted(scored, key=lambda x: x[1]["confidence"], reverse=True)
