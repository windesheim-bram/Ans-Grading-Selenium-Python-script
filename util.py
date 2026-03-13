# util.py

import re
import pandas as pd
from typing import Any, Optional


_NBSP = "\u00A0"  # Non-breaking space.
_ZWSP = "\u200b"  # Zero-width space.
_BOM = "\ufeff"   # Byte order mark.


def _to_clean_str(value: Any) -> str:
    """Convert to string and remove common invisible chars; normalize NBSP."""
    s = str(value)
    s = s.replace(_NBSP, " ")
    s = s.replace(_ZWSP, "").replace(_BOM, "")

    return s


def normalize_column_name(value: Any) -> str:    
    """
    For Excel header names and column names in config:
    - lowercase
    - remove ALL whitespace
    """
    s = _to_clean_str(value).casefold()
    s = "".join(ch for ch in s if not ch.isspace())

    return s


def normalize_value(value: Any) -> Optional[str]:
    """
    For cell values:
    - returns None for empty/NaN
    - always returns a string otherwise
    - converts integer-like numbers (1.0) to "1"
    - trims and removes invisibles
    """
    if value is None:
        return None
    
    if isinstance(value, float) and pd.isna(value):
        return None

    # Numeric normalization.
    if isinstance(value, (int, float)):

        # 1.0 -> "1", 2.5 -> "2.5".
        if isinstance(value, float) and value.is_integer():
            return str(int(value))
        
        return str(value).strip()

    s = _to_clean_str(value).strip()

    # If it looks like "1111111.0" as a string -> "1111111".
    if re.fullmatch(r"\d+(\.0+)?", s):
        return str(int(float(s)))

    return s


def normalize_value_student_number(value: Any) -> Optional[str]:
    """
    For student number cell values:
    - normalize_value first
    - lowercase
    - remove ONE leading 's'
    """
    s = normalize_value(value)

    if not s:
        return None

    s = _to_clean_str(s).strip().casefold()
    s = re.sub(r"^s", "", s, count=1)
    
    return s
