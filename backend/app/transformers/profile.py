"""Transformer for profile/intelligence data from enrichment payloads."""
from typing import Dict, Any, List, Optional


def _transform_reporting_structure(role_meaning: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Transform reporting structure into ReportingStructureView shape."""
    reporting = role_meaning.get("reportingStructure", {})
    if not reporting:
        return None

    return {
        "division_name": role_meaning.get("divisionName"),
        "reports_to": reporting.get("likelyReportsTo"),
        "direct_reports": reporting.get("directReports"),
    }


def _transform_department_products(products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Transform department products into DepartmentProductView shape."""
    return [
        {
            "product_name": item.get("productName", ""),
            "status": item.get("status", "likely"),
            "reasoning": item.get("reasoning"),
        }
        for item in products
        if isinstance(item, dict) and item.get("productName")
    ]


def _transform_public_statements(statements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Transform public statements into PublicStatementView shape."""
    return [
        {
            "date": stmt.get("date"),
            "quote": stmt.get("quote"),
            "context": stmt.get("context"),
        }
        for stmt in statements
        if isinstance(stmt, dict) and stmt.get("quote")
    ]


def _transform_career_trajectory(trajectory: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Transform career trajectory into CareerTrajectoryView shape."""
    if not trajectory:
        return None

    return {
        "pattern": trajectory.get("pattern"),
        "progression": trajectory.get("progression"),
        "expertise": trajectory.get("expertise", []),
    }


def transform_profile(
    role_payload: Dict[str, Any],
    product_payload: Optional[Dict[str, Any]] = None,
    pain_payload: Optional[Dict[str, Any]] = None,
    outreach_payload: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Transform role intelligence payload into ProfileSchema shape.

    Maps raw payload 3 fields to the canonical ProfileSchema structure,
    including nested ReportingStructureView, DepartmentProductView,
    CareerTrajectoryView, and PublicStatementView objects.
    """
    # Handle both nested and flat payload structures for role_summary
    # Nested: roleMeaningAtCompany.summary
    # Flat: roleMeaningAtCompany_summary
    role_summary = None
    if "roleMeaningAtCompany" in role_payload:
        role_meaning = role_payload.get("roleMeaningAtCompany", {})
        role_summary = role_meaning.get("summary")
    elif "roleMeaningAtCompany_summary" in role_payload:
        role_summary = role_payload.get("roleMeaningAtCompany_summary")
    
    recent_activity = role_payload.get("recentActivity", {})
    career = role_payload.get("careerTrajectory", {})

    return {
        "role_summary": role_summary,
        "day_to_day": role_payload.get("dayToDay", {}).get("highLevel", []),
        "decision_authority": role_payload.get("decisionAuthority", {}).get("summary"),
        "reporting_structure": _transform_reporting_structure(role_meaning),
        "department_products": _transform_department_products(
            role_payload.get("departmentProducts", [])
        ),
        "recent_initiatives": recent_activity.get("initiatives", []),
        "strategic_priorities": recent_activity.get("strategicPriorities", []),
        "public_statements": _transform_public_statements(
            recent_activity.get("publicStatements", [])
        ),
        "career_trajectory": _transform_career_trajectory(career),
    }
