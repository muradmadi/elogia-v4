"""Transformer for company data from enrichment payloads."""
from typing import Dict, Any

def transform_company(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Extract company fields from payload 2."""
    locations = payload.get("locations", [])
    headquarters = ""
    for loc in locations:
        if loc.get("is_primary"):
            inferred = loc.get("inferred_location", {})
            headquarters = inferred.get("formatted_address") or loc.get("address")
            break
    if not headquarters:
        headquarters = payload.get("locality", "")

    derived = payload.get("derived_datapoints", {})
    # Build derived_datapoints object matching DerivedDatapointsView schema
    derived_datapoints = {
        "pattern_tags": derived.get("pattern_tags"),
        "business_type": derived.get("business_type", []),
        "business_stage": derived.get("business_stage"),
        "scale_scope": derived.get("scale_scope"),
    }
    # Remove None values for optional fields
    derived_datapoints = {k: v for k, v in derived_datapoints.items() if v is not None}

    return {
        "name": payload.get("name"),
        "domain": payload.get("domain"),
        "industry": payload.get("industry"),
        "size": payload.get("size"),
        "employee_count": payload.get("employee_count"),
        "annual_revenue": payload.get("annual_revenue"),
        "locality": headquarters,  # map headquarters to locality
        "country": None,  # country not available in payload
        "description": payload.get("description"),
        "specialties": payload.get("specialties", []),
        "derived_datapoints": derived_datapoints if derived_datapoints else None,
    }