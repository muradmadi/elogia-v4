"""Transformer for pain point analysis from enrichment payloads."""
from typing import Dict, Any, List, Optional


def _transform_pain_point(item: Dict[str, Any]) -> Dict[str, Any]:
    """Transform a single pain point into PainPointDetailView shape."""
    return {
        "pain_point": item.get("painPoint", ""),
        "description": item.get("description", ""),
        "urgency": item.get("urgency", ""),
        "frequency": item.get("frequency", ""),
        "impact": item.get("impact", ""),
        "evidence": item.get("evidence", ""),
        "evidence_level": item.get("evidenceLevel", ""),
    }


def _transform_top_pains(top_pains: Dict[str, Any]) -> Dict[str, Any]:
    """Transform top pains summary into TopPainsSummaryView shape."""
    return {
        "most_urgent": top_pains.get("mostUrgent", ""),
        "most_frequent": top_pains.get("mostFrequent", ""),
        "most_impactful": top_pains.get("mostImpactful", ""),
    }


def _transform_categories(pain_points: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
    """Transform pain points dict into categories shape.

    Each key (e.g., 'market', 'operational') maps to a list of PainPointDetailView objects.
    """
    categories: Dict[str, List[Dict[str, Any]]] = {}

    for category_name, items in pain_points.items():
        if isinstance(items, list):
            categories[category_name] = [
                _transform_pain_point(item)
                for item in items
                if isinstance(item, dict)
            ]

    return categories


def transform_painpoints(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Transform raw pain payload into PainPointsSchema shape.

    Maps raw payload 5 fields to the canonical PainPointsSchema structure,
    including TopPainsSummaryView and dynamic category groupings of PainPointDetailView.
    """
    subject = payload.get("subject", {})

    return {
        "notes": payload.get("notes"),
        "role_scope": subject.get("roleScope"),
        "top_pains": _transform_top_pains(payload.get("topPains", {})),
        "categories": _transform_categories(payload.get("painPoints", {})),
    }
