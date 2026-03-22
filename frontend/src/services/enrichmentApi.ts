import type {
  EnrichmentTriggerResponse,
  EnrichmentJobResponse,
  PersonSchema,
  CompanySchema,
  ProfileSchema,
  ProductSchema,
  PainPointsSchema,
  CommunicationSchema,
  JobSummary,
} from "../lib/types";

const API_BASE = import.meta.env.PUBLIC_API_URL ?? "http://localhost:8000";

/**
 * Trigger enrichment for an email address.
 * POST /webhooks/trigger?email=...
 * Returns 202 Accepted with job_id.
 */
export async function triggerEnrichment(
  email: string,
): Promise<EnrichmentTriggerResponse> {
  const url = new URL("/webhooks/trigger", API_BASE);
  url.searchParams.set("email", email);

  const response = await fetch(url.toString(), {
    method: "POST",
  });

  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(
      body.detail ?? `Enrichment trigger failed with status ${response.status}`,
    );
  }

  return response.json();
}

/**
 * Get the current state of an enrichment job.
 * GET /api/enrichment/jobs/{job_id}
 * Used for polling to detect payload arrivals.
 */
export async function getEnrichmentJob(
  jobId: string,
): Promise<EnrichmentJobResponse> {
  const response = await fetch(`${API_BASE}/api/enrichment/jobs/${jobId}`);

  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail ?? `Failed to fetch job: ${response.status}`);
  }

  return response.json();
}

/**
 * Generic fetcher for standalone payload endpoints.
 * Returns null when the payload hasn't arrived yet (404 or null response).
 */
async function fetchPayload<T>(
  jobId: string,
  endpoint: string,
): Promise<T | null> {
  const url = `${API_BASE}/api/enrichment/${jobId}/${endpoint}`;
  console.log(`[enrichmentApi] Fetching: ${url}`);

  let response: Response;
  try {
    response = await fetch(url);
  } catch (err) {
    console.error(`[enrichmentApi] Network error fetching ${url}:`, err);
    throw new Error(
      `Network error: ${err instanceof Error ? err.message : "Failed to connect to backend"}`,
    );
  }

  if (response.status === 404) {
    console.log(
      `[enrichmentApi] 404 for ${endpoint} — payload not yet available`,
    );
    return null;
  }

  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    console.error(
      `[enrichmentApi] ${response.status} error for ${endpoint}:`,
      body,
    );
    throw new Error(
      body.detail ?? `Failed to fetch ${endpoint}: ${response.status}`,
    );
  }

  return response.json();
}

/** GET /api/enrichment/{job_id}/person → PersonSchema | null */
export function getPersonSchema(jobId: string): Promise<PersonSchema | null> {
  return fetchPayload<PersonSchema>(jobId, "person");
}

/** GET /api/enrichment/{job_id}/company → CompanySchema | null */
export function getCompanySchema(jobId: string): Promise<CompanySchema | null> {
  return fetchPayload<CompanySchema>(jobId, "company");
}

/** GET /api/enrichment/{job_id}/profile → ProfileSchema | null */
export function getProfileSchema(jobId: string): Promise<ProfileSchema | null> {
  return fetchPayload<ProfileSchema>(jobId, "profile");
}

/** GET /api/enrichment/{job_id}/products → ProductSchema[] | null */
export function getProductSchema(
  jobId: string,
): Promise<ProductSchema[] | null> {
  return fetchPayload<ProductSchema[]>(jobId, "products");
}

/** GET /api/enrichment/{job_id}/painpoints → PainPointsSchema | null */
export function getPainPointsSchema(
  jobId: string,
): Promise<PainPointsSchema | null> {
  return fetchPayload<PainPointsSchema>(jobId, "painpoints");
}

/** GET /api/enrichment/{job_id}/communication → CommunicationSchema | null */
export function getCommunicationSchema(
  jobId: string,
): Promise<CommunicationSchema | null> {
  return fetchPayload<CommunicationSchema>(jobId, "communication");
}

/** GET /api/enrichment/completed → List[JobSummary] */
export async function getCompletedJobs(): Promise<JobSummary[]> {
  const response = await fetch(`${API_BASE}/api/enrichment/completed`);

  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(
      body.detail ?? `Failed to fetch completed jobs: ${response.status}`,
    );
  }

  return response.json();
}
