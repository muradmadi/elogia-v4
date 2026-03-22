import { useState } from "react";
import { useStore } from "@nanostores/react";
import { $currentAssetId, $isLoadingContent, $contentError } from "../../stores/asset";
import { uploadAsset } from "../../services/assetApi";
import { Button } from "../ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "../ui/card";
import { Alert, AlertDescription, AlertTitle } from "../ui/alert";
import { cn } from "../../lib/utils";
import { FileText, Upload } from "lucide-react";

interface PdfUploaderProps {
  onUploadComplete?: (assetId: string) => void;
}

export function PdfUploader({ onUploadComplete }: PdfUploaderProps) {
  const currentAssetId = useStore($currentAssetId);
  const isLoading = useStore($isLoadingContent);
  const error = useStore($contentError);

  const [isDragging, setIsDragging] = useState(false);
  const [uploadProgress, setUploadProgress] = useState<string | null>(null);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = async (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);

    const files = Array.from(e.dataTransfer.files);
    const pdfFile = files.find((file) => file.type === "application/pdf");

    if (pdfFile) {
      await handleFileUpload(pdfFile);
    } else {
      $contentError.set("Please drop a PDF file");
    }
  };

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      await handleFileUpload(file);
    }
  };

  const handleFileUpload = async (file: File) => {
    if (!file.type.includes("pdf")) {
      $contentError.set("Please select a PDF file");
      return;
    }

    $isLoadingContent.set(true);
    $contentError.set(null);
    setUploadProgress("Uploading PDF...");

    try {
      const response = await uploadAsset(file);
      $currentAssetId.set(response.asset_id);
      setUploadProgress("Processing PDF...");
      onUploadComplete?.(response.asset_id);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Upload failed";
      $contentError.set(message);
    } finally {
      $isLoadingContent.set(false);
      setUploadProgress(null);
    }
  };

  // Clear the file input to allow re-uploading the same file
  const clearFileInput = () => {
    const fileInput = document.getElementById("pdf-upload") as HTMLInputElement;
    if (fileInput) {
      fileInput.value = "";
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Upload PDF Asset</CardTitle>
      </CardHeader>
      <CardContent>
        <div
          className={cn(
            "border-2 border-dashed rounded-lg p-8 text-center transition-colors",
            isDragging
              ? "border-primary bg-primary/10"
              : "border-muted-foreground/25 hover:border-muted-foreground/50",
            (isLoading || currentAssetId) && "opacity-50 pointer-events-none",
          )}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
        >
          <div className="space-y-4">
            <FileText className="h-12 w-12 mx-auto text-muted-foreground" />
            <div>
              <p className="text-lg font-medium">
                {isDragging ? "Drop PDF here" : "Drag & drop a PDF file"}
              </p>
              <p className="text-sm text-muted-foreground">
                or click to browse
              </p>
            </div>
            <input
              type="file"
              accept=".pdf,application/pdf"
              onChange={handleFileSelect}
              className="hidden"
              id="pdf-upload"
              disabled={isLoading || !!currentAssetId}
              onClick={clearFileInput}
            />
            <Button
              type="button"
              variant="outline"
              onClick={() => {
                clearFileInput();
                document.getElementById("pdf-upload")?.click();
              }}
              disabled={isLoading || !!currentAssetId}
            >
              <Upload className="h-4 w-4 mr-2" />
              Select PDF File
            </Button>
          </div>
        </div>

        {uploadProgress && (
          <div className="mt-4 text-center text-sm text-muted-foreground">
            {uploadProgress}
          </div>
        )}

        {currentAssetId && !error && (
          <Alert className="mt-4" variant="default">
            <AlertTitle>PDF Uploaded Successfully</AlertTitle>
            <AlertDescription>
              <div className="space-y-2">
                <p>Asset ID: <code className="bg-muted px-2 py-1 rounded text-xs">{currentAssetId}</code></p>
                <p className="text-sm text-muted-foreground">
                  The PDF is being processed. You can refresh the content below to see results.
                </p>
              </div>
            </AlertDescription>
          </Alert>
        )}

        {error && (
          <Alert className="mt-4" variant="destructive">
            <AlertTitle>Upload Error</AlertTitle>
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}
      </CardContent>
    </Card>
  );
}
