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
    tags = []
    tags.extend(derived.get("business_type", []))
    tags.extend(derived.get("subindustry", []))
    if derived.get("pattern_tags"):
        tags.append(derived["pattern_tags"])

    return {
        "name": payload.get("name"),
        "domain": payload.get("domain"),
        "industry": payload.get("industry"),
        "size": payload.get("size"),
        "revenue": payload.get("annual_revenue"),
        "headquarters": headquarters,
        "description": payload.get("description"),
        "specialties": payload.get("specialties", []),
        "business_tags": tags,
    }