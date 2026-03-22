/** Enrichment job status enum — mirrors backend EnrichmentJobStatus */
export type EnrichmentJobStatus = "pending" | "completed";

/** Payload type identifiers matching Clay's payload_type field */
export type PayloadType =
  | "person"
  | "company"
  | "profile"
  | "products"
  | "painpoints"
  | "communication";

/** Payload metadata for the 3x2 grid */
export interface PayloadInfo {
  key: PayloadType;
  label: string;
  payloadField: keyof Pick<
    EnrichmentJobResponse,
    | "payload_1"
    | "payload_2"
    | "payload_3"
    | "payload_4"
    | "payload_5"
    | "payload_6"
  >;
  endpoint: string;
}

/** The 6 payload definitions */
export const PAYLOAD_DEFINITIONS: PayloadInfo[] = [
  {
    key: "person",
    label: "Person",
    payloadField: "payload_1",
    endpoint: "person",
  },
  {
    key: "company",
    label: "Company",
    payloadField: "payload_2",
    endpoint: "company",
  },
  {
    key: "profile",
    label: "Profile",
    payloadField: "payload_3",
    endpoint: "profile",
  },
  {
    key: "products",
    label: "Products",
    payloadField: "payload_4",
    endpoint: "products",
  },
  {
    key: "painpoints",
    label: "Pain Points",
    payloadField: "payload_5",
    endpoint: "painpoints",
  },
  {
    key: "communication",
    label: "Communication",
    payloadField: "payload_6",
    endpoint: "communication",
  },
];

// ---------------------------------------------------------------------------
// Person Schema (payload 1)
// ---------------------------------------------------------------------------

/** Experience entry — mirrors backend ExperienceView */
export interface ExperienceView {
  title: string;
  company: string;
  start_date: string | null;
  end_date: string | null;
  is_current: boolean;
  summary: string | null;
}

/** Education entry — mirrors backend EducationView */
export interface EducationView {
  school_name: string;
  degree: string | null;
  field_of_study: string | null;
  start_date: string | null;
  end_date: string | null;
}

/** Language entry — mirrors backend LanguageView */
export interface LanguageView {
  language: string;
  proficiency: string | null;
}

/** Person view — mirrors backend PersonSchema */
export interface PersonSchema {
  full_name: string;
  first_name: string | null;
  last_name: string | null;
  linkedin_url: string | null;
  location: string | null;
  summary: string | null;
  experience: ExperienceView[];
  education: EducationView[];
  languages: LanguageView[];
}

// ---------------------------------------------------------------------------
// Company Schema (payload 2)
// ---------------------------------------------------------------------------

/** AI-derived business context — mirrors backend DerivedDatapointsView */
export interface DerivedDatapointsView {
  pattern_tags: string | null;
  business_type: string[];
  business_stage: string | null;
  scale_scope: string | null;
}

/** Company view — mirrors backend CompanySchema */
export interface CompanySchema {
  name: string;
  domain: string | null;
  industry: string | null;
  size: string | null;
  employee_count: number | null;
  annual_revenue: string | null;
  locality: string | null;
  country: string | null;
  description: string | null;
  specialties: string[];
  derived_datapoints: DerivedDatapointsView | null;
}

// ---------------------------------------------------------------------------
// Profile Schema (payload 3)
// ---------------------------------------------------------------------------

/** Attributable quote — mirrors backend PublicStatementView */
export interface PublicStatementView {
  date: string | null;
  quote: string;
  context: string;
}

/** Department product mapping — mirrors backend DepartmentProductView */
export interface DepartmentProductView {
  product_name: string;
  status: string;
  reasoning: string | null;
}

/** Career trajectory analysis — mirrors backend CareerTrajectoryView */
export interface CareerTrajectoryView {
  pattern: string | null;
  progression: string | null;
  expertise: string[];
}

/** Reporting structure — mirrors backend ReportingStructureView */
export interface ReportingStructureView {
  division_name: string | null;
  reports_to: string | null;
  direct_reports: string | null;
}

/** Profile / role intelligence — mirrors backend ProfileSchema */
export interface ProfileSchema {
  role_summary: string | null;
  day_to_day: string[];
  decision_authority: string | null;
  reporting_structure: ReportingStructureView | null;
  department_products: DepartmentProductView[];
  recent_initiatives: string[];
  strategic_priorities: string[];
  public_statements: PublicStatementView[];
  career_trajectory: CareerTrajectoryView | null;
}

// ---------------------------------------------------------------------------
// Product Schema (payload 4)
// ---------------------------------------------------------------------------

/** Overall product score — mirrors backend OverallScoreView */
export interface OverallScoreView {
  score: number;
  summary: string;
}

/** Image quality assessment — mirrors backend ImageQualityView */
export interface ImageQualityView {
  score: number;
  strengths: string[];
  weaknesses: string[];
}

/** Main image analysis — mirrors backend MainImageView */
export interface MainImageView {
  technical_quality: ImageQualityView;
}

/** Mobile experience — mirrors backend MobileExperienceView */
export interface MobileExperienceView {
  score: number;
  issues: string[];
}

/** Gallery flow — mirrors backend GalleryFlowView */
export interface GalleryFlowView {
  story_arc: string | null;
  progression: string | null;
  coverage_gaps: string[];
  mobile_experience: MobileExperienceView | null;
}

/** A+ content analysis — mirrors backend APlusContentView */
export interface APlusContentView {
  present: boolean;
  assessment: string | null;
  missed_opportunities: string[];
}

/** Image detail — mirrors backend ImageDetailView */
export interface ImageDetailView {
  url: string;
  why: string;
}

/** Opportunity detail — mirrors backend OpportunityDetailView */
export interface OpportunityDetailView {
  how: string;
  description: string;
}

/** Top images — mirrors backend TopImagesView */
export interface TopImagesView {
  best_image: ImageDetailView | null;
  worst_image: ImageDetailView | null;
  biggest_opportunity: OpportunityDetailView | null;
}

/** Competitive benchmark — mirrors backend CompetitiveBenchmarkView */
export interface CompetitiveBenchmarkView {
  relative_position: string;
  strengths_vs_competitors: string[];
  weaknesses_vs_competitors: string[];
  competitor_tactics_not_used: string[];
}

/** Recommendation — mirrors backend RecommendationView */
export interface RecommendationView {
  effort: string;
  priority: string;
  expected_impact: string;
  recommendation: string;
}

/** Product schema — mirrors backend ProductSchema */
export interface ProductSchema {
  overall_score: OverallScoreView;
  main_image: MainImageView;
  gallery_flow: GalleryFlowView | null;
  a_plus_content: APlusContentView | null;
  top_images: TopImagesView | null;
  competitive_benchmark: CompetitiveBenchmarkView | null;
  prioritized_recommendations: RecommendationView[];
}

// ---------------------------------------------------------------------------
// Pain Points Schema (payload 5)
// ---------------------------------------------------------------------------

/** Pain point detail — mirrors backend PainPointDetailView */
export interface PainPointDetailView {
  pain_point: string;
  description: string;
  urgency: string;
  frequency: string;
  impact: string;
  evidence: string;
  evidence_level: string;
}

/** Top pains summary — mirrors backend TopPainsSummaryView */
export interface TopPainsSummaryView {
  most_urgent: string;
  most_frequent: string;
  most_impactful: string;
}

/** Pain points schema — mirrors backend PainPointsSchema.
 *  categories is a dynamic dict keyed by category name (e.g. "market", "operational"). */
export interface PainPointsSchema {
  notes: string | null;
  role_scope: string | null;
  top_pains: TopPainsSummaryView;
  categories: Record<string, PainPointDetailView[]>;
}

// ---------------------------------------------------------------------------
// Communication Schema (payload 6)
// ---------------------------------------------------------------------------

/** Message architecture element — simplified version */
export interface ArchitectureElementView {
  text: string;
  source: string | null;
}

/** Message architecture — mirrors backend MessageArchitectureView */
export interface MessageArchitectureView {
  hook: ArchitectureElementView;
  bridge: ArchitectureElementView;
  proof: ArchitectureElementView;
  ask: ArchitectureElementView;
}

/** Channel format — mirrors backend ChannelFormatView */
export interface ChannelFormatView {
  style: string;
  length: string;
  reasoning: string | null;
}

/** Channel timing — mirrors backend ChannelTimingView */
export interface ChannelTimingView {
  best_time: string;
  avoid_time: string;
  reasoning: string | null;
}

/** Channel strategy — mirrors backend ChannelStrategyView */
export interface ChannelStrategyView {
  primary_channel: string;
  secondary_channel: string;
  format: ChannelFormatView;
  timing: ChannelTimingView;
}

/** Angle variant — mirrors backend AngleVariantView */
export interface AngleVariantView {
  angle_name: string;
  target_pain: string;
  opening: string;
  framing: string;
  proof_point: string;
  cta: string;
}

/** Risk mitigation — mirrors backend RiskMitigationView */
export interface RiskMitigationView {
  risk: string;
  impact: string;
  likelihood: string;
  mitigation: string;
}

/** Pain-solution map — mirrors backend PainSolutionMapView */
export interface PainSolutionMapView {
  their_pain: string;
  your_solution: string;
  evidence_level: string;
  connection_logic: string;
}

/** Strategic positioning — mirrors backend StrategicPositioningView */
export interface StrategicPositioningView {
  core_thesis: string;
  pain_solution_map: PainSolutionMapView[];
}

/** Communication schema — mirrors backend CommunicationSchema */
export interface CommunicationSchema {
  notes: string | null;
  strategic_positioning: StrategicPositioningView;
  message_architecture: MessageArchitectureView;
  channel_strategy: ChannelStrategyView;
  angle_variants: AngleVariantView[];
  risk_mitigation: RiskMitigationView[];
}

// ---------------------------------------------------------------------------
// API response types
// ---------------------------------------------------------------------------

/** Response from POST /webhooks/trigger (202 Accepted) */
export interface EnrichmentTriggerResponse {
  status: "accepted";
  job_id: string;
  email: string;
  message: string;
}

/** Full enrichment job record from GET /api/enrichment/jobs/{job_id} */
export interface EnrichmentJobResponse {
  job_id: string;
  email: string;
  status: EnrichmentJobStatus;
  payload_1: Record<string, unknown> | null;
  payload_2: Record<string, unknown> | null;
  payload_3: Record<string, unknown> | null;
  payload_4: Record<string, unknown> | null;
  payload_5: Record<string, unknown> | null;
  payload_6: Record<string, unknown> | null;
  created_at: string;
  updated_at: string | null;
}

/** Job summary from GET /api/enrichment/completed */
export interface JobSummary {
  job_id: string;
  email: string;
  status: EnrichmentJobStatus;
}

// ---------------------------------------------------------------------------
// Sequence types
// ---------------------------------------------------------------------------

/** Touch in Claude-generated sequence */
export interface TouchView {
  objective: string;
  touch_number: number;
  example_snippet: string;
  ai_prompt_instruction: string;
}

/** Account strategy analysis */
export interface AccountStrategyView {
  personalization_angle: string;
  identified_core_pain_point: string;
}

/** Claude outreach view — full sequence response */
export interface ClaudeOutreachView {
  touches: TouchView[];
  account_strategy_analysis: AccountStrategyView;
}

/** Response from POST /api/sequence/generate/{job_id} (202) */
export interface SequenceGenerationResponse {
  job_id: string;
  sequence_id: string;
  status: "accepted";
  message: string;
}

/** Sequence job status enum */
export type CampaignSequenceStatus =
  | "pending"
  | "generating"
  | "completed"
  | "failed";

// ---------------------------------------------------------------------------
// Content Pipeline types
// ---------------------------------------------------------------------------

/** Asset status enum — mirrors backend AssetStatus */
export type AssetStatus = "uploaded" | "completed" | "failed" | "received";

/** Content snack type — mirrors backend ContentSnack */
export type ContentSnackType = "linkedin_post" | "email_pill";

/** Content snack response — mirrors backend ContentSnackResponse */
export interface ContentSnackResponse {
  id: string;
  asset_id: string;
  content_type: ContentSnackType;
  content_text: string;
  content_metadata: Record<string, unknown> | null;
  created_at: string;
  updated_at: string;
}

/** Asset upload response — mirrors backend AssetUploadResponse */
export interface AssetUploadResponse {
  asset_id: string;
  filename: string;
  original_filename: string | null;
  sequence_number: number | null;
  storage_url: string;
  status: AssetStatus;
  message: string;
}

/** Asset content response — mirrors backend AssetContentResponse */
export interface AssetContentResponse {
  asset_id: string;
  content_items: ContentSnackResponse[];
  total_count: number;
  linkedin_post_count: number;
  email_pill_count: number;
}

/** Marketing asset response — mirrors backend MarketingAssetResponse */
export interface MarketingAssetResponse {
  id: string;
  filename: string;
  original_filename: string | null;
  sequence_number: number | null;
  storage_url: string;
  status: AssetStatus;
  webhook_payload: Record<string, unknown> | null;
  created_at: string;
  updated_at: string;
}

/** Asset with snacks response — mirrors backend AssetWithSnacksResponse */
export interface AssetWithSnacksResponse {
  asset: MarketingAssetResponse;
  snacks: ContentSnackResponse[];
}
