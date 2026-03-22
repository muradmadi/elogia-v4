import { useState } from "react";
import { Card, CardContent } from "../ui/card";
import { Button } from "../ui/button";

export function InfoModal() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <>
      {/* Info Icon Button */}
      <button
        onClick={() => setIsOpen(true)}
        className="flex h-8 w-8 items-center justify-center rounded-full bg-muted text-sm font-bold text-muted-foreground transition-colors hover:bg-accent hover:text-foreground"
        aria-label="Show instructions"
      >
        i
      </button>

      {/* Modal */}
      {isOpen && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-overlay backdrop-blur-sm"
          onClick={() => setIsOpen(false)}
        >
          <div
            className="relative mx-4 w-full max-w-lg rounded-lg border border-border bg-background shadow-xl"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Close Button */}
            <div className="flex items-center justify-between border-b border-border px-6 py-4">
              <h3 className="text-lg font-semibold">How to Use</h3>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setIsOpen(false)}
                className="h-8 w-8 p-0"
              >
                ✕
              </Button>
            </div>

            {/* Content */}
            <div className="p-6">
              <p className="text-sm text-muted-foreground leading-relaxed">
                Enter an email address to trigger Clay enrichment. The system will
                collect person, company, role intelligence, product analysis, pain
                points, and outreach strategy data.
              </p>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
