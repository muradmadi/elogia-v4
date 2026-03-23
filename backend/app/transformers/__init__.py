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

from app.schemas.lead_profile import LeadProfileView
from .person import transform_person
from .company import transform_company

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

    # Transform Profile (payload 3)
    from .profile import transform_profile
    profile_data = transform_profile(role_intelligence_payload) if role_intelligence_payload else None
    
    # Transform Products (payload 4)
    products_data = []
    if product_payload:
        from .products import transform_product
        if isinstance(product_payload, list):
            for item in product_payload:
                products_data.append(transform_product(item))
        else:
            products_data.append(transform_product(product_payload))
            
    # Transform Pain (payload 5) using the service router mapping
    pain_points_data = None
    if pain_payload:
        from .intelligence import transform_pain_points
        pain_orig = transform_pain_points(pain_payload)
        if pain_orig:
            categories_dict = {}
            for category in pain_orig.get("categories", []):
                category_name = category.get("name", "uncategorized")
                pts = []
                for pain in category.get("pain_points", []):
                    pts.append({
                        "painPoint": pain.get("pain_point", ""),
                        "description": pain.get("description", ""),
                        "urgency": pain.get("urgency", ""),
                        "frequency": pain.get("frequency", ""),
                        "impact": pain.get("impact", ""),
                        "evidence": pain.get("evidence", ""),
                        "evidenceLevel": pain.get("evidence_level", "")
                    })
                categories_dict[category_name] = pts
                
            top_pains_data = pain_orig.get("top_pains", {})
            top_pains = {
                "mostUrgent": top_pains_data.get("most_urgent", ""),
                "mostFrequent": top_pains_data.get("most_frequent", ""),
                "mostImpactful": top_pains_data.get("most_impactful", "")
            }
            
            pain_points_data = {
                "notes": pain_orig.get("notes"),
                "role_scope": pain_orig.get("subject_title"),
                "topPains": top_pains,
                "painPoints": categories_dict
            }
            
    # Transform Communication (payload 6) using the service router mapping
    outreach_data = None
    if outreach_payload:
        from .intelligence import transform_outreach_strategy
        outreach_orig = transform_outreach_strategy(outreach_payload)
        if outreach_orig:
            msg_arch = outreach_orig.get("message_architecture", {})
            message_architecture = {
                "hook": {"text": msg_arch.get("hook", "")},
                "bridge": {"text": msg_arch.get("bridge", "")},
                "proof": {"text": msg_arch.get("proof", "")},
                "ask": {"text": msg_arch.get("ask", "")}
            }
            
            chan_strat = outreach_orig.get("channel_strategy") or {}
            timing_data = chan_strat.get("timing") or {}
            format_data = chan_strat.get("format") or {}
            
            channel_strategy = {
                "primaryChannel": chan_strat.get("primary_channel", ""),
                "secondaryChannel": chan_strat.get("secondary_channel", ""),
                "format": {
                    "style": format_data.get("style", ""),
                    "length": format_data.get("length", ""),
                    "reasoning": format_data.get("reasoning")
                },
                "timing": {
                    "bestTime": timing_data.get("best_time", ""),
                    "avoidTime": timing_data.get("avoid_time", ""),
                    "reasoning": timing_data.get("reasoning")
                }
            }
            
            angle_variants = []
            for angle in outreach_orig.get("angle_variants", []):
                angle_variants.append({
                    "angleName": angle.get("angle_name", ""),
                    "targetPain": angle.get("target_pain", ""),
                    "opening": angle.get("opening", ""),
                    "framing": angle.get("framing", ""),
                    "proofPoint": angle.get("proof_point", ""),
                    "cta": angle.get("cta", "")
                })
                
            risk_mitigation = outreach_orig.get("risk_mitigation", [])
                
            strat_pos = outreach_orig.get("strategic_positioning") or {}
            pain_solution_map = []
            for map_item in strat_pos.get("pain_solution_map", []):
                pain_solution_map.append({
                    "theirPain": map_item.get("their_pain", ""),
                    "yourSolution": map_item.get("your_solution", ""),
                    "evidenceLevel": map_item.get("evidence_level", ""),
                    "connectionLogic": map_item.get("connection_logic", "")
                })
                
            strategic_positioning = {
                "coreThesis": strat_pos.get("core_thesis", ""),
                "painSolutionMap": pain_solution_map
            }
            
            outreach_data = {
                "notes": outreach_orig.get("notes"),
                "strategicPositioning": strategic_positioning,
                "messageArchitecture": message_architecture,
                "channelStrategy": channel_strategy,
                "angleVariants": angle_variants,
                "riskMitigation": risk_mitigation
            }

    # Merge and validate
    lead_dict = {
        **person_data,
        "company": company_data,
        "profile": profile_data,
        "products": products_data,
        "pain_points": pain_points_data,
        "outreach": outreach_data,
    }
    return LeadProfileView.model_validate(lead_dict)


__all__ = [
    "build_lead_profile",
    "transform_person",
    "transform_company",

    "transform_sequence_response",
    "validate_claude_response",
    "transform_content_snack",
    "transform_asset_content",
    "parse_date",
    "slice_list",
]
