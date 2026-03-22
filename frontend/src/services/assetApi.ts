import type {
  AssetUploadResponse,
  AssetContentResponse,
  AssetWithSnacksResponse,
} from "../lib/types";

const API_BASE = import.meta.env.PUBLIC_API_URL ?? "http://localhost:8000";

/**
 * Upload a PDF asset and trigger the n8n content shredder webhook.
 * POST /api/assets/upload
 * Returns 202 Accepted with asset_id.
 */
export async function uploadAsset(file: File): Promise<AssetUploadResponse> {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_BASE}/api/assets/upload`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(
      body.detail ?? `Asset upload failed with status ${response.status}`,
    );
  }

  return response.json();
}

/**
 * Get a marketing asset along with all its associated content snacks.
 * GET /api/assets/{asset_id}/snacks
 * Returns AssetWithSnacksResponse.
 */
export async function getAssetWithSnacks(
  assetId: string,
): Promise<AssetWithSnacksResponse> {
  const response = await fetch(`${API_BASE}/api/assets/${assetId}/snacks`);

  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(
      body.detail ?? `Failed to retrieve asset with snacks: ${response.status}`,
    );
  }

  return response.json();
}

/**
 * Get cleaned content for a specific asset in a structured format.
 * GET /api/assets/{asset_id}/content
 * Returns AssetContentResponse.
 */
export async function getAssetContent(
  assetId: string,
): Promise<AssetContentResponse> {
  const response = await fetch(`${API_BASE}/api/assets/${assetId}/content`);

  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(
      body.detail ?? `Failed to retrieve asset content: ${response.status}`,
    );
  }

  return response.json();
}

/**
 * Poll for asset content until it's available.
 * Returns the content once the asset status is "completed".
 */
export async function pollAssetContent(
  assetId: string,
  maxAttempts = 120, // Increased from 30 to 120 (2 minutes at 1 second intervals)
  intervalMs = 1000,
): Promise<AssetContentResponse> {
  for (let attempt = 0; attempt < maxAttempts; attempt++) {
    try {
      const response = await getAssetContent(assetId);
      // If we get a response, the content is ready
      return response;
    } catch (error) {
      // If asset is not found or not ready yet, wait and retry
      if (attempt < maxAttempts - 1) {
        await new Promise((resolve) => setTimeout(resolve, intervalMs));
      } else {
        throw error;
      }
    }
  }
  throw new Error("Timeout waiting for asset content");
}
