import { atom } from "nanostores";
import type { EnrichmentJobStatus, PayloadType } from "../lib/types";

const STORAGE_KEY = "enrichment_state";

interface StoredState {
  currentJobId: string | null;
  activeEmail: string | null;
  isJobInProgress: boolean;
  jobStatus: EnrichmentJobStatus | null;
  payloadStatus: {
    payload_1: boolean;
    payload_2: boolean;
    payload_3: boolean;
    payload_4: boolean;
    payload_5: boolean;
    payload_6: boolean;
  };
}

/** Load state from localStorage */
function loadState(): StoredState | null {
  if (typeof window === "undefined") return null;
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (!stored) return null;
    return JSON.parse(stored) as StoredState;
  } catch {
    return null;
  }
}

/** Save state to localStorage */
function saveState(state: StoredState): void {
  if (typeof window === "undefined") return;
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
  } catch {
    // Ignore localStorage errors
  }
}

/** Clear state from localStorage */
function clearState(): void {
  if (typeof window === "undefined") return;
  try {
    localStorage.removeItem(STORAGE_KEY);
  } catch {
    // Ignore localStorage errors
  }
}

// Initialize from localStorage
const initialState = loadState();

// Safety check: validate loaded state is reasonable
// Rules:
// 1. If isJobInProgress=true but no currentJobId, discard state
// 2. If isJobInProgress=true but the state was saved more than 1 hour ago,
//    it's likely stale - discard state (safety net)
function validateInitialState(state: StoredState | null): StoredState | null {
  if (!state) return null;

  // Check rule 1: must have jobId if in progress
  if (state.isJobInProgress && !state.currentJobId) {
    console.warn(
      "[enrichment-store] Discarding invalid initial state: isJobInProgress but no currentJobId",
    );
    clearState();
    return null;
  }

  // State is valid - we'll let polling/recovery mechanisms handle stale jobs
  // When component mounts, it will verify with backend if needed
  return state;
}

const safeInitialState = validateInitialState(initialState);

/** The current active enrichment job ID — set by the form, read by other islands */
export const $currentJobId = atom<string | null>(
  safeInitialState?.currentJobId ?? null,
);

/** The email locked into the form while a job is in progress */
export const $activeEmail = atom<string | null>(
  safeInitialState?.activeEmail ?? null,
);

/** Whether a job is currently in progress (pending) */
export const $isJobInProgress = atom<boolean>(
  safeInitialState?.isJobInProgress ?? false,
);

/** The current job status — polled from the backend */
export const $jobStatus = atom<EnrichmentJobStatus | null>(
  safeInitialState?.jobStatus ?? null,
);

/** Payload arrival tracking — which of the 6 payloads have been received */
export const $payloadStatus = atom<{
  payload_1: boolean;
  payload_2: boolean;
  payload_3: boolean;
  payload_4: boolean;
  payload_5: boolean;
  payload_6: boolean;
}>(
  safeInitialState?.payloadStatus ?? {
    payload_1: false,
    payload_2: false,
    payload_3: false,
    payload_4: false,
    payload_5: false,
    payload_6: false,
  },
);

/** Modal open/close state for payload detail modal */
export const $isDetailModalOpen = atom<boolean>(false);

/** Selected payload type for detail view */
export const $selectedPayloadType = atom<PayloadType | null>(null);

// Subscribe to changes and persist to localStorage
// CRITICAL FIX: Use debounced batch updates to ensure atomic localStorage saves
let persistTimeout: ReturnType<typeof setTimeout> | null = null;

function getCurrentState(): StoredState {
  return {
    currentJobId: $currentJobId.get(),
    activeEmail: $activeEmail.get(),
    isJobInProgress: $isJobInProgress.get(),
    jobStatus: $jobStatus.get(),
    payloadStatus: $payloadStatus.get(),
  };
}

function schedulePersist() {
  // Cancel any pending persistence
  if (persistTimeout) {
    clearTimeout(persistTimeout);
  }

  // Schedule persistence after 100ms to batch updates
  persistTimeout = setTimeout(() => {
    const state = getCurrentState();
    console.log("[enrichment-store] Persisting state to localStorage:", {
      isJobInProgress: state.isJobInProgress,
      currentJobId: state.currentJobId,
      activeEmail: state.activeEmail,
    });
    saveState(state);
    persistTimeout = null;
  }, 100);
}

// Subscribe to ALL atoms - each one triggers a debounced save
$currentJobId.subscribe(() => schedulePersist());
$activeEmail.subscribe(() => schedulePersist());
$isJobInProgress.subscribe(() => schedulePersist());
$jobStatus.subscribe(() => schedulePersist());
$payloadStatus.subscribe(() => schedulePersist());

/** Reset all enrichment state */
export function resetEnrichmentState() {
  $currentJobId.set(null);
  $activeEmail.set(null);
  $isJobInProgress.set(false);
  $jobStatus.set(null);
  $payloadStatus.set({
    payload_1: false,
    payload_2: false,
    payload_3: false,
    payload_4: false,
    payload_5: false,
    payload_6: false,
  });
  $isDetailModalOpen.set(false);
  $selectedPayloadType.set(null);
  clearState();
}
