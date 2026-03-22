import { useEffect, useState } from "react";
import { useStore } from "@nanostores/react";
import {
  $completedJobs,
  $selectedJobId,
  $sequenceData,
  $generationStatus,
  $isGenerating,
  $generationError,
} from "../../stores/prompting";
import {
  getCompletedJobs,
  triggerSequenceGeneration,
  getSequenceData,
} from "../../services/sequenceApi";
import { Button } from "../ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "../ui/card";
import { Alert, AlertDescription } from "../ui/alert";
import { Skeleton } from "../ui/skeleton";
import { Badge } from "../ui/badge";

export function SequenceLiveDemo() {
  const completedJobs = useStore($completedJobs);
  const selectedJobId = useStore($selectedJobId);
  const sequenceData = useStore($sequenceData);
  const generationStatus = useStore($generationStatus);
  const isGenerating = useStore($isGenerating);
  const generationError = useStore($generationError);

  const [isLoadingJobs, setIsLoadingJobs] = useState(true);
  const [pollingIntervalId, setPollingIntervalId] = useState<
    ReturnType<typeof setInterval> | null
  >(null);

  // Load completed jobs on mount
  useEffect(() => {
    async function fetchJobs() {
      try {
        const jobs = await getCompletedJobs();
        $completedJobs.set(jobs);
      } catch (error) {
        console.error("Failed to load completed jobs:", error);
      } finally {
        setIsLoadingJobs(false);
      }
    }

    fetchJobs();
  }, []);

  // Handle job selection
  const handleJobSelect = (jobId: string) => {
    $selectedJobId.set(jobId);
    // Clear previous sequence data when selecting a new job
    $sequenceData.set(null);
    $generationStatus.set(null);
    $generationError.set(null);
  };

  // Handle Send button click
  const handleSendClick = async () => {
    if (!selectedJobId) return;

    try {
      $isGenerating.set(true);
      $generationError.set(null);
      $generationStatus.set("generating");

      // Trigger sequence generation
      await triggerSequenceGeneration(selectedJobId);

      // Start polling for sequence data
      const pollInterval = setInterval(async () => {
        try {
          const data = await getSequenceData(selectedJobId);
          // Success - got the data
          $sequenceData.set(data);
          $generationStatus.set("completed");
          $isGenerating.set(false);
          if (pollInterval) clearInterval(pollInterval);
          setPollingIntervalId(null);
        } catch (error) {
          // Keep polling if data not yet generated (404)
          if (error instanceof Error && error.message.includes("not yet")) {
            // Still waiting, continue polling
            return;
          }
          // Real error occurred
          $generationError.set(
            error instanceof Error ? error.message : "Unknown error"
          );
          $generationStatus.set("failed");
          $isGenerating.set(false);
          if (pollInterval) clearInterval(pollInterval);
          setPollingIntervalId(null);
        }
      }, 2000); // Poll every 2 seconds

      setPollingIntervalId(pollInterval);
    } catch (error) {
      $generationError.set(
        error instanceof Error ? error.message : "Failed to trigger generation"
      );
      $generationStatus.set("failed");
      $isGenerating.set(false);
    }
  };

  // Cleanup polling interval on unmount
  useEffect(() => {
    return () => {
      if (pollingIntervalId) {
        clearInterval(pollingIntervalId);
      }
    };
  }, [pollingIntervalId]);

  return (
    <div className="w-full space-y-8">
      {/* Email Selector Section */}
      <div className="space-y-4">
        <h2 className="text-2xl font-bold">Select Enriched Email</h2>

        {isLoadingJobs ? (
          <div className="space-y-2">
            <Skeleton className="h-10 w-full" />
          </div>
        ) : completedJobs.length === 0 ? (
          <Alert>
            <AlertDescription>
              No completed enrichment jobs found. Please complete an enrichment
              first on the Enrichment page.
            </AlertDescription>
          </Alert>
        ) : (
          <div className="space-y-3">
            <div className="grid gap-2">
              {completedJobs.map((job) => (
                <button
                  key={job.job_id}
                  onClick={() => handleJobSelect(job.job_id)}
                  className={`w-full text-left px-4 py-3 rounded-lg border-2 transition-colors ${
                    selectedJobId === job.job_id
                      ? "border-primary bg-primary/5"
                      : "border-border hover:border-primary/50"
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-semibold">{job.email}</p>
                      <p className="text-sm text-muted-foreground">
                        Job ID: {job.job_id.slice(0, 8)}...
                      </p>
                    </div>
                    <Badge variant="outline">{job.status}</Badge>
                  </div>
                </button>
              ))}
            </div>

            {/* Send Button */}
            <Button
              onClick={handleSendClick}
              disabled={!selectedJobId || isGenerating}
              className="w-full"
              size="lg"
            >
              {isGenerating ? "Generating Sequence..." : "Generate Sequence"}
            </Button>
          </div>
        )}
      </div>

      {/* Status & Error Section */}
      {generationError && (
        <Alert variant="destructive">
          <AlertDescription>{generationError}</AlertDescription>
        </Alert>
      )}

      {isGenerating && (
        <Alert>
          <AlertDescription>
            Generating 8-touch email sequence using Claude...
          </AlertDescription>
        </Alert>
      )}

      {/* Sequence Touches Section */}
      {sequenceData && (
        <div className="space-y-6">
          {/* Account Strategy Section */}
          <div>
            <h2 className="text-2xl font-bold mb-4">Account Strategy</h2>
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Strategic Analysis</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <p className="text-sm font-semibold text-muted-foreground mb-2">
                    Personalization Angle
                  </p>
                  <p className="text-base">
                    {sequenceData.account_strategy_analysis
                      .personalization_angle}
                  </p>
                </div>
                <div>
                  <p className="text-sm font-semibold text-muted-foreground mb-2">
                    Core Pain Point
                  </p>
                  <p className="text-base">
                    {sequenceData.account_strategy_analysis
                      .identified_core_pain_point}
                  </p>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* 8-Touch Email Sequence */}
          <div>
            <h2 className="text-2xl font-bold mb-4">Email Sequence (8 Touches)</h2>
            <div className="grid gap-4 md:grid-cols-2">
              {sequenceData.touches.map((touch, index) => (
                <Card key={index} className="flex flex-col">
                  <CardHeader>
                    <div className="flex items-start justify-between gap-2">
                      <div className="space-y-1 flex-1">
                        <Badge variant="secondary">
                          Touch {touch.touch_number}
                        </Badge>
                        <CardTitle className="text-lg mt-2">
                          {touch.objective}
                        </CardTitle>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-4 flex-1 flex flex-col">
                    <div>
                      <p className="text-xs font-semibold text-muted-foreground uppercase mb-2">
                        AI Prompt Instruction
                      </p>
                      <p className="text-sm leading-relaxed text-foreground/90">
                        {touch.ai_prompt_instruction}
                      </p>
                    </div>

                    <div className="flex-1">
                      <p className="text-xs font-semibold text-muted-foreground uppercase mb-2">
                        Example Snippet
                      </p>
                      <div className="bg-muted p-3 rounded text-sm leading-relaxed italic text-foreground/80">
                        {touch.example_snippet}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>

          {/* Reset Button */}
          <Button
            onClick={() => {
              $selectedJobId.set(null);
              $sequenceData.set(null);
              $generationStatus.set(null);
              $generationError.set(null);
            }}
            variant="outline"
            className="w-full"
          >
            Generate Another Sequence
          </Button>
        </div>
      )}
    </div>
  );
}
