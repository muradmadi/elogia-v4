from typing import Dict, Any, Optional, List
from app.schemas.enriched_data import LeadProfileView
from app.schemas.sequence import ClaudeOutreachView
from .person import transform_person
from .company import transform_company
from .intelligence import transform_role_intelligence
from .sequence import transform_sequence_response, validate_claude_response

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


def build_claude_outreach(raw_claude_response: Dict[str, Any]) -> ClaudeOutreachView:
    """Transform raw Claude API response into validated outreach sequence.
    
    Args:
        raw_claude_response: Raw JSON response from Claude's sequence generation
        
    Returns:
        ClaudeOutreachView: Validated and structured outreach sequence data
    """
    return transform_sequence_response(raw_claude_response)


def validate_claude_outreach(raw_claude_response: Dict[str, Any]) -> ClaudeOutreachView:
    """Quick validation of Claude response using Pydantic's model_validate.
    
    This is a simpler alternative when you just want to validate the response
    without additional transformation logic.
    
    Args:
        raw_claude_response: Raw JSON response from Claude's sequence generation
        
    Returns:
        ClaudeOutreachView: Validated outreach sequence data
    """
    return validate_claude_response(raw_claude_response)