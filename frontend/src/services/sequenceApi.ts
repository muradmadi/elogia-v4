import type {
  JobSummary,
  SequenceGenerationResponse,
  ClaudeOutreachView,
} from "../lib/types";

const API_BASE = import.meta.env.PUBLIC_API_URL ?? "http://localhost:8000";

/**
 * Get all completed enrichment jobs for dropdown selection
 * GET /api/enrichment/completed
 */
export async function getCompletedJobs(): Promise<JobSummary[]> {
  const response = await fetch(`${API_BASE}/api/enrichment/completed`);
  if (!response.ok) {
    throw new Error(`Failed to fetch completed jobs: ${response.status}`);
  }
  return response.json();
}

/**
 * Trigger sequence generation for a job
 * POST /api/sequence/generate/{job_id}
 * Returns 202 Accepted with sequence_id
 */
export async function triggerSequenceGeneration(
  jobId: string,
): Promise<SequenceGenerationResponse> {
  const response = await fetch(`${API_BASE}/api/sequence/generate/${jobId}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
  });

  if (response.status !== 202) {
    throw new Error(
      `Failed to trigger sequence generation: ${response.status}`,
    );
  }

  return response.json();
}

/**
 * Poll for sequence data
 * GET /api/sequence/job/{job_id}
 * Returns 200 OK with ClaudeOutreachView when ready
 * Returns 404 when data is not yet generated (still pending)
 */
export async function getSequenceData(
  jobId: string,
): Promise<ClaudeOutreachView> {
  const response = await fetch(`${API_BASE}/api/sequence/job/${jobId}`);

  if (response.status === 404) {
    // Sequence data not yet generated
    throw new Error("Sequence data not yet generated");
  }

  if (!response.ok) {
    throw new Error(`Failed to fetch sequence data: ${response.status}`);
  }

  return response.json();
}
