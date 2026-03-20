import logging
from typing import Dict, Any, List, Optional
from .base import slice_list

# Configure logger
logger = logging.getLogger(__name__)

def transform_public_statements(statements: List[Dict]) -> List[Dict]:
    return [
        {
            "date": stmt.get("date"),
            "quote": stmt.get("quote"),
            "context": stmt.get("context"),
            "source": stmt.get("source"),
        }
        for stmt in statements
    ]

def transform_product_intelligence(product_payload: Dict[str, Any]) -> List[Dict]:
    """Map product analysis (payload 4) to ProductIntelligenceView shape."""
    if not product_payload:
        logger.warning("Empty product payload received")
        return []
    
    # Extract product name from reasoning field
    # Clay includes product name in the reasoning text
    product_name = None
    reasoning = product_payload.get("reasoning", "")
    if reasoning and "for" in reasoning:
        # Try to extract product name from phrases like "data for Almirón Profutura 33"
        import re
        # Look for "for [Product Name]" pattern, capturing until next period or comma
        # Using .+? to match any characters (including Unicode) non-greedily
        match = re.search(r'for\s+(.+?)(?:\.|,|$)', reasoning)
        if match:
            product_name = match.group(1).strip()
            logger.debug(f"Extracted product name: {product_name}")
        else:
            logger.warning(f"Could not extract product name from reasoning: {reasoning[:100]}...")
    else:
        logger.warning(f"No reasoning field found or 'for' not in reasoning")
    
    # Fallback to generic name if extraction fails
    if not product_name:
        product_name = "Product Analysis"
        logger.info("Using fallback product name: 'Product Analysis'")
    
    # Extract overall score
    overall_score_data = product_payload.get("overallScore", {})
    overall_score = overall_score_data.get("score")
    if overall_score is not None:
        try:
            overall_score = float(overall_score)
        except (ValueError, TypeError):
            overall_score = None
    
    # Extract summary
    summary = overall_score_data.get("summary")
    
    # Extract top images - map to TopImageItemView schema
    top_images_data = product_payload.get("topThreeImages", {})
    top_images = []
    
    # Extract best image
    best_image_data = top_images_data.get("bestImage")
    if best_image_data and isinstance(best_image_data, dict):
        top_images.append({
            "url": best_image_data.get("url", ""),
            "why": best_image_data.get("why", "Best performing image with highest visual appeal and conversion potential")
        })
    
    # Extract worst image
    worst_image_data = top_images_data.get("worstImage")
    if worst_image_data and isinstance(worst_image_data, dict):
        top_images.append({
            "url": worst_image_data.get("url", ""),
            "why": worst_image_data.get("why", "Image with most room for improvement, identified as the biggest opportunity")
        })
    
    # Extract gallery flow
    gallery_flow_data = product_payload.get("galleryFlow", {})
    gallery_flow = None
    if gallery_flow_data:
        gallery_flow = {
            "story_arc": gallery_flow_data.get("storyArc"),
            "progression": gallery_flow_data.get("progression"),
            "coverage_gaps": gallery_flow_data.get("coverageGaps", []),
            "mobile_experience": gallery_flow_data.get("mobileExperience")
        }
    
    # Extract competitive benchmark
    competitive_benchmark_data = product_payload.get("competitiveBenchmark", {})
    competitive_benchmark = None
    if competitive_benchmark_data:
        competitive_benchmark = {
            "relative_position": competitive_benchmark_data.get("relativePosition"),
            "strengths_vs_competitors": competitive_benchmark_data.get("strengthsVsCompetitors", []),
            "weaknesses_vs_competitors": competitive_benchmark_data.get("weaknessesVsCompetitors", []),
            "competitor_tactics_not_used": competitive_benchmark_data.get("competitorTacticsNotUsed", [])
        }
    
    # Extract prioritized recommendations
    recommendations_data = product_payload.get("prioritizedRecommendations", [])
    prioritized_recommendations = []
    for rec in recommendations_data:
        if isinstance(rec, dict):
            prioritized_recommendations.append({
                "recommendation": rec.get("recommendation"),
                "priority": rec.get("priority", "medium"),
                "effort": rec.get("effort", "medium"),
                "expected_impact": rec.get("expectedImpact", "medium")
            })
    
    return [{
        "product_name": product_name,
        "overall_score": overall_score,
        "summary": summary,
        "reasoning": product_payload.get("reasoning"),
        "confidence": product_payload.get("confidence"),
        "top_images": top_images,
        "gallery_flow": gallery_flow,
        "mobile_experience_score": None,  # Not in current data
        "competitive_benchmark": competitive_benchmark,
        "prioritized_recommendations": prioritized_recommendations,
    }]

def transform_pain_points(pain: Dict[str, Any]) -> Optional[Dict]:
    if not pain:
        logger.warning("Empty pain payload received")
        return None
    
    # Map top pains from camelCase to snake_case
    top_pains_data = pain.get("topPains", {})
    top_pains = None
    if top_pains_data:
        top_pains = {
            "most_urgent": top_pains_data.get("mostUrgent"),
            "most_frequent": top_pains_data.get("mostFrequent"),
            "most_impactful": top_pains_data.get("mostImpactful")
        }
    
    # Map categories if present; adjust structure to match PainPointAnalysis
    categories = []
    pain_points_data = pain.get("painPoints", {})
    for cat_name, cat_data in pain_points_data.items():
        if isinstance(cat_data, list):
            categories.append({
                "name": cat_name,
                "pain_points": [
                    {
                        "pain_point": p.get("painPoint"),
                        "description": p.get("description"),
                        "urgency": p.get("urgency"),
                        "frequency": p.get("frequency"),
                        "impact": p.get("impact"),
                        "evidence": p.get("evidence"),
                        "evidence_level": p.get("evidenceLevel"),
                        "source": p.get("source"),
                    }
                    for p in cat_data
                ]
            })
    
    subject_data = pain.get("subject", {})
    return {
        "notes": pain.get("notes"),
        "sources": pain.get("sources", []),
        "subject_name": subject_data.get("name"),
        "subject_title": subject_data.get("title"),
        "subject_company": subject_data.get("company"),
        "reasoning": pain.get("reasoning"),
        "confidence": pain.get("confidence"),
        "top_pains": top_pains,
        "categories": categories,
    }

def transform_outreach_strategy(outreach: Dict[str, Any]) -> Optional[Dict]:
    if not outreach:
        logger.warning("Empty outreach payload received")
        return None
    
    # Extract text from nested message architecture objects
    message_arch_data = outreach.get("messageArchitecture", {})
    message_architecture = {}
    for key in ["hook", "bridge", "proof", "ask"]:
        if key in message_arch_data:
            value = message_arch_data[key]
            if isinstance(value, dict) and "text" in value:
                message_architecture[key] = value["text"]
            else:
                message_architecture[key] = value
    
    # Map angle variants from camelCase to snake_case
    angle_variants_data = outreach.get("angleVariants", [])
    angle_variants = []
    for angle in angle_variants_data:
        if isinstance(angle, dict):
            angle_variants.append({
                "angle_name": angle.get("angleName"),
                "proof_point": angle.get("proofPoint"),
                "target_pain": angle.get("targetPain"),
                "opening": angle.get("opening"),
                "framing": angle.get("framing"),
                "cta": angle.get("cta")
            })
    
    # Map channel strategy
    channel_strat_data = outreach.get("channelStrategy", {})
    channel_strategy = None
    if channel_strat_data:
        # Extract timing
        timing_data = channel_strat_data.get("timing", {})
        timing = None
        if timing_data:
            timing = {
                "best_time": timing_data.get("bestTime"),
                "avoid_time": timing_data.get("avoidTime"),
                "reasoning": timing_data.get("reasoning", "")
            }
        
        # Extract format
        format_data = channel_strat_data.get("format", {})
        format_info = None
        if format_data:
            format_info = {
                "style": format_data.get("style"),
                "length": format_data.get("length"),
                "reasoning": format_data.get("reasoning", "")
            }
        
        channel_strategy = {
            "primary_channel": channel_strat_data.get("primaryChannel"),
            "secondary_channel": channel_strat_data.get("secondaryChannel"),
            "timing": timing,
            "format": format_info
        }
    
    # Map strategic positioning
    strategic_pos_data = outreach.get("strategicPositioning", {})
    strategic_positioning = None
    if strategic_pos_data:
        # Map pain solution map from camelCase to snake_case
        pain_solution_map_data = strategic_pos_data.get("painSolutionMap", [])
        pain_solution_map = []
        for item in pain_solution_map_data:
            if isinstance(item, dict):
                pain_solution_map.append({
                    "their_pain": item.get("theirPain"),
                    "your_solution": item.get("yourSolution"),
                    "evidence_level": item.get("evidenceLevel"),
                    "connection_logic": item.get("connectionLogic")
                })
        
        strategic_positioning = {
            "core_thesis": strategic_pos_data.get("coreThesis"),
            "pain_solution_map": pain_solution_map
        }
    
    return {
        "notes": outreach.get("notes"),
        "sources": outreach.get("sources", []),
        "reasoning": outreach.get("reasoning"),
        "confidence": outreach.get("confidence"),
        "message_architecture": message_architecture,
        "angle_variants": angle_variants,
        "channel_strategy": channel_strategy,
        "risk_mitigation": outreach.get("riskMitigation", []),
        "strategic_positioning": strategic_positioning,
    }

def transform_role_intelligence(
    role_payload: Dict[str, Any],          # payload 3
    product_payload: Dict[str, Any],       # payload 4 (single dict)
    pain_payload: Dict[str, Any],           # payload 5
    outreach_payload: Dict[str, Any],       # payload 6
) -> Dict[str, Any]:
    """Combine all intelligence sources into a RoleIntelligenceView shape."""
    # From payload 3
    day_to_day = role_payload.get("dayToDay", {}).get("highLevel", [])
    decision_authority = role_payload.get("decisionAuthority", {}).get("summary", "")
    # reports_to and direct_reports may come from roleMeaningAtCompany in payload 3
    role_meaning = role_payload.get("roleMeaningAtCompany", {})
    reports_to = role_meaning.get("likelyReportsTo", "")
    direct_reports = role_meaning.get("directReports", "")
    # department products - extract from product payload if available
    department_products = []
    # public statements from payload 3
    public_statements = transform_public_statements(
        role_payload.get("recentActivity", {}).get("publicStatements", [])
    )
    career_trajectory = role_payload.get("careerTrajectory", {}).get("pattern")
    recent_initiatives = role_payload.get("recentActivity", {}).get("initiatives", [])

    # Transform the other payloads
    product_intelligence = transform_product_intelligence(product_payload)
    pain_points = transform_pain_points(pain_payload)
    outreach_strategy = transform_outreach_strategy(outreach_payload)

    return {
        "day_to_day": day_to_day,
        "decision_authority": decision_authority,
        "reports_to": reports_to,
        "direct_reports": direct_reports,
        "department_products": department_products,
        "public_statements": public_statements,
        "career_trajectory": career_trajectory,
        "recent_initiatives": recent_initiatives,
        "product_intelligence": product_intelligence,
        "pain_points": pain_points,
        "outreach_strategy": outreach_strategy,
    }