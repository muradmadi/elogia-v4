import { useEffect, useState, useCallback } from "react";
import { useStore } from "@nanostores/react";
import {
  $currentAssetId,
  $contentItems,
  $isLoadingContent,
  $contentError,
  resetAssetState,
  forceClearAssetState,
} from "../../stores/asset";
import { pollAssetContent } from "../../services/assetApi";
import { Card, CardContent, CardHeader, CardTitle } from "../ui/card";
import { Badge } from "../ui/badge";
import { Skeleton } from "../ui/skeleton";
import { Alert, AlertDescription, AlertTitle } from "../ui/alert";
import { Button } from "../ui/button";
import { cn } from "../../lib/utils";
import type { ContentSnackResponse } from "../../lib/types";
import { Briefcase, Mail, RefreshCw, Upload, Trash2 } from "lucide-react";

export function ContentResults() {
  const currentAssetId = useStore($currentAssetId);
  const contentItems = useStore($contentItems);
  const isLoading = useStore($isLoadingContent);
  const error = useStore($contentError);

  const [polling, setPolling] = useState(false);
  const [pollingAttempt, setPollingAttempt] = useState(0);
  const [showStaleWarning, setShowStaleWarning] = useState(false);

  // Check if state might be stale (no content after multiple attempts)
  useEffect(() => {
    if (currentAssetId && contentItems.length === 0 && pollingAttempt >= 3) {
      setShowStaleWarning(true);
    } else {
      setShowStaleWarning(false);
    }
  }, [currentAssetId, contentItems.length, pollingAttempt]);

  // Poll for content when asset ID changes
  useEffect(() => {
    if (!currentAssetId) {
      $contentItems.set([]);
      return;
    }

    const pollContent = async () => {
      setPolling(true);
      $isLoadingContent.set(true);
      $contentError.set(null);

      try {
        const response = await pollAssetContent(currentAssetId);
        $contentItems.set(response.content_items);
        setPollingAttempt(0); // Reset attempt counter on success
        setShowStaleWarning(false);
      } catch (err) {
        const message = err instanceof Error ? err.message : "Failed to load content";
        $contentError.set(message);
        setPollingAttempt(prev => prev + 1);
      } finally {
        $isLoadingContent.set(false);
        setPolling(false);
      }
    };

    pollContent();
  }, [currentAssetId, pollingAttempt]);

  // Manual refresh function
  const handleRefresh = useCallback(() => {
    if (currentAssetId) {
      setPollingAttempt(prev => prev + 1);
    }
  }, [currentAssetId]);

  // Reset state to allow new upload
  const handleReset = useCallback(() => {
    resetAssetState();
  }, []);

  // Force clear stale state
  const handleClearStaleState = useCallback(() => {
    forceClearAssetState();
    setShowStaleWarning(false);
    setPollingAttempt(0);
  }, []);

  // Filter content by type
  const linkedinPosts = contentItems.filter(
    (item) => item.content_type === "linkedin_post",
  );
  const emailPills = contentItems.filter(
    (item) => item.content_type === "email_pill",
  );

  // Render a single content card
  const renderContentCard = (
    item: ContentSnackResponse,
    index: number,
    type: "linkedin" | "email",
  ) => (
    <Card key={item.id} className="h-full">
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardTitle className="text-sm font-medium">
            {type === "linkedin" ? `LinkedIn Post ${index + 1}` : `Email Pill ${index + 1}`}
          </CardTitle>
          <Badge variant={type === "linkedin" ? "default" : "secondary"}>
            {type === "linkedin" ? "LinkedIn" : "Email"}
          </Badge>
        </div>
      </CardHeader>
      <CardContent>
        <p className="text-sm text-muted-foreground whitespace-pre-wrap">
          {item.content_text}
        </p>
      </CardContent>
    </Card>
  );

  // Show loading skeleton while polling
  if (polling || isLoading) {
    return (
      <div className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {[...Array(2)].map((_, i) => (
            <Card key={`linkedin-skeleton-${i}`}>
              <CardHeader className="pb-2">
                <Skeleton className="h-4 w-24" />
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <Skeleton className="h-4 w-full" />
                  <Skeleton className="h-4 w-3/4" />
                  <Skeleton className="h-4 w-1/2" />
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {[...Array(2)].map((_, i) => (
            <Card key={`email-skeleton-${i}`}>
              <CardHeader className="pb-2">
                <Skeleton className="h-4 w-24" />
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <Skeleton className="h-4 w-full" />
                  <Skeleton className="h-4 w-3/4" />
                  <Skeleton className="h-4 w-1/2" />
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  // Show error state
  if (error) {
    return (
      <Alert variant="destructive">
        <AlertTitle>Content Loading Error</AlertTitle>
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    );
  }

  // Show empty state if no asset selected
  if (!currentAssetId) {
    return (
      <Card>
        <CardContent className="pt-6">
          <div className="text-center text-muted-foreground">
            <p>Upload a PDF to see extracted content</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  // Show content cards with action buttons
  return (
    <div className="space-y-6 mt-12">
      {/* Stale state warning */}
      {showStaleWarning && (
        <Alert className="mb-4 border-amber-200 bg-amber-50 text-amber-800 [&>svg]:text-amber-600">
          <AlertTitle>Stale Asset Detected</AlertTitle>
          <AlertDescription>
            <div className="space-y-2">
              <p>
                This asset ({currentAssetId.slice(0, 8)}...) was uploaded a while ago but has no content.
                The database may have been cleared or the processing may have failed.
              </p>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleClearStaleState}
                  className="border-amber-300 text-amber-800 hover:bg-amber-100"
                >
                  <Trash2 className="h-4 w-4 mr-2" />
                  Clear Stale State
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleRefresh}
                  className="text-amber-800 hover:bg-amber-100"
                >
                  Try One More Time
                </Button>
              </div>
            </div>
          </AlertDescription>
        </Alert>
      )}

      {/* Action buttons */}
      <div className="flex justify-between items-center">
        <div className="text-sm text-muted-foreground">
          Asset ID: <code className="bg-muted px-2 py-1 rounded">{currentAssetId}</code>
        </div>
        <div className="flex gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={handleRefresh}
            disabled={polling || isLoading}
          >
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh Content
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={handleReset}
          >
            <Upload className="h-4 w-4 mr-2" />
            Upload New PDF
          </Button>
        </div>
      </div>

      {/* LinkedIn Posts Section */}
      <div>
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Briefcase className="h-5 w-5" /> LinkedIn Posts
          <Badge variant="outline">{linkedinPosts.length}</Badge>
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {linkedinPosts.slice(0, 2).map((item, index) =>
            renderContentCard(item, index, "linkedin"),
          )}
          {linkedinPosts.length === 0 && (
            <div className="col-span-2 text-center text-muted-foreground py-4">
              No LinkedIn posts extracted yet. The PDF may still be processing.
              {error && (
                <div className="mt-2 text-sm">
                  Error: {error}
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Email Pills Section */}
      <div>
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Mail className="h-5 w-5" /> Email Pills
          <Badge variant="outline">{emailPills.length}</Badge>
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {emailPills.slice(0, 2).map((item, index) =>
            renderContentCard(item, index, "email"),
          )}
          {emailPills.length === 0 && (
            <div className="col-span-2 text-center text-muted-foreground py-4">
              No email pills extracted yet. The PDF may still be processing.
              {error && (
                <div className="mt-2 text-sm">
                  Error: {error}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
