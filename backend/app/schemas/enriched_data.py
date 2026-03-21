"""Pydantic schemas for enriched lead profile data."""
from pydantic import Field
from typing import List, Optional

from .base import BaseSchema

# --- 1. Nested Models for Person Data ---
class ExperienceView(BaseSchema):
    title: str = Field(description="Job title held at the company")
    company: str = Field(description="Name of the employer")
    start_date: Optional[str] = Field(None, description="Start date of the role (YYYY-MM-DD)")
    end_date: Optional[str] = Field("Present", description="End date of the role, or 'Present' if current")
    is_current: bool = Field(description="Indicates whether the role is ongoing")

class EducationView(BaseSchema):
    school_name: str = Field(description="Name of the educational institution")
    degree: Optional[str] = Field(None, description="Degree or certification obtained")

class LanguageView(BaseSchema):
    language: str = Field(description="Language name (e.g., Spanish, English)")
    proficiency: Optional[str] = Field(None, description="Self-reported proficiency level")

# --- 2. Nested Models for Company Data ---
class CompanyView(BaseSchema):
    name: str = Field(description="Company legal name")
    domain: Optional[str] = Field(None, description="Primary website domain")
    industry: str = Field(description="Industry classification (e.g., Food and Beverage)")
    size: str = Field(description="Employee count range (e.g., '10,001+ employees')")
    revenue: Optional[str] = Field(None, description="Annual revenue range (e.g., '10B-100B')")
    headquarters: str = Field(description="City and country of headquarters")
    description: str = Field(description="Company description or overview")
    specialties: List[str] = Field(default_factory=list, description="List of company specialties")
    business_tags: List[str] = Field(default_factory=list, description="Derived business tags (e.g., B2C, CPG, Sustainability)")

# --- 3. Nested Models for Role Intelligence ---
class PublicStatementView(BaseSchema):
    date: str = Field(description="Date of the statement (YYYY-MM-DD)")
    quote: str = Field(description="Exact quote from the person")
    context: str = Field(description="Context in which the quote was made")
    source: str = Field(description="Source URL or reference")

# Product intelligence models (from payload 4)
class TopImageItemView(BaseSchema):
    url: str = Field(description="URL of the product image")
    why: str = Field(description="Reason this image is considered best/worst")

class GalleryFlowView(BaseSchema):
    story_arc: Optional[str] = Field(None, description="Narrative progression of the image gallery")
    progression: Optional[str] = Field(None, description="Progression of the image gallery")
    coverage_gaps: List[str] = Field(default_factory=list, description="Missing elements in the visual story")
    mobile_experience: Optional[str] = Field(None, description="Mobile experience analysis")

class CompetitiveBenchmarkView(BaseSchema):
    relative_position: str = Field(description="Position vs competitors: 'above', 'below', or 'on par'")
    strengths_vs_competitors: List[str] = Field(default_factory=list, description="Areas where the product outperforms")
    weaknesses_vs_competitors: List[str] = Field(default_factory=list, description="Areas where competitors lead")
    competitor_tactics_not_used: List[str] = Field(default_factory=list, description="Strategies used by competitors but not by this brand")

class RecommendationView(BaseSchema):
    recommendation: str = Field(description="Specific actionable suggestion")
    priority: str = Field(description="Priority level: 'high', 'medium', 'low'")
    effort: str = Field(description="Estimated effort: 'low', 'medium', 'high'")
    expected_impact: str = Field(description="Predicted outcome of implementing the recommendation")

class ProductIntelligenceView(BaseSchema):
    product_name: str = Field(description="Name of the product analyzed")
    overall_score: float = Field(description="Overall rating (0-10) of the product's digital presence")
    summary: str = Field(description="High-level assessment of the product's visual strategy")
    reasoning: Optional[str] = Field(None, description="Detailed reasoning behind the score and summary")
    confidence: Optional[str] = Field(None, description="Confidence level: 'high', 'medium', 'low'")
    top_images: List[TopImageItemView] = Field(default_factory=list, description="Key images highlighted in the analysis")
    gallery_flow: Optional[GalleryFlowView] = Field(None, description="Analysis of the image gallery flow")
    mobile_experience_score: Optional[int] = Field(None, description="Mobile experience score (0-10)")
    competitive_benchmark: Optional[CompetitiveBenchmarkView] = Field(None, description="Comparison against competitors")
    prioritized_recommendations: List[RecommendationView] = Field(default_factory=list, description="Actionable improvements")

# Pain point analysis models (from payload 5)
class PainPointDetail(BaseSchema):
    pain_point: str = Field(description="Brief name of the pain point")
    description: str = Field(description="Detailed explanation of the pain point")
    urgency: str = Field(description="Urgency level: 'critical', 'high', 'medium', 'low'")
    frequency: str = Field(description="How often the pain occurs: 'daily', 'weekly', 'monthly'")
    impact: str = Field(description="Consequences if the pain is not addressed")
    evidence: str = Field(description="Supporting evidence or reasoning")
    evidence_level: str = Field(description="Strength of evidence: 'DIRECT', 'INFERRED_STRONG', 'INFERRED_WEAK'")
    source: str = Field(description="Source URL or reference for the evidence")

class PainPointCategory(BaseSchema):
    name: str = Field(description="Category name (e.g., 'market', 'operational', 'performance')")
    pain_points: List[PainPointDetail] = Field(default_factory=list, description="List of pain points in this category")

class TopPainsSummary(BaseSchema):
    most_urgent: str = Field(description="Pain point requiring immediate attention")
    most_frequent: str = Field(description="Pain point that occurs most often")
    most_impactful: str = Field(description="Pain point with the greatest potential impact")

class PainPointAnalysis(BaseSchema):
    notes: Optional[str] = Field(None, description="Additional context or caveats")
    sources: List[str] = Field(default_factory=list, description="URLs of sources used in the analysis")
    subject_name: str = Field(description="Name of the person the analysis refers to")
    subject_title: str = Field(description="Title of the person")
    subject_company: str = Field(description="Company of the person")
    reasoning: Optional[str] = Field(None, description="Reasoning behind the analysis")
    confidence: Optional[str] = Field(None, description="Overall confidence: 'high', 'medium', 'low'")
    top_pains: TopPainsSummary = Field(description="Summary of the most critical pain points")
    categories: List[PainPointCategory] = Field(default_factory=list, description="Pain points grouped by category")

# Outreach strategy models (from payload 6)
class MessageArchitectureView(BaseSchema):
    hook: str = Field(description="Opening line to grab attention")
    bridge: str = Field(description="Connection between hook and value proposition")
    proof: str = Field(description="Evidence of capability or track record")
    ask: str = Field(description="Specific call-to-action")

class AngleVariantView(BaseSchema):
    angle_name: str = Field(description="Name of the outreach angle")
    opening: str = Field(description="Suggested opening sentence")
    framing: str = Field(description="How to frame the value proposition")
    proof_point: str = Field(description="Supporting evidence for this angle")
    cta: str = Field(description="Call-to-action specific to this angle")
    target_pain: str = Field(description="The pain point this angle addresses")

class ChannelTimingView(BaseSchema):
    best_time: str = Field(description="Optimal time window for outreach")
    avoid_time: str = Field(description="Times to avoid")
    reasoning: str = Field(description="Why these timings are recommended")


class ChannelFormatView(BaseSchema):
    style: Optional[str] = Field(None, description="Style of the content format")
    length: Optional[str] = Field(None, description="Length of the content format")
    reasoning: Optional[str] = Field(None, description="Reasoning behind the format choice")


class ChannelStrategyView(BaseSchema):
    primary_channel: str = Field(description="Main channel for outreach (e.g., 'Email')")
    secondary_channel: str = Field(description="Fallback channel (e.g., 'LinkedIn')")
    format: Optional[ChannelFormatView] = Field(None, description="Format details (style, length, reasoning)")
    timing: ChannelTimingView = Field(description="Timing recommendations")

class RiskMitigationView(BaseSchema):
    risk: str = Field(description="Description of the potential risk")
    impact: str = Field(description="Impact level: 'high', 'medium', 'low'")
    likelihood: str = Field(description="Likelihood: 'high', 'medium', 'low'")
    mitigation: str = Field(description="How to reduce or address the risk")

class PainSolutionMapView(BaseSchema):
    their_pain: str = Field(description="Pain point experienced by the prospect")
    your_solution: str = Field(description="How your offering addresses it")
    evidence_level: str = Field(description="Strength of connection: 'DIRECT', 'INFERRED_STRONG', etc.")
    connection_logic: str = Field(description="Reasoning behind the mapping")

class StrategicPositioningView(BaseSchema):
    core_thesis: str = Field(description="Central argument for relevance")
    pain_solution_map: List[PainSolutionMapView] = Field(default_factory=list, description="Detailed mapping of pains to solutions")

class OutreachStrategyView(BaseSchema):
    notes: Optional[str] = Field(None, description="Additional context about the strategy")
    sources: List[str] = Field(default_factory=list, description="URLs of sources used")
    reasoning: Optional[str] = Field(None, description="Reasoning behind the chosen strategy")
    confidence: Optional[str] = Field(None, description="Confidence level: 'high', 'medium', 'low'")
    message_architecture: MessageArchitectureView = Field(description="Core message structure")
    angle_variants: List[AngleVariantView] = Field(default_factory=list, description="Alternative outreach angles")
    channel_strategy: ChannelStrategyView = Field(description="Channel and timing recommendations")
    risk_mitigation: List[RiskMitigationView] = Field(default_factory=list, description="Potential risks and how to address them")
    strategic_positioning: StrategicPositioningView = Field(description="Overall strategic fit and mapping")

# Updated RoleIntelligenceView with all components
class RoleIntelligenceView(BaseSchema):
    day_to_day: List[str] = Field(default_factory=list, description="High-level day-to-day responsibilities")
    decision_authority: str = Field(description="Summary of the person's decision-making power")
    reports_to: str = Field(description="Who the person likely reports to")
    direct_reports: str = Field(description="Description of direct reports or team structure")
    department_products: List[str] = Field(default_factory=list, description="Products the person's department is responsible for")
    public_statements: List[PublicStatementView] = Field(default_factory=list, description="Public quotes and statements")
    career_trajectory: Optional[str] = Field(None, description="Summary of career progression and patterns")
    recent_initiatives: List[str] = Field(default_factory=list, description="Recent projects or strategic priorities")
    product_intelligence: List[ProductIntelligenceView] = Field(default_factory=list, description="Analysis of relevant products")
    pain_points: Optional[PainPointAnalysis] = Field(None, description="Analysis of likely pain points")
    outreach_strategy: Optional[OutreachStrategyView] = Field(None, description="Outreach strategy based on intelligence")

# --- 4. The Main View Model for the Frontend ---
class LeadProfileView(BaseSchema):
    # Person Identity
    name: str = Field(description="Full name of the lead")
    current_title: str = Field(description="Current job title")
    location: str = Field(description="Geographic location (city, country)")
    linkedin_url: Optional[str] = Field(None, description="URL to LinkedIn profile")
    headline: Optional[str] = Field(None, description="Professional headline from profile")
    summary: Optional[str] = Field(None, description="Profile summary or bio")
    
    # Nested Arrays (Sliced in transformer)
    recent_experience: List[ExperienceView] = Field(default_factory=list, description="Most recent work experiences")
    education: List[EducationView] = Field(default_factory=list, description="Educational background")
    languages: List[LanguageView] = Field(default_factory=list, description="Languages spoken")
    
    # Nested Objects
    company: Optional[CompanyView] = Field(None, description="Current company details")
    intelligence: Optional[RoleIntelligenceView] = Field(None, description="Deep intelligence about the role")