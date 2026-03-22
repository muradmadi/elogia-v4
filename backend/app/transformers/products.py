"""Transformer for product visual intelligence from enrichment payloads."""
from typing import Dict, Any, List, Optional


def _transform_technical_quality(quality: Dict[str, Any]) -> Dict[str, Any]:
    """Transform technical quality into ImageQualityView shape."""
    return {
        "score": quality.get("score", 0),
        "strengths": quality.get("strengths", []),
        "weaknesses": quality.get("weaknesses", []),
    }


def _transform_main_image(main_image: Dict[str, Any]) -> Dict[str, Any]:
    """Transform main image into MainImageView shape."""
    technical = main_image.get("technicalQuality", {})
    return {
        "technical_quality": _transform_technical_quality(technical),
    }


def _transform_mobile_experience(mobile: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Transform mobile experience into MobileExperienceView shape."""
    if not mobile:
        return None

    return {
        "score": mobile.get("score", 0),
        "issues": mobile.get("issues", []),
    }


def _transform_gallery_flow(gallery: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Transform gallery flow into GalleryFlowView shape."""
    if not gallery:
        return None

    return {
        "story_arc": gallery.get("storyArc"),
        "progression": gallery.get("progression"),
        "coverage_gaps": gallery.get("coverageGaps", []),
        "mobile_experience": _transform_mobile_experience(gallery.get("mobileExperience")),
    }


def _transform_a_plus_content(a_plus: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Transform A+ content into APlusContentView shape."""
    if not a_plus:
        return None

    return {
        "present": a_plus.get("present", False),
        "assessment": a_plus.get("assessment"),
        "missed_opportunities": a_plus.get("missedOpportunities", []),
    }


def _transform_image_detail(image: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Transform image detail into ImageDetailView shape."""
    if not image or not image.get("url"):
        return None

    return {
        "url": image["url"],
        "why": image.get("why", ""),
    }


def _transform_opportunity_detail(opportunity: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Transform opportunity detail into OpportunityDetailView shape."""
    if not opportunity:
        return None

    return {
        "how": opportunity.get("how", ""),
        "description": opportunity.get("description", ""),
    }


def _transform_top_images(top: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Transform top images into TopImagesView shape."""
    if not top:
        return None

    return {
        "best_image": _transform_image_detail(top.get("bestImage")),
        "worst_image": _transform_image_detail(top.get("worstImage")),
        "biggest_opportunity": _transform_opportunity_detail(top.get("biggestOpportunity")),
    }


def _transform_competitive_benchmark(benchmark: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Transform competitive benchmark into CompetitiveBenchmarkView shape."""
    if not benchmark:
        return None

    return {
        "relative_position": benchmark.get("relativePosition", ""),
        "strengths_vs_competitors": benchmark.get("strengthsVsCompetitors", []),
        "weaknesses_vs_competitors": benchmark.get("weaknessesVsCompetitors", []),
        "competitor_tactics_not_used": benchmark.get("competitorTacticsNotUsed", []),
    }


def _transform_recommendations(recommendations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Transform recommendations into RecommendationView shape."""
    return [
        {
            "effort": rec.get("effort", ""),
            "priority": rec.get("priority", ""),
            "expected_impact": rec.get("expectedImpact", ""),
            "recommendation": rec.get("recommendation", ""),
        }
        for rec in recommendations
        if isinstance(rec, dict)
    ]


def transform_product(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Transform raw product payload into ProductSchema shape.

    Maps raw payload 4 fields to the canonical ProductSchema structure,
    including all nested view objects for visual and conversion intelligence.
    """
    return {
        "overall_score": {
            "score": payload.get("overallScore", {}).get("score", 0),
            "summary": payload.get("overallScore", {}).get("summary", ""),
        },
        "main_image": _transform_main_image(payload.get("mainImage", {})),
        "gallery_flow": _transform_gallery_flow(payload.get("galleryFlow")),
        "a_plus_content": _transform_a_plus_content(payload.get("aPlusContent")),
        "top_images": _transform_top_images(payload.get("topThreeImages")),
        "competitive_benchmark": _transform_competitive_benchmark(
            payload.get("competitiveBenchmark")
        ),
        "prioritized_recommendations": _transform_recommendations(
            payload.get("prioritizedRecommendations", [])
        ),
    }
