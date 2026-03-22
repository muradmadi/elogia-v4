import { useEffect, useState } from "react";
import { useStore } from "@nanostores/react";
import { Button } from "../ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "../ui/card";
import { Skeleton } from "../ui/skeleton";
import { Alert, AlertDescription, AlertTitle } from "../ui/alert";
import {
  getPersonSchema,
  getCompanySchema,
  getProfileSchema,
  getProductSchema,
  getPainPointsSchema,
  getCommunicationSchema,
} from "../../services/enrichmentApi";
import {
  $currentJobId,
  $isDetailModalOpen,
  $selectedPayloadType,
} from "../../stores/enrichment";
import type {
  PayloadType,
  PersonSchema,
  CompanySchema,
  ProfileSchema,
  ProductSchema,
  PainPointsSchema,
  CommunicationSchema,
} from "../../lib/types";

// Utility function to format dates
function formatDate(dateStr: string | null): string {
  if (!dateStr) return "—";
  
  // Try to parse the date
  const date = new Date(dateStr);
  if (isNaN(date.getTime())) return dateStr;
  
  // Format as "Month Year" (e.g., "January 2023")
  const options: Intl.DateTimeFormatOptions = { year: "numeric", month: "long" };
  return date.toLocaleDateString("en-US", options);
}

// Utility function to convert language name to country flag emoji
function getLanguageFlag(language: string): string {
  const languageToFlag: Record<string, string> = {
    // English variants
    "english": "🇺🇸",
    "english (us)": "🇺🇸",
    "english (uk)": "🇬🇧",
    "english (australian)": "🇦🇺",
    "english (canadian)": "🇨🇦",
    
    // Spanish variants
    "spanish": "🇪🇸",
    "spanish (spain)": "🇪🇸",
    "spanish (latin america)": "🇲🇽",
    
    // Other languages
    "french": "🇫🇷",
    "german": "🇩🇪",
    "italian": "🇮🇹",
    "portuguese": "🇵🇹",
    "portuguese (brazil)": "🇧🇷",
    "dutch": "🇳🇱",
    "polish": "🇵🇱",
    "russian": "🇷🇺",
    "chinese": "🇨🇳",
    "mandarin": "🇨🇳",
    "cantonese": "🇭🇰",
    "japanese": "🇯🇵",
    "korean": "🇰🇷",
    "arabic": "🇸🇦",
    "hindi": "🇮🇳",
    "turkish": "🇹🇷",
    "swedish": "🇸🇪",
    "norwegian": "🇳🇴",
    "danish": "🇩🇰",
    "finnish": "🇫🇮",
    "greek": "🇬🇷",
    "hebrew": "🇮🇱",
    "thai": "🇹🇭",
    "vietnamese": "🇻🇳",
    "indonesian": "🇮🇩",
    "malay": "🇲🇾",
    "tagalog": "🇵🇭",
  };
  
  const normalizedLang = language.toLowerCase().trim();
  return languageToFlag[normalizedLang] || "🏳️";
}

// Utility function to convert string to title case
function toTitleCase(str: string | null): string {
  if (!str) return "—";
  return str.replace(/\w\S*/g, (txt) => {
    return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();
  });
}

export function PayloadDetailModal() {
  const isOpen = useStore($isDetailModalOpen);
  const payloadType = useStore($selectedPayloadType);
  const jobId = useStore($currentJobId);

  const onClose = () => {
    $isDetailModalOpen.set(false);
    $selectedPayloadType.set(null);
  };
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [payloadData, setPayloadData] = useState<
    | PersonSchema
    | CompanySchema
    | ProfileSchema
    | ProductSchema[]
    | PainPointsSchema
    | CommunicationSchema
    | null
  >(null);

  useEffect(() => {
    if (!isOpen || !jobId || !payloadType) return;

    const fetchPayload = async () => {
      setIsLoading(true);
      setError(null);

      try {
        let data: typeof payloadData = null;

        switch (payloadType) {
          case "person":
            data = await getPersonSchema(jobId);
            break;
          case "company":
            data = await getCompanySchema(jobId);
            break;
          case "profile":
            data = await getProfileSchema(jobId);
            break;
          case "products":
            data = await getProductSchema(jobId);
            break;
          case "painpoints":
            data = await getPainPointsSchema(jobId);
            break;
          case "communication":
            data = await getCommunicationSchema(jobId);
            break;
        }

        setPayloadData(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to fetch payload");
      } finally {
        setIsLoading(false);
      }
    };

    fetchPayload();
  }, [isOpen, jobId, payloadType]);

  if (!isOpen || !payloadType) return null;

  const getPayloadLabel = (type: PayloadType): string => {
    const labels: Record<PayloadType, string> = {
      person: "Person Data",
      company: "Company Data",
      profile: "Profile Data",
      products: "Products Data",
      painpoints: "Pain Points Data",
      communication: "Communication Data",
    };
    return labels[type];
  };

  const handleModalClick = (e: React.MouseEvent) => {
    e.stopPropagation();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/30"
        onClick={onClose}
      />

      {/* Modal */}
      <Card
        className="relative z-10 w-full max-w-3xl max-h-[90vh] flex flex-col"
        onClick={handleModalClick}
      >
        <CardHeader className="flex flex-row items-center justify-between border-b">
          <CardTitle>{getPayloadLabel(payloadType)}</CardTitle>
          <Button variant="ghost" size="sm" onClick={onClose}>
            ✕
          </Button>
        </CardHeader>

        <CardContent className="flex-1 overflow-hidden p-0">
          {isLoading ? (
            <div className="p-6 space-y-4">
              <Skeleton className="h-6 w-3/4" />
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-2/3" />
            </div>
          ) : error ? (
            <Alert variant="destructive" className="m-4">
              <AlertTitle>Error</AlertTitle>
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          ) : !payloadData ? (
            <div className="p-6 text-center text-muted-foreground">
              No data available for this payload type yet.
            </div>
          ) : (
            <div className="custom-scrollbar overflow-y-auto max-h-[60vh] p-6">
              {(() => {
                try {
                  return renderPayloadContent(payloadType, payloadData);
                } catch (err) {
                  console.error('Error rendering payload content:', err);
                  return (
                    <Alert variant="destructive">
                      <AlertTitle>Rendering Error</AlertTitle>
                      <AlertDescription>
                        Failed to render payload data: {err instanceof Error ? err.message : String(err)}
                      </AlertDescription>
                    </Alert>
                  );
                }
              })()}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

// Helper function to normalize field names from camelCase to snake_case
function normalizeFieldNames(data: any): any {
  if (!data || typeof data !== 'object') return data;
  
  if (Array.isArray(data)) {
    return data.map(item => normalizeFieldNames(item));
  }
  
  const normalized: any = {};
  for (const [key, value] of Object.entries(data)) {
    let snakeKey = key;
    
    // Special cases for pain points data
    if (key === 'roleMeaningAtCompany_summary') {
      snakeKey = 'role_summary';
    } else if (key === 'painPoints') {
      snakeKey = 'categories'; // Map painPoints to categories
    } else if (key === 'topPains') {
      snakeKey = 'top_pains'; // Map topPains to top_pains
    } else {
      // Convert camelCase to snake_case for other fields
      snakeKey = key.replace(/[A-Z]/g, letter => `_${letter.toLowerCase()}`);
    }
    
    // Recursively normalize nested objects
    normalized[snakeKey] = normalizeFieldNames(value);
  }
  return normalized;
}

// Helper function to render payload content based on type
function renderPayloadContent(
  type: PayloadType,
  data: any,
): React.ReactNode {
  // Handle null or undefined data
  if (!data) {
    return (
      <div className="p-6 text-center text-muted-foreground">
        No data available for this payload type yet.
      </div>
    );
  }

  try {
    // Normalize field names before rendering
    const normalizedData = normalizeFieldNames(data);
    
    switch (type) {
      case "person":
        return renderPersonContent(normalizedData as PersonSchema);
      case "company":
        return renderCompanyContent(normalizedData as CompanySchema);
      case "profile":
        return renderProfileContent(normalizedData as ProfileSchema);
      case "products":
        return renderProductsContent(normalizedData as ProductSchema[]);
      case "painpoints":
        return renderPainPointsContent(normalizedData as PainPointsSchema);
      case "communication":
        return renderCommunicationContent(normalizedData as CommunicationSchema);
      default:
        return null;
    }
  } catch (err) {
return (
      <div className="p-6">
        <Alert variant="destructive">
          <AlertTitle>Rendering Error</AlertTitle>
          <AlertDescription>
            Failed to render {type} data: {err instanceof Error ? err.message : String(err)}
          </AlertDescription>
        </Alert>
        <pre className="mt-4 p-4 bg-muted text-xs overflow-auto">
          {JSON.stringify(data, null, 2)}
        </pre>
      </div>
    );
  }
}

// TEMPLATE 1: PERSON (payload_1)
function renderPersonContent(data: PersonSchema) {
  // Safely access properties with defaults
  const experience = data.experience || [];
  const education = data.education || [];
  const languages = data.languages || [];
  
  // Get 3 most recent jobs (experience is typically sorted by most recent first)
  const recentJobs = experience.slice(0, 3);
  
  // Get most recent education (first entry)
  const recentEducation = education.length > 0 ? education[0] : null;

  return (
    <div className="space-y-6">
      {/* Basic Information Section */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold">Basic Information</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <p className="text-sm text-muted-foreground">Name</p>
            <p className="font-medium">{data.full_name || "—"}</p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Location</p>
            <p className="font-medium">{data.location || "—"}</p>
          </div>
        </div>
        {data.summary && (
          <div>
            <p className="text-sm text-muted-foreground">Summary</p>
            <p className="font-medium">{data.summary}</p>
          </div>
        )}
        {data.linkedin_url && (
          <div className="flex items-center gap-2">
            <a
              href={data.linkedin_url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 text-blue-600 hover:text-blue-800"
            >
              <svg className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
                <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
              </svg>
              <span>LinkedIn Profile</span>
            </a>
          </div>
        )}
      </div>

      {/* Experience Section */}
      <div>
        <h3 className="text-lg font-semibold mb-3">Recent Experience</h3>
        {recentJobs.length > 0 ? (
          <div className="space-y-4">
            {recentJobs.map((exp, idx) => (
              <Card key={idx} className="p-4">
                <div className="space-y-2">
                  <p className="font-medium">{exp.title}</p>
                  <p className="text-sm text-muted-foreground">{exp.company}</p>
                  <p className="text-sm text-muted-foreground">
                    {formatDate(exp.start_date)} — {exp.end_date ? formatDate(exp.end_date) : "Present"}
                  </p>
                  {exp.summary && (
                    <p className="text-sm mt-2">{exp.summary}</p>
                  )}
                </div>
              </Card>
            ))}
          </div>
        ) : (
          <p className="text-muted-foreground">No experience data</p>
        )}
      </div>

      {/* Education Section */}
      <div>
        <h3 className="text-lg font-semibold mb-3">Education</h3>
        {recentEducation ? (
          <Card className="p-4">
            <div className="space-y-2">
              <p className="font-medium">{recentEducation.school_name}</p>
              <p className="text-sm text-muted-foreground">
                {toTitleCase(recentEducation.degree)}
                {recentEducation.field_of_study && ` — ${recentEducation.field_of_study}`}
              </p>
              <p className="text-sm text-muted-foreground">
                {formatDate(recentEducation.start_date)} — {formatDate(recentEducation.end_date)}
              </p>
            </div>
          </Card>
        ) : (
          <p className="text-muted-foreground">No education data</p>
        )}
      </div>

      {/* Languages Section */}
      <div>
        <h3 className="text-lg font-semibold mb-3">Languages</h3>
        {data.languages.length > 0 ? (
          <div className="flex flex-wrap gap-2">
            {data.languages.map((lang, idx) => (
              <div key={idx} className="inline-flex items-center gap-2 bg-muted px-3 py-1.5 rounded-full">
                <span>{getLanguageFlag(lang.language)}</span>
                <span className="font-medium">{lang.language}</span>
                {lang.proficiency && (
                  <span className="text-xs text-muted-foreground">({lang.proficiency})</span>
                )}
              </div>
            ))}
          </div>
        ) : (
          <p className="text-muted-foreground">No language data</p>
        )}
      </div>
    </div>
  );
}

// TEMPLATE 2: COMPANY (payload_2)
function renderCompanyContent(data: CompanySchema) {
  return (
    <div className="space-y-6">
      {/* Basic Information Section */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold">Basic Information</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <p className="text-sm text-muted-foreground">Name</p>
            <p className="font-medium">{data.name || "—"}</p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Domain</p>
            <p className="font-medium">{data.domain || "—"}</p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Industry</p>
            <p className="font-medium">{data.industry || "—"}</p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Size</p>
            <p className="font-medium">{data.size || "—"}</p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Employee Count</p>
            <p className="font-medium">{data.employee_count ?? "—"}</p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Annual Revenue</p>
            <p className="font-medium">{data.annual_revenue || "—"}</p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Locality</p>
            <p className="font-medium">{data.locality || "—"}</p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Country</p>
            <p className="font-medium">{data.country || "—"}</p>
          </div>
        </div>
        {data.description && (
          <div>
            <p className="text-sm text-muted-foreground">Description</p>
            <p className="font-medium">{data.description}</p>
          </div>
        )}
      </div>

      {/* Specialties Section */}
      <div>
        <h3 className="text-lg font-semibold mb-3">Specialties</h3>
        {data.specialties.length > 0 ? (
          <div className="flex flex-wrap gap-2">
            {data.specialties.map((specialty, idx) => (
              <span key={idx} className="inline-flex items-center px-3 py-1.5 bg-muted rounded-full text-sm">
                {specialty}
              </span>
            ))}
          </div>
        ) : (
          <p className="text-muted-foreground">No specialties data</p>
        )}
      </div>
    </div>
  );
}

// TEMPLATE 3: PROFILE (payload_3)
function renderProfileContent(data: ProfileSchema) {
  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold mb-2">Role Summary</h3>
        <p>{data.role_summary || "—"}</p>
      </div>

      <div>
        <h3 className="text-lg font-semibold mb-2">Day to Day</h3>
        {data.day_to_day.length > 0 ? (
          <ul className="list-disc list-inside ml-4 space-y-1">
            {data.day_to_day.map((task, idx) => (
              <li key={idx}>{task}</li>
            ))}
          </ul>
        ) : (
          <p className="text-muted-foreground">No day-to-day data</p>
        )}
      </div>

      <div>
        <h3 className="text-lg font-semibold mb-2">Decision Authority</h3>
        <p>{data.decision_authority || "—"}</p>
      </div>

      <div>
        <h3 className="text-lg font-semibold mb-2">Reporting Structure</h3>
        {data.reporting_structure ? (
          <Card className="p-4 space-y-2">
            <p><strong>Division Name:</strong> {data.reporting_structure.division_name || "—"}</p>
            <p><strong>Reports To:</strong> {data.reporting_structure.reports_to || "—"}</p>
            <p><strong>Direct Reports:</strong> {data.reporting_structure.direct_reports || "—"}</p>
          </Card>
        ) : (
          <p className="text-muted-foreground">No reporting structure data</p>
        )}
      </div>

      <div>
        <h3 className="text-lg font-semibold mb-2">Department Products</h3>
        {data.department_products.filter(p => p.status !== "excluded").length > 0 ? (
          <div className="space-y-2">
            {data.department_products
              .filter(p => p.status !== "excluded")
              .map((product, idx) => (
                <Card key={idx} className="p-3">
                  <div className="space-y-1">
                    <p><strong>Product Name:</strong> {product.product_name}</p>
                    <p><strong>Status:</strong> {product.status}</p>
                    <p><strong>Reasoning:</strong> {product.reasoning || "—"}</p>
                  </div>
                </Card>
              ))}
          </div>
        ) : (
          <p className="text-muted-foreground">No department products data</p>
        )}
      </div>

      <div>
        <h3 className="text-lg font-semibold mb-2">Recent Initiatives</h3>
        {data.recent_initiatives.length > 0 ? (
          <ul className="list-disc list-inside ml-4 space-y-1">
            {data.recent_initiatives.map((initiative, idx) => (
              <li key={idx}>{initiative}</li>
            ))}
          </ul>
        ) : (
          <p className="text-muted-foreground">No recent initiatives data</p>
        )}
      </div>

      <div>
        <h3 className="text-lg font-semibold mb-2">Strategic Priorities</h3>
        {data.strategic_priorities.length > 0 ? (
          <ul className="list-disc list-inside ml-4 space-y-1">
            {data.strategic_priorities.map((priority, idx) => (
              <li key={idx}>{priority}</li>
            ))}
          </ul>
        ) : (
          <p className="text-muted-foreground">No strategic priorities data</p>
        )}
      </div>

      <div>
        <h3 className="text-lg font-semibold mb-2">Public Statements</h3>
        {(() => {
          const currentYear = new Date().getFullYear();
          const lastYear = currentYear - 1;
          
          const filteredStatements = data.public_statements.filter(stmt => {
            if (!stmt.date) return false;
            
            // Extract year from date string (handles various formats like "2024", "2024-03-15", "March 2024")
            const yearMatch = stmt.date.match(/\b(20\d{2})\b/);
            if (!yearMatch) return false;
            
            const statementYear = parseInt(yearMatch[1], 10);
            return statementYear === currentYear || statementYear === lastYear;
          });
          
          return filteredStatements.length > 0 ? (
            <div className="space-y-2">
              {filteredStatements.map((statement, idx) => (
                <Card key={idx} className="p-3">
                  <div className="space-y-1">
                    <p><strong>Date:</strong> {statement.date || "—"}</p>
                    <p><strong>Quote:</strong> {statement.quote}</p>
                    <p><strong>Context:</strong> {statement.context}</p>
                  </div>
                </Card>
              ))}
            </div>
          ) : (
            <p className="text-muted-foreground">No public statements from current or last year</p>
          );
        })()}
      </div>

      <div>
        <h3 className="text-lg font-semibold mb-2">Career Trajectory</h3>
        {data.career_trajectory ? (
          <Card className="p-4 space-y-2">
            <p><strong>Pattern:</strong> {data.career_trajectory.pattern || "—"}</p>
            <p><strong>Progression:</strong> {data.career_trajectory.progression || "—"}</p>
            <div>
              <p><strong>Expertise:</strong></p>
              {data.career_trajectory.expertise.length > 0 ? (
                <ul className="list-disc list-inside ml-4 space-y-1">
                  {data.career_trajectory.expertise.map((expertise, idx) => (
                    <li key={idx}>{expertise}</li>
                  ))}
                </ul>
              ) : (
                <p className="text-muted-foreground">No expertise data</p>
              )}
            </div>
          </Card>
        ) : (
          <p className="text-muted-foreground">No career trajectory data</p>
        )}
      </div>
    </div>
  );
}

// TEMPLATE 4: PRODUCTS (payload_4)
function renderProductsContent(data: ProductSchema[]) {
  if (!data || data.length === 0) {
    return <p className="text-muted-foreground">No products data</p>;
  }

  return (
    <div className="space-y-6">
      {data.map((product, productIdx) => (
        <Card key={productIdx} className="p-4 space-y-6">
          <div>
            <h3 className="text-lg font-semibold mb-2">Overall Score</h3>
            <Card className="p-3">
              <p><strong>Score:</strong> {product.overall_score.score}</p>
              <p><strong>Summary:</strong> {product.overall_score.summary}</p>
            </Card>
          </div>

          <div>
            <h3 className="text-lg font-semibold mb-2">Main Image</h3>
            <Card className="p-3 space-y-2">
              <p><strong>Technical Quality Score:</strong> {product.main_image.technical_quality.score}</p>
              <div>
                <p><strong>Strengths:</strong></p>
                {product.main_image.technical_quality.strengths.length > 0 ? (
                  <ul className="list-disc list-inside ml-4 space-y-1">
                    {product.main_image.technical_quality.strengths.map((strength, idx) => (
                      <li key={idx}>{strength}</li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-muted-foreground">No strengths data</p>
                )}
              </div>
              <div>
                <p><strong>Weaknesses:</strong></p>
                {product.main_image.technical_quality.weaknesses.length > 0 ? (
                  <ul className="list-disc list-inside ml-4 space-y-1">
                    {product.main_image.technical_quality.weaknesses.map((weakness, idx) => (
                      <li key={idx}>{weakness}</li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-muted-foreground">No weaknesses data</p>
                )}
              </div>
            </Card>
          </div>

          {product.gallery_flow && (
            <div>
              <h3 className="text-lg font-semibold mb-2">Gallery Flow</h3>
              <Card className="p-3 space-y-2">
                <p><strong>Story Arc:</strong> {product.gallery_flow.story_arc || "—"}</p>
                <p><strong>Progression:</strong> {product.gallery_flow.progression || "—"}</p>
                <div>
                  <p><strong>Coverage Gaps:</strong></p>
                  {product.gallery_flow.coverage_gaps.length > 0 ? (
                    <ul className="list-disc list-inside ml-4 space-y-1">
                      {product.gallery_flow.coverage_gaps.map((gap, idx) => (
                        <li key={idx}>{gap}</li>
                      ))}
                    </ul>
                  ) : (
                    <p className="text-muted-foreground">No coverage gaps data</p>
                  )}
                </div>
                {product.gallery_flow.mobile_experience && (
                  <div>
                    <p><strong>Mobile Experience Score:</strong> {product.gallery_flow.mobile_experience.score}</p>
                    <div>
                      <p><strong>Issues:</strong></p>
                      {product.gallery_flow.mobile_experience.issues.length > 0 ? (
                        <ul className="list-disc list-inside ml-4 space-y-1">
                          {product.gallery_flow.mobile_experience.issues.map((issue, idx) => (
                            <li key={idx}>{issue}</li>
                          ))}
                        </ul>
                      ) : (
                        <p className="text-muted-foreground">No mobile issues data</p>
                      )}
                    </div>
                  </div>
                )}
              </Card>
            </div>
          )}

          {product.a_plus_content && (
            <div>
              <h3 className="text-lg font-semibold mb-2">A+ Content</h3>
              <Card className="p-3 space-y-2">
                <p><strong>Present:</strong> {product.a_plus_content.present ? "Yes" : "No"}</p>
                <p><strong>Assessment:</strong> {product.a_plus_content.assessment || "—"}</p>
                <div>
                  <p><strong>Missed Opportunities:</strong></p>
                  {product.a_plus_content.missed_opportunities.length > 0 ? (
                    <ul className="list-disc list-inside ml-4 space-y-1">
                      {product.a_plus_content.missed_opportunities.map((opportunity, idx) => (
                        <li key={idx}>{opportunity}</li>
                      ))}
                    </ul>
                  ) : (
                    <p className="text-muted-foreground">No missed opportunities data</p>
                  )}
                </div>
              </Card>
            </div>
          )}

          {product.top_images && (
            <div>
              <h3 className="text-lg font-semibold mb-2">Top Images</h3>
              <Card className="p-3 space-y-3">
                {product.top_images.best_image && (
                  <div>
                    <p><strong>Best Image:</strong></p>
                    <p>URL: {product.top_images.best_image.url}</p>
                    <p>Why: {product.top_images.best_image.why}</p>
                  </div>
                )}
                {product.top_images.worst_image && (
                  <div>
                    <p><strong>Worst Image:</strong></p>
                    <p>URL: {product.top_images.worst_image.url}</p>
                    <p>Why: {product.top_images.worst_image.why}</p>
                  </div>
                )}
                {product.top_images.biggest_opportunity && (
                  <div>
                    <p><strong>Biggest Opportunity:</strong></p>
                    <p>How: {product.top_images.biggest_opportunity.how}</p>
                    <p>Description: {product.top_images.biggest_opportunity.description}</p>
                  </div>
                )}
              </Card>
            </div>
          )}

          {product.competitive_benchmark && (
            <div>
              <h3 className="text-lg font-semibold mb-2">Competitive Benchmark</h3>
              <Card className="p-3 space-y-2">
                <p><strong>Relative Position:</strong> {product.competitive_benchmark.relative_position}</p>
                <div>
                  <p><strong>Strengths vs Competitors:</strong></p>
                  {product.competitive_benchmark.strengths_vs_competitors.length > 0 ? (
                    <ul className="list-disc list-inside ml-4 space-y-1">
                      {product.competitive_benchmark.strengths_vs_competitors.map((strength, idx) => (
                        <li key={idx}>{strength}</li>
                      ))}
                    </ul>
                  ) : (
                    <p className="text-muted-foreground">No strengths data</p>
                  )}
                </div>
                <div>
                  <p><strong>Weaknesses vs Competitors:</strong></p>
                  {product.competitive_benchmark.weaknesses_vs_competitors.length > 0 ? (
                    <ul className="list-disc list-inside ml-4 space-y-1">
                      {product.competitive_benchmark.weaknesses_vs_competitors.map((weakness, idx) => (
                        <li key={idx}>{weakness}</li>
                      ))}
                    </ul>
                  ) : (
                    <p className="text-muted-foreground">No weaknesses data</p>
                  )}
                </div>
                <div>
                  <p><strong>Competitor Tactics Not Used:</strong></p>
                  {product.competitive_benchmark.competitor_tactics_not_used.length > 0 ? (
                    <ul className="list-disc list-inside ml-4 space-y-1">
                      {product.competitive_benchmark.competitor_tactics_not_used.map((tactic, idx) => (
                        <li key={idx}>{tactic}</li>
                      ))}
                    </ul>
                  ) : (
                    <p className="text-muted-foreground">No tactics data</p>
                  )}
                </div>
              </Card>
            </div>
          )}

          <div>
            <h3 className="text-lg font-semibold mb-2">Prioritized Recommendations</h3>
            {product.prioritized_recommendations.length > 0 ? (
              <div className="space-y-2">
                {product.prioritized_recommendations.map((rec, idx) => (
                  <Card key={idx} className="p-3">
                    <div className="space-y-1">
                      <p><strong>Effort:</strong> {rec.effort}</p>
                      <p><strong>Priority:</strong> {rec.priority}</p>
                      <p><strong>Expected Impact:</strong> {rec.expected_impact}</p>
                      <p><strong>Recommendation:</strong> {rec.recommendation}</p>
                    </div>
                  </Card>
                ))}
              </div>
            ) : (
              <p className="text-muted-foreground">No recommendations data</p>
            )}
          </div>
        </Card>
      ))}
    </div>
  );
}

// TEMPLATE 5: PAIN POINTS (payload_5)
function renderPainPointsContent(data: PainPointsSchema) {
  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold mb-2">Notes</h3>
        <p>{data.notes || "—"}</p>
      </div>

      <div>
        <h3 className="text-lg font-semibold mb-2">Role Scope</h3>
        <p>{data.role_scope || "—"}</p>
      </div>

      <div>
        <h3 className="text-lg font-semibold mb-2">Top Pains</h3>
        <Card className="p-4 space-y-2">
          <p><strong>Most Urgent:</strong> {data.top_pains.most_urgent}</p>
          <p><strong>Most Frequent:</strong> {data.top_pains.most_frequent}</p>
          <p><strong>Most Impactful:</strong> {data.top_pains.most_impactful}</p>
        </Card>
      </div>

      <div>
        <h3 className="text-lg font-semibold mb-2">Categories</h3>
        {Object.keys(data.categories).length > 0 ? (
          <div className="space-y-4">
            {Object.entries(data.categories).map(([categoryName, painPoints]) => (
              <div key={categoryName}>
                <h4 className="font-semibold mb-2">Category: {categoryName}</h4>
                <div className="space-y-2">
                  {painPoints.map((pain, idx) => (
                    <Card key={idx} className="p-3">
                      <div className="space-y-1">
                        <p><strong>Pain Point:</strong> {pain.pain_point}</p>
                        <p><strong>Description:</strong> {pain.description}</p>
                        <p><strong>Urgency:</strong> {pain.urgency}</p>
                        <p><strong>Frequency:</strong> {pain.frequency}</p>
                        <p><strong>Impact:</strong> {pain.impact}</p>
                        <p><strong>Evidence:</strong> {pain.evidence}</p>
                        <p><strong>Evidence Level:</strong> {pain.evidence_level}</p>
                      </div>
                    </Card>
                  ))}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-muted-foreground">No categories data</p>
        )}
      </div>
    </div>
  );
}

// TEMPLATE 6: COMMUNICATION (payload_6)
function renderCommunicationContent(data: CommunicationSchema) {
  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold mb-2">Notes</h3>
        <p>{data.notes || "—"}</p>
      </div>

      <div>
        <h3 className="text-lg font-semibold mb-2">Strategic Positioning</h3>
        <Card className="p-4 space-y-3">
          <p><strong>Core Thesis:</strong> {data.strategic_positioning.core_thesis}</p>
          <div>
            <p><strong>Pain Solution Map:</strong></p>
            {data.strategic_positioning.pain_solution_map.length > 0 ? (
              <div className="space-y-2 mt-2">
                {data.strategic_positioning.pain_solution_map.map((map, idx) => (
                  <Card key={idx} className="p-3">
                    <div className="space-y-1">
                      <p><strong>Their Pain:</strong> {map.their_pain}</p>
                      <p><strong>Your Solution:</strong> {map.your_solution}</p>
                      <p><strong>Evidence Level:</strong> {map.evidence_level}</p>
                      <p><strong>Connection Logic:</strong> {map.connection_logic}</p>
                    </div>
                  </Card>
                ))}
              </div>
            ) : (
              <p className="text-muted-foreground">No pain solution map data</p>
            )}
          </div>
        </Card>
      </div>

      <div>
        <h3 className="text-lg font-semibold mb-2">Message Architecture</h3>
        <Card className="p-4 space-y-4">
          <div>
            <p><strong>Hook:</strong></p>
            <Card className="p-3 mt-2 space-y-1">
              <p>Text: {data.message_architecture.hook.text}</p>
              <p>Source: {data.message_architecture.hook.source || "—"}</p>
            </Card>
          </div>
          <div>
            <p><strong>Bridge:</strong></p>
            <Card className="p-3 mt-2 space-y-1">
              <p>Text: {data.message_architecture.bridge.text}</p>
              <p>Source: {data.message_architecture.bridge.source || "—"}</p>
            </Card>
          </div>
          <div>
            <p><strong>Proof:</strong></p>
            <Card className="p-3 mt-2 space-y-1">
              <p>Text: {data.message_architecture.proof.text}</p>
              <p>Source: {data.message_architecture.proof.source || "—"}</p>
            </Card>
          </div>
          <div>
            <p><strong>Ask:</strong></p>
            <Card className="p-3 mt-2 space-y-1">
              <p>Text: {data.message_architecture.ask.text}</p>
              <p>Source: {data.message_architecture.ask.source || "—"}</p>
            </Card>
          </div>
        </Card>
      </div>

      <div>
        <h3 className="text-lg font-semibold mb-2">Channel Strategy</h3>
        <Card className="p-4 space-y-2">
          <p><strong>Primary Channel:</strong> {data.channel_strategy.primary_channel}</p>
          <p><strong>Secondary Channel:</strong> {data.channel_strategy.secondary_channel}</p>
          <div>
            <p><strong>Format:</strong></p>
            <Card className="p-3 mt-2 space-y-1">
              <p>Style: {data.channel_strategy.format.style}</p>
              <p>Length: {data.channel_strategy.format.length}</p>
              <p>Reasoning: {data.channel_strategy.format.reasoning || "—"}</p>
            </Card>
          </div>
          <div>
            <p><strong>Timing:</strong></p>
            <Card className="p-3 mt-2 space-y-1">
              <p>Best Time: {data.channel_strategy.timing.best_time}</p>
              <p>Avoid Time: {data.channel_strategy.timing.avoid_time}</p>
              <p>Reasoning: {data.channel_strategy.timing.reasoning || "—"}</p>
            </Card>
          </div>
        </Card>
      </div>

      <div>
        <h3 className="text-lg font-semibold mb-2">Angle Variants</h3>
        {data.angle_variants.length > 0 ? (
          <div className="space-y-2">
            {data.angle_variants.map((angle, idx) => (
              <Card key={idx} className="p-3">
                <div className="space-y-1">
                  <p><strong>Angle Name:</strong> {angle.angle_name}</p>
                  <p><strong>Target Pain:</strong> {angle.target_pain}</p>
                  <p><strong>Opening:</strong> {angle.opening}</p>
                  <p><strong>Framing:</strong> {angle.framing}</p>
                  <p><strong>Proof Point:</strong> {angle.proof_point}</p>
                  <p><strong>CTA:</strong> {angle.cta}</p>
                </div>
              </Card>
            ))}
          </div>
        ) : (
          <p className="text-muted-foreground">No angle variants data</p>
        )}
      </div>

      <div>
        <h3 className="text-lg font-semibold mb-2">Risk Mitigation</h3>
        {data.risk_mitigation.length > 0 ? (
          <div className="space-y-2">
            {data.risk_mitigation.map((risk, idx) => (
              <Card key={idx} className="p-3">
                <div className="space-y-1">
                  <p><strong>Risk:</strong> {risk.risk}</p>
                  <p><strong>Impact:</strong> {risk.impact}</p>
                  <p><strong>Likelihood:</strong> {risk.likelihood}</p>
                  <p><strong>Mitigation:</strong> {risk.mitigation}</p>
                </div>
              </Card>
            ))}
          </div>
        ) : (
          <p className="text-muted-foreground">No risk mitigation data</p>
        )}
      </div>
    </div>
  );
}
