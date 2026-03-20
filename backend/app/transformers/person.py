from typing import Dict, Any
from .base import parse_date, slice_list

def transform_person(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Extract person fields from payload 1."""
    return {
        "name": payload.get("name"),
        "current_title": payload.get("title"),
        "location": payload.get("location_name"),
        "linkedin_url": payload.get("url"),
        "headline": payload.get("headline"),
        "summary": payload.get("summary"),
        "recent_experience": [
            {
                "title": exp.get("title"),
                "company": exp.get("company"),
                "start_date": parse_date(exp.get("start_date")),
                "end_date": parse_date(exp.get("end_date")) or "Present",
                "is_current": exp.get("is_current", False),
            }
            for exp in slice_list(payload.get("experience", []))
        ],
        "education": [
            {
                "school_name": edu.get("school_name"),
                "degree": edu.get("degree"),
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