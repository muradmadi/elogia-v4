"""Transformer for person data from enrichment payloads."""
from typing import Dict, Any
from .base import parse_date, slice_list

def transform_person(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Extract person fields from payload 1."""
    name = payload.get("name") or payload.get("full_name") or payload.get("fullName", "")
    # Simple name splitting (first word as first name, rest as last name)
    parts = name.split(" ", 1)
    first_name = parts[0] if parts else None
    last_name = parts[1] if len(parts) > 1 else None
    
    return {
        "name": name,  # alias full_name
        "first_name": first_name,
        "last_name": last_name,
        "linkedin_url": payload.get("url") or payload.get("linkedin_url"),
        "location": payload.get("location_name") or payload.get("location"),
        "headline": payload.get("headline"),
        "summary": payload.get("summary"),
        "experience": [
            {
                "title": exp.get("title"),
                "company": exp.get("company"),
                "start_date": parse_date(exp.get("start_date")),
                "end_date": parse_date(exp.get("end_date")) or "Present",
                "is_current": exp.get("is_current", False),
                "description": exp.get("summary"),
            }
            for exp in slice_list(payload.get("experience", []))
        ],
        "education": [
            {
                "school_name": edu.get("school_name"),
                "degree": edu.get("degree"),
                "field_of_study": edu.get("field_of_study"),
                "start_date": parse_date(edu.get("start_date")),
                "end_date": parse_date(edu.get("end_date")),
            }
            for edu in payload.get("education", [])
        ],
        "languages": [
            {
                "language": lang.get("language"),
                "proficiency": lang.get("proficiency"),
            }
            for lang in payload.get("languages", [])
        ],
    }