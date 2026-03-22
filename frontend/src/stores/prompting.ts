import { atom } from "nanostores";
import type {
  JobSummary,
  ClaudeOutreachView,
  CampaignSequenceStatus,
} from "../lib/types";

const STORAGE_KEY = "prompting_state";

interface StoredState {
  completedJobs: JobSummary[];
  selectedJobId: string | null;
  sequenceData: ClaudeOutreachView | null;
  generationStatus: CampaignSequenceStatus | null;
  isGenerating: boolean;
  generationError: string | null;
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

/** List of completed enrichment jobs for dropdown selection */
export const $completedJobs = atom<JobSummary[]>(
  initialState?.completedJobs ?? [],
);

/** The currently selected job ID in the dropdown */
export const $selectedJobId = atom<string | null>(
  initialState?.selectedJobId ?? null,
);

/** The generated sequence data for the selected job */
export const $sequenceData = atom<ClaudeOutreachView | null>(
  initialState?.sequenceData ?? null,
);

/** Current generation status (pending, generating, completed, failed) */
export const $generationStatus = atom<CampaignSequenceStatus | null>(
  initialState?.generationStatus ?? null,
);

/** Whether generation is currently in progress */
export const $isGenerating = atom<boolean>(initialState?.isGenerating ?? false);

/** Error message from generation attempt */
export const $generationError = atom<string | null>(
  initialState?.generationError ?? null,
);

// Subscribe to changes and persist to localStorage
function getCurrentState(): StoredState {
  return {
    completedJobs: $completedJobs.get(),
    selectedJobId: $selectedJobId.get(),
    sequenceData: $sequenceData.get(),
    generationStatus: $generationStatus.get(),
    isGenerating: $isGenerating.get(),
    generationError: $generationError.get(),
  };
}

$completedJobs.subscribe(() => saveState(getCurrentState()));
$selectedJobId.subscribe(() => saveState(getCurrentState()));
$sequenceData.subscribe(() => saveState(getCurrentState()));
$generationStatus.subscribe(() => saveState(getCurrentState()));
$isGenerating.subscribe(() => saveState(getCurrentState()));
$generationError.subscribe(() => saveState(getCurrentState()));

/** Reset all prompting state */
export function resetPromptingState() {
  $completedJobs.set([]);
  $selectedJobId.set(null);
  $sequenceData.set(null);
  $generationStatus.set(null);
  $isGenerating.set(false);
  $generationError.set(null);
  clearState();
}
