"""Base transformer utilities for data parsing and slicing."""
from typing import Any, List, Optional
from datetime import datetime

def parse_date(date_str: Optional[str]) -> Optional[str]:
    """Normalize date to YYYY-MM-DD if possible."""
    if not date_str:
        return None
    try:
        # Handle various formats; adjust as needed
        return datetime.strptime(date_str, "%Y-%m-%d").date().isoformat()
    except ValueError:
        # If already ISO or unknown, return as-is
        return date_str

def slice_list(data: List[Any], max_items: int = 5) -> List[Any]:
    """Return first N items."""
    return data[:max_items] if data else []