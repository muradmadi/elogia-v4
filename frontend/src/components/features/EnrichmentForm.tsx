import { useState, useCallback, useEffect, useRef } from "react";
import { useStore } from "@nanostores/react";
import { Button } from "../ui/button";
import { Input } from "../ui/input";
import { Card, CardContent } from "../ui/card";
import { Alert, AlertDescription, AlertTitle } from "../ui/alert";
import { cn } from "@/lib/utils";
import { triggerEnrichment, getEnrichmentJob } from "../../services/enrichmentApi";
import {
  $currentJobId,
  $activeEmail,
  $isJobInProgress,
  $payloadStatus,
  resetEnrichmentState,
} from "../../stores/enrichment";

type FormState = "idle" | "loading" | "success" | "error";

interface EnrichmentFormProps {}

export function EnrichmentForm({}: EnrichmentFormProps) {
  const activeEmail = useStore($activeEmail);
  const isJobInProgress = useStore($isJobInProgress);
  const currentJobId = useStore($currentJobId);
  
  // Initialize email from store state
  const [email, setEmail] = useState(activeEmail ?? "");
  
  // Track job start time for timeout detection - use Ref to avoid closure issues
  const jobStartTimeRef = useRef<number | null>(null);
  
  // Determine form state based on store
  const [formState, setFormState] = useState<FormState>(() => {
    if (currentJobId && isJobInProgress) return "success";
    return "idle";
  });
  
  const [errorMessage, setErrorMessage] = useState("");
  const pollingIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const recoveryTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const pollForPayloads = useCallback(async (jobId: string) => {
    try {
      const jobResponse = await getEnrichmentJob(jobId);
      
      // Update payload status based on which payloads have arrived
      const newPayloadStatus = {
        payload_1: jobResponse.payload_1 !== null,
        payload_2: jobResponse.payload_2 !== null,
        payload_3: jobResponse.payload_3 !== null,
        payload_4: jobResponse.payload_4 !== null,
        payload_5: jobResponse.payload_5 !== null,
        payload_6: jobResponse.payload_6 !== null,
      };
      
      $payloadStatus.set(newPayloadStatus);
      
      // Check if all payloads have arrived OR job status is completed
      const allPayloadsReceived = Object.values(newPayloadStatus).every(Boolean);
      const isJobCompleted = allPayloadsReceived || jobResponse.status === "completed";
      
      if (isJobCompleted) {
        // CRITICAL: Stop polling when job is complete
        if (pollingIntervalRef.current) {
          clearInterval(pollingIntervalRef.current);
          pollingIntervalRef.current = null;
        }
        $isJobInProgress.set(false);
        jobStartTimeRef.current = null;
        console.log(`[enrichment] Job ${jobId} completed (allPayloads=${allPayloadsReceived}, status=${jobResponse.status}), stopped polling`);
      }
      
      // Check for timeout: if job has been running for more than 15 minutes
      if (jobStartTimeRef.current && Date.now() - jobStartTimeRef.current > 15 * 60 * 1000) {
        console.warn(`[enrichment] Job ${jobId} timed out after 15 minutes`);
        // Auto-reset to allow user interaction
        if (pollingIntervalRef.current) {
          clearInterval(pollingIntervalRef.current);
          pollingIntervalRef.current = null;
        }
        $isJobInProgress.set(false);
        jobStartTimeRef.current = null;
      }
    } catch (err) {
      console.error("[enrichment] Error polling for payloads:", err);
      
      // Check for 404 - job was deleted
      const is404 = err instanceof Error && (err.message.includes("404") || err.message.includes("not found"));
      
      // Check for other fatal errors - consider them timeouts
      const isFatalError = err instanceof Error &&
        (err.message.includes("Network error") ||
         err.message.includes("500") ||
         err.message.includes("502") ||
         err.message.includes("503"));
      
      if (is404) {
        console.warn(`[enrichment] Job ${jobId} not found (404), resetting state`);
        resetEnrichmentState();
        setEmail("");
        setFormState("idle");
        jobStartTimeRef.current = null;
        if (pollingIntervalRef.current) {
          clearInterval(pollingIntervalRef.current);
          pollingIntervalRef.current = null;
        }
      } else if (isFatalError && jobStartTimeRef.current && Date.now() - jobStartTimeRef.current > 30 * 1000) {
        // Only reset after 30 seconds of persistent fatal errors
        console.warn(`[enrichment] Job ${jobId} encountered persistent errors, resetting after 30s`);
        resetEnrichmentState();
        setEmail("");
        setFormState("error");
        setErrorMessage("Job failed due to backend errors. Please try again.");
        jobStartTimeRef.current = null;
        if (pollingIntervalRef.current) {
          clearInterval(pollingIntervalRef.current);
          pollingIntervalRef.current = null;
        }
      }
      // For transient errors, just log and continue polling
    }
  }, []);  // CRITICAL: No dependencies - this callback never changes

  const handleSubmit = useCallback(
    async (e: React.FormEvent) => {
      e.preventDefault();

      const trimmedEmail = email.trim();
      if (!trimmedEmail) return;

      setFormState("loading");
      setErrorMessage("");
      jobStartTimeRef.current = Date.now();  // FIX: Use Ref instead of state

      try {
        const result = await triggerEnrichment(trimmedEmail);

        // Update cross-island state
        $currentJobId.set(result.job_id);
        $activeEmail.set(trimmedEmail);
        $isJobInProgress.set(true);

        // Reset payload status for new job
        $payloadStatus.set({
          payload_1: false,
          payload_2: false,
          payload_3: false,
          payload_4: false,
          payload_5: false,
          payload_6: false,
        });

        setFormState("success");

        // Start polling for payloads
        if (pollingIntervalRef.current) {
          clearInterval(pollingIntervalRef.current);
        }
        
        // CRITICAL: Store job ID in ref to avoid closure issues
        const jobId = result.job_id;
        console.log(`[enrichment] Starting polling for job ${jobId}`);
        
        pollingIntervalRef.current = setInterval(() => {
          pollForPayloads(jobId);  // Use captured jobId, not dependency
        }, 2000); // Poll every 2 seconds
      } catch (err) {
        setFormState("error");
        jobStartTimeRef.current = null;  // FIX: Use Ref instead of state
        setErrorMessage(
          err instanceof Error ? err.message : "An unexpected error occurred"
        );
      }
    },
    [email, pollForPayloads]
  );

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent<HTMLInputElement>) => {
      if (e.key === "Enter" && !isJobInProgress && email.trim()) {
        e.preventDefault();
        const formEvent = new Event('submit', { bubbles: true, cancelable: true }) as unknown as React.FormEvent;
        handleSubmit(formEvent);
      }
    },
    [handleSubmit, isJobInProgress, email]
  );

  // Cleanup polling interval on unmount
  useEffect(() => {
    return () => {
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
      }
    };
  }, []);

  // Restart polling if page loads with an in-progress job
  useEffect(() => {
    if (currentJobId && isJobInProgress && !pollingIntervalRef.current) {
      console.log(`[enrichment] Restarting polling for existing job ${currentJobId}`);
      jobStartTimeRef.current = Date.now();
      
      // Start polling immediately
      pollForPayloads(currentJobId);
      
      // Then set up interval
      pollingIntervalRef.current = setInterval(() => {
        pollForPayloads(currentJobId);
      }, 2000);
    }
  }, [currentJobId, isJobInProgress, pollForPayloads]);

  // Cleanup recovery timeout on unmount or when job completes
  useEffect(() => {
    return () => {
      if (recoveryTimeoutRef.current) {
        clearTimeout(recoveryTimeoutRef.current);
        recoveryTimeoutRef.current = null;
      }
    };
  }, []);

  const isDisabled = isJobInProgress || formState === "loading";
  const displayEmail = isJobInProgress ? activeEmail ?? email : email;

  return (
    <Card className="mx-auto max-w-xl">
      <CardContent className="pt-4 pb-4">
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="flex gap-3">
            <Input
              type="email"
              placeholder="Enter an email address to enrich..."
              value={displayEmail}
              onChange={(e) => {
                if (!isJobInProgress) {
                  setEmail(e.target.value);
                  if (formState === "error") {
                    setFormState("idle");
                    setErrorMessage("");
                  }
                }
              }}
              onKeyDown={handleKeyDown}
              disabled={isDisabled}
              className={cn(
                "flex-1",
                isJobInProgress && "opacity-75 cursor-not-allowed"
              )}
              required
            />
            <Button
              type="submit"
              disabled={isDisabled || !email.trim()}
              className={cn(
                "min-w-24",
                formState === "loading" && "animate-pulse"
              )}
            >
              {formState === "loading" ? "Sending..." : "Send"}
            </Button>
          </div>

          {/* Success message */}
          {formState === "success" && (
            <Alert className="border-success/30 bg-success/10 text-success">
              <AlertTitle>Enrichment started</AlertTitle>
              <AlertDescription>
                It will take roughly 5 minutes to receive all the information
                from Clay. The form is locked while enrichment is in progress.
              </AlertDescription>
            </Alert>
          )}

          {/* Error message */}
          {formState === "error" && (
            <Alert variant="destructive">
              <AlertTitle>Enrichment failed</AlertTitle>
              <AlertDescription>{errorMessage}</AlertDescription>
            </Alert>
          )}

          {/* Simple reset button */}
          <div className="pt-2 text-right">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => {
                // CRITICAL: Cancel all async operations
                resetEnrichmentState();
                setEmail("");
                setFormState("idle");
                setErrorMessage("");
                jobStartTimeRef.current = null;
                
                // Clear all pending intervals and timeouts
                if (pollingIntervalRef.current) {
                  clearInterval(pollingIntervalRef.current);
                  pollingIntervalRef.current = null;
                }
                if (recoveryTimeoutRef.current) {
                  clearTimeout(recoveryTimeoutRef.current);
                  recoveryTimeoutRef.current = null;
                }
                
                console.log("[enrichment] Form reset by user");
              }}
              className="text-xs text-muted-foreground"
            >
              Reset Form
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  );
}
