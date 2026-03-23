from pydantic import Field
from typing import List, Optional, Dict
from .base import BaseSchema

class ExperienceView(BaseSchema):
    title: str = Field(description="Job title held")
    company_name: str = Field(alias="company", description="Name of the employer")
    start_date: Optional[str] = Field(None, description="Start date (YYYY-MM-DD)")
    end_date: Optional[str] = Field(None, description="End date (YYYY-MM-DD)")
    is_current: bool = Field(default=False, description="Indicates if the role is ongoing")
    description: Optional[str] = Field(alias="summary", default=None, description="Role description")

class EducationView(BaseSchema):
    school_name: str = Field(description="Name of the educational institution")
    degree: Optional[str] = Field(None, description="Degree obtained")
    field_of_study: Optional[str] = Field(None, description="Field of study")
    start_date: Optional[str] = Field(None, description="Start date (YYYY-MM-DD)")
    end_date: Optional[str] = Field(None, description="End date (YYYY-MM-DD)")

class LanguageView(BaseSchema):
    language: str = Field(description="Language name")
    proficiency: Optional[str] = Field(None, description="Proficiency level")

class PersonSchema(BaseSchema):
    """Clean, standalone view model strictly for person-level data."""
    full_name: str = Field(alias="name", description="Full name of the lead")
    first_name: Optional[str] = Field(None, description="First name")
    last_name: Optional[str] = Field(None, description="Last name")
    linkedin_url: Optional[str] = Field(alias="url", default=None, description="LinkedIn profile URL")
    location: Optional[str] = Field(alias="location_name", default=None, description="Primary geographic location")
    headline: Optional[str] = Field(None, description="Professional headline")
    summary: Optional[str] = Field(None, description="Profile bio or summary")
    
    experience: List[ExperienceView] = Field(default_factory=list, description="Work history")
    education: List[EducationView] = Field(default_factory=list, description="Educational background")
    languages: List[LanguageView] = Field(default_factory=list, description="Languages spoken")

class DerivedDatapointsView(BaseSchema):
    """Nested view for AI-derived business context."""
    pattern_tags: Optional[str] = Field(None, description="Comma-separated pattern tags (e.g., CPG, B2C)")
    business_type: List[str] = Field(default_factory=list, description="Business model types (e.g., B2B, B2C)")
    business_stage: Optional[str] = Field(None, description="Current stage (e.g., Established, Startup)")
    scale_scope: Optional[str] = Field(None, description="Geographic scale and market reach")

class CompanySchema(BaseSchema):
    """Clean, standalone view model strictly for company-level data."""
    name: str = Field(description="Company legal name")
    domain: Optional[str] = Field(None, description="Primary website domain")
    industry: Optional[str] = Field(None, description="Industry classification")
    
    # Scale Metrics
    size: Optional[str] = Field(None, description="Employee count range")
    employee_count: Optional[int] = Field(None, description="Exact employee count")
    annual_revenue: Optional[str] = Field(None, description="Annual revenue range")
    
    # Geography (Kept strict, dropping the massive locations array)
    locality: Optional[str] = Field(None, description="Headquarters city")
    country: Optional[str] = Field(None, description="Headquarters country code")
    
    # Context
    description: Optional[str] = Field(None, description="Company description or overview")
    specialties: List[str] = Field(default_factory=list, description="List of company specialties")
    derived_datapoints: Optional[DerivedDatapointsView] = Field(None, description="High-level business intelligence")

class PublicStatementView(BaseSchema):
    """View for attributable quotes and statements."""
    date: Optional[str] = Field(None, description="Year or date of the statement")
    quote: str = Field(description="Exact quote from the person")
    context: str = Field(description="Context or event where the quote was made")

class DepartmentProductView(BaseSchema):
    """Mapping of products relevant to the lead's specific department/remit."""
    product_name: str = Field(description="Name of the product or brand")
    status: str = Field(description="Status of relation: 'confirmed', 'likely', or 'excluded'")
    reasoning: Optional[str] = Field(None, description="Why this product is mapped to their scope")

class CareerTrajectoryView(BaseSchema):
    """Analysis of the lead's career progression and core expertise."""
    pattern: Optional[str] = Field(None, description="High-level summary of their career arc")
    progression: Optional[str] = Field(None, description="Detailed breakdown of their role evolution")
    expertise: List[str] = Field(default_factory=list, description="Core professional competencies")

class ReportingStructureView(BaseSchema):
    """Inferred or confirmed organizational placement."""
    division_name: Optional[str] = Field(None, description="Specific division or business unit")
    reports_to: Optional[str] = Field(None, description="Who this role likely reports to")
    direct_reports: Optional[str] = Field(None, description="Likely team structure managed by this role")

class ProfileSchema(BaseSchema):
    """Clean, standalone view model strictly for Role Intelligence and Context."""
    role_summary: Optional[str] = Field(alias="roleMeaningAtCompany_summary", default=None, description="Executive summary of what this role actually does")
    
    # Responsibilities & Authority
    day_to_day: List[str] = Field(default_factory=list, description="High-level day-to-day responsibilities")
    decision_authority: Optional[str] = Field(None, description="Summary of P&L or strategic decision-making power")
    
    # Organizational Context
    reporting_structure: Optional[ReportingStructureView] = Field(None, description="Where they sit in the org chart")
    department_products: List[DepartmentProductView] = Field(default_factory=list, description="Products directly under their purview")
    
    # Strategic Focus
    recent_initiatives: List[str] = Field(default_factory=list, description="Recent projects or active initiatives")
    strategic_priorities: List[str] = Field(default_factory=list, description="Core business priorities for this role")
    public_statements: List[PublicStatementView] = Field(default_factory=list, description="Public quotes and verified statements")
    
    # Career Context
    career_trajectory: Optional[CareerTrajectoryView] = Field(None, description="Analysis of their professional background")

class OverallScoreView(BaseSchema):
    """Top-level assessment of the product's visual strategy."""
    score: int = Field(description="Overall rating (0-10)")
    summary: str = Field(description="High-level strategic summary")

class ImageQualityView(BaseSchema):
    """Technical evaluation of a specific image."""
    score: int = Field(description="Technical quality score (0-10)")
    strengths: List[str] = Field(default_factory=list, description="Visual strengths")
    weaknesses: List[str] = Field(default_factory=list, description="Visual weaknesses and conversion risks")

class MainImageView(BaseSchema):
    """Analysis of the primary product hero image."""
    technical_quality: ImageQualityView = Field(alias="technicalQuality", description="Technical breakdown of the hero image")

class MobileExperienceView(BaseSchema):
    """Evaluation of how the product displays on mobile devices."""
    score: int = Field(description="Mobile experience score (0-10)")
    issues: List[str] = Field(default_factory=list, description="Specific mobile rendering or UX issues")

class GalleryFlowView(BaseSchema):
    """Analysis of the secondary image gallery narrative."""
    story_arc: Optional[str] = Field(None, alias="storyArc", description="Narrative progression of the gallery")
    progression: Optional[str] = Field(None, description="How the images move the buyer toward purchase")
    coverage_gaps: List[str] = Field(default_factory=list, alias="coverageGaps", description="Missing information in the visual story")
    mobile_experience: Optional[MobileExperienceView] = Field(None, alias="mobileExperience", description="Mobile-specific gallery analysis")

class APlusContentView(BaseSchema):
    """Analysis of enhanced brand content (e.g., Amazon A+)."""
    present: bool = Field(default=False, description="Whether A+ content exists")
    assessment: Optional[str] = Field(None, description="Evaluation of the existing A+ content or lack thereof")
    missed_opportunities: List[str] = Field(default_factory=list, alias="missedOpportunities", description="Specific content that should be added")

class ImageDetailView(BaseSchema):
    url: str = Field(description="URL of the specific image")
    why: str = Field(description="Strategic reasoning for this highlight")

class OpportunityDetailView(BaseSchema):
    how: str = Field(description="Actionable execution steps")
    description: str = Field(description="What the opportunity entails")

class TopImagesView(BaseSchema):
    """The most critical visual highlights from the listing."""
    best_image: Optional[ImageDetailView] = Field(None, alias="bestImage", description="The strongest image asset")
    worst_image: Optional[ImageDetailView] = Field(None, alias="worstImage", description="The weakest or most damaging image asset")
    biggest_opportunity: Optional[OpportunityDetailView] = Field(None, alias="biggestOpportunity", description="The highest-leverage visual fix")

class CompetitiveBenchmarkView(BaseSchema):
    """How this product's presentation compares to direct competitors."""
    relative_position: str = Field(alias="relativePosition", description="Position vs competitors (e.g., 'below', 'above')")
    strengths_vs_competitors: List[str] = Field(default_factory=list, alias="strengthsVsCompetitors", description="Where this product visually wins")
    weaknesses_vs_competitors: List[str] = Field(default_factory=list, alias="weaknessesVsCompetitors", description="Where competitors are visually winning")
    competitor_tactics_not_used: List[str] = Field(default_factory=list, alias="competitorTacticsNotUsed", description="Successful tactics used by rivals")

class RecommendationView(BaseSchema):
    """Actionable strategic advice."""
    effort: str = Field(description="Estimated implementation effort")
    priority: str = Field(description="Strategic priority level")
    expected_impact: str = Field(alias="expectedImpact", description="Predicted outcome of the change")
    recommendation: str = Field(description="The specific action to take")

class ProductSchema(BaseSchema):
    """Clean, standalone view model strictly for Product visual and conversion intelligence."""
    overall_score: OverallScoreView = Field(alias="overallScore", description="Top-level score and summary")
    main_image: MainImageView = Field(alias="mainImage", description="Hero image analysis")
    gallery_flow: Optional[GalleryFlowView] = Field(None, alias="galleryFlow", description="Secondary image analysis")
    a_plus_content: Optional[APlusContentView] = Field(None, alias="aPlusContent", description="Enhanced content analysis")
    top_images: Optional[TopImagesView] = Field(None, alias="topThreeImages", description="Key visual highlights")
    competitive_benchmark: Optional[CompetitiveBenchmarkView] = Field(None, alias="competitiveBenchmark", description="Competitor comparison")
    prioritized_recommendations: List[RecommendationView] = Field(default_factory=list, alias="prioritizedRecommendations", description="Action steps")

class PainPointDetailView(BaseSchema):
    """Detailed breakdown of a specific pain point."""
    pain_point: str = Field(alias="painPoint", description="Brief name of the pain point")
    description: str = Field(description="Detailed explanation of the pain point")
    urgency: str = Field(description="Urgency level (e.g., 'critical', 'high', 'medium', 'low')")
    frequency: str = Field(description="How often the pain occurs (e.g., 'daily', 'weekly', 'monthly')")
    impact: str = Field(description="Consequences if the pain is not addressed")
    evidence: str = Field(description="Supporting evidence or reasoning")
    evidence_level: str = Field(alias="evidenceLevel", description="Strength of evidence (e.g., 'DIRECT', 'INFERRED_STRONG')")

class TopPainsSummaryView(BaseSchema):
    """Executive summary of the most critical friction points."""
    most_urgent: str = Field(alias="mostUrgent", description="Pain point requiring immediate attention")
    most_frequent: str = Field(alias="mostFrequent", description="Pain point that occurs most often")
    most_impactful: str = Field(alias="mostImpactful", description="Pain point with the greatest potential consequence")

class PainPointsSchema(BaseSchema):
    """Clean, standalone view model strictly for Pain Point analysis."""
    notes: Optional[str] = Field(None, description="High-level analytical notes or caveats")
    role_scope: Optional[str] = Field(None, description="The exact operational scope these pain points apply to")
    
    top_pains: TopPainsSummaryView = Field(alias="topPains", description="Summary of the core critical pains")
    
    # We use a Dict to capture dynamic categories like "market", "operational", "performance"
    categories: Dict[str, List[PainPointDetailView]] = Field(
        alias="painPoints", 
        description="Pain points grouped by category keys (e.g., 'market', 'operational')"
    )


# --- 1. Message Architecture Sub-Models ---
class ArchitectureElementView(BaseSchema):
    """Generic view for a message component and its strategic rationale."""
    text: str = Field(description="The actual copy to use")
    rationale: Optional[str] = Field(None, alias="whyItWorks", description="Strategic reasoning for this copy")
    source: Optional[str] = Field(None, description="Data source backing this copy")
    logic: Optional[str] = Field(None, description="Logical connection to the value prop")
    friction: Optional[str] = Field(None, description="Level of friction in the ask")

class MessageArchitectureView(BaseSchema):
    """Core message structure broken down into its functional parts."""
    hook: ArchitectureElementView = Field(description="Opening attention grabber")
    bridge: ArchitectureElementView = Field(description="Connection between hook and solution")
    proof: ArchitectureElementView = Field(description="Evidence of capability")
    ask: ArchitectureElementView = Field(description="Specific call-to-action")

# --- 2. Channel Strategy Sub-Models ---
class ChannelFormatView(BaseSchema):
    style: str = Field(description="Recommended tone/style")
    length: str = Field(description="Recommended length")
    reasoning: Optional[str] = Field(None, description="Why this format works")

class ChannelTimingView(BaseSchema):
    best_time: str = Field(alias="bestTime", description="Optimal outreach windows")
    avoid_time: str = Field(alias="avoidTime", description="Times to strictly avoid")
    reasoning: Optional[str] = Field(None, description="Logic behind the timing")

class ChannelStrategyView(BaseSchema):
    """Logistical plan for delivering the message."""
    primary_channel: str = Field(alias="primaryChannel", description="Main outreach channel")
    secondary_channel: str = Field(alias="secondaryChannel", description="Fallback or reinforcement channel")
    format: ChannelFormatView = Field(description="Format constraints")
    timing: ChannelTimingView = Field(description="When to send")

# --- 3. Tactical Sub-Models ---
class AngleVariantView(BaseSchema):
    """Alternative messaging angles based on different pains."""
    angle_name: str = Field(alias="angleName", description="Internal name for this angle")
    target_pain: str = Field(alias="targetPain", description="The specific pain point addressed")
    opening: str = Field(description="Suggested opening sentence")
    framing: str = Field(description="How to frame the value proposition")
    proof_point: str = Field(alias="proofPoint", description="Specific evidence to use")
    cta: str = Field(description="Angle-specific call to action")

class RiskMitigationView(BaseSchema):
    """Potential friction points in the outreach and how to bypass them."""
    risk: str = Field(description="The potential objection or risk")
    impact: str = Field(description="Consequence level (high, medium, low)")
    likelihood: str = Field(description="Probability of occurrence")
    mitigation: str = Field(description="Tactical advice to bypass the risk")

class PainSolutionMapView(BaseSchema):
    """Direct mapping of user pains to your specific solutions."""
    their_pain: str = Field(alias="theirPain", description="The prospect's specific problem")
    your_solution: str = Field(alias="yourSolution", description="How your offering solves it")
    evidence_level: str = Field(alias="evidenceLevel", description="Strength of the connection")
    connection_logic: str = Field(alias="connectionLogic", description="The strategic bridge between the two")

class StrategicPositioningView(BaseSchema):
    """The overarching narrative strategy."""
    core_thesis: str = Field(alias="coreThesis", description="The central argument for why you should connect")
    pain_solution_map: List[PainSolutionMapView] = Field(alias="painSolutionMap", default_factory=list, description="Detailed pain-to-solution mappings")

# --- 4. The Main Communication Schema ---
class CommunicationSchema(BaseSchema):
    """Clean, standalone view model strictly for Outreach and Communication Strategy."""
    notes: Optional[str] = Field(None, description="High-level strategic caveats or context")
    strategic_positioning: StrategicPositioningView = Field(alias="strategicPositioning", description="Core positioning thesis and mapping")
    message_architecture: MessageArchitectureView = Field(alias="messageArchitecture", description="Structural breakdown of the ideal message")
    channel_strategy: ChannelStrategyView = Field(alias="channelStrategy", description="Logistical delivery plan")
    angle_variants: List[AngleVariantView] = Field(alias="angleVariants", default_factory=list, description="Alternative outreach angles")
    risk_mitigation: List[RiskMitigationView] = Field(alias="riskMitigation", default_factory=list, description="Objection handling and risk management")
