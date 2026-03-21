"""
Transformers package for converting raw payload data into structured lead profiles.

Naming Convention:
------------------
This package uses three distinct naming conventions to clearly separate concerns:

1. `transform_*` functions:
   - Convert raw payload dictionaries into domain-specific dictionaries
   - Example: `transform_person(person_payload)` → `PersonView` dict
   - These are single-purpose transformations of one data type

2. `build_*` functions:
   - Orchestrate multiple transformers to build complete view models
   - Example: `build_lead_profile(enrichment_job)` → `LeadProfileView` dict
   - These are higher-level orchestrators that combine multiple data sources

3. `validate_*` functions:
   - Validate existing dictionaries against Pydantic schemas
   - Example: `validate_claude_response(response_dict)` → validated dict or error
   - These ensure data integrity before further processing

Usage Pattern:
--------------
- Use `transform_*` for converting single payload types
- Use `build_*` for creating complete view models from multiple sources
- Use `validate_*` for validating Claude/LLM responses before use
"""

from typing import Dict, Any, Optional

from app.schemas.enriched_data import LeadProfileView
from .person import transform_person
from .company import transform_company
from .intelligence import transform_role_intelligence
from .sequence import transform_sequence_response, validate_claude_response
from .content import transform_content_snack, transform_asset_content
from .base import parse_date, slice_list


def build_lead_profile(
    person_payload: Dict[str, Any],
    company_payload: Optional[Dict[str, Any]] = None,
    role_intelligence_payload: Optional[Dict[str, Any]] = None,
    product_payload: Optional[Dict[str, Any]] = None,
    pain_payload: Optional[Dict[str, Any]] = None,
    outreach_payload: Optional[Dict[str, Any]] = None,
) -> LeadProfileView:
    """Orchestrate all transformations and return a validated LeadProfileView."""
    person_data = transform_person(person_payload)
    company_data = transform_company(company_payload) if company_payload else None

    intelligence_data = transform_role_intelligence(
        role_payload=role_intelligence_payload or {},
        product_payload=product_payload or {},
        pain_payload=pain_payload or {},
        outreach_payload=outreach_payload or {},
    )

    # Merge and validate
    lead_dict = {
        **person_data,
        "company": company_data,
        "intelligence": intelligence_data,
    }
    return LeadProfileView.model_validate(lead_dict)


__all__ = [
    "build_lead_profile",
    "transform_person",
    "transform_company",
    "transform_role_intelligence",
    "transform_sequence_response",
    "validate_claude_response",
    "transform_content_snack",
    "transform_asset_content",
    "parse_date",
    "slice_list",
]
