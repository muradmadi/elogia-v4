import { atom } from "nanostores";
import type { AssetStatus, ContentSnackResponse } from "../lib/types";

const STORAGE_KEY = "asset_state";
const STORAGE_TIMESTAMP_KEY = "asset_state_timestamp";
const MAX_STATE_AGE_MS = 24 * 60 * 60 * 1000; // 24 hours

interface StoredState {
  currentAssetId: string | null;
  assetStatus: AssetStatus | null;
  contentItems: ContentSnackResponse[];
  timestamp?: number;
}

/** Load state from localStorage with timestamp validation */
function loadState(): StoredState | null {
  if (typeof window === "undefined") return null;
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    const timestampStr = localStorage.getItem(STORAGE_TIMESTAMP_KEY);

    if (!stored || !timestampStr) return null;

    const timestamp = parseInt(timestampStr, 10);
    const now = Date.now();

    // Check if state is too old (more than 24 hours)
    if (now - timestamp > MAX_STATE_AGE_MS) {
      console.warn(
        "[asset-store] Discarding stale state (older than 24 hours)",
      );
      clearState();
      return null;
    }

    return JSON.parse(stored) as StoredState;
  } catch {
    return null;
  }
}

/** Save state to localStorage with timestamp */
function saveState(state: StoredState): void {
  if (typeof window === "undefined") return;
  try {
    const stateWithTimestamp = { ...state, timestamp: Date.now() };
    localStorage.setItem(STORAGE_KEY, JSON.stringify(stateWithTimestamp));
    localStorage.setItem(STORAGE_TIMESTAMP_KEY, Date.now().toString());
  } catch {
    // Ignore localStorage errors
  }
}

/** Clear state from localStorage */
function clearState(): void {
  if (typeof window === "undefined") return;
  try {
    localStorage.removeItem(STORAGE_KEY);
    localStorage.removeItem(STORAGE_TIMESTAMP_KEY);
  } catch {
    // Ignore localStorage errors
  }
}

// Initialize from localStorage with validation
const initialState = loadState();

/** The current active asset ID — set by the uploader, read by the results viewer */
export const $currentAssetId = atom<string | null>(
  initialState?.currentAssetId ?? null,
);

/** The current asset status — polled from the backend */
export const $assetStatus = atom<AssetStatus | null>(
  initialState?.assetStatus ?? null,
);

/** The content items (LinkedIn posts and email pills) */
export const $contentItems = atom<ContentSnackResponse[]>(
  initialState?.contentItems ?? [],
);

/** Whether content is currently being loaded */
export const $isLoadingContent = atom<boolean>(false);

/** Error message if content loading fails */
export const $contentError = atom<string | null>(null);

// Subscribe to changes and persist to localStorage
function getCurrentState(): StoredState {
  return {
    currentAssetId: $currentAssetId.get(),
    assetStatus: $assetStatus.get(),
    contentItems: $contentItems.get(),
  };
}

$currentAssetId.subscribe(() => saveState(getCurrentState()));
$assetStatus.subscribe(() => saveState(getCurrentState()));
$contentItems.subscribe(() => saveState(getCurrentState()));

/** Reset all asset state */
export function resetAssetState() {
  $currentAssetId.set(null);
  $assetStatus.set(null);
  $contentItems.set([]);
  $isLoadingContent.set(false);
  $contentError.set(null);
  clearState();
}

/** Force clear localStorage state (for debugging) */
export function forceClearAssetState() {
  clearState();
  resetAssetState();
}
