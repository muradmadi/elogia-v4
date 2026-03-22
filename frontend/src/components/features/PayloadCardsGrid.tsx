import { useStore } from "@nanostores/react";
import { Card } from "../ui/card";
import { cn } from "../../lib/utils";
import { PAYLOAD_DEFINITIONS, type PayloadInfo } from "../../lib/types";
import {
  $payloadStatus,
  $currentJobId,
  $isDetailModalOpen,
  $selectedPayloadType,
} from "../../stores/enrichment";
import { PayloadDetailModal } from "./PayloadDetailModal";


export function PayloadCardsGrid() {
  const payloadStatus = useStore($payloadStatus);
  const jobId = useStore($currentJobId);

  function handleCardClick(payload: PayloadInfo, e: React.MouseEvent) {
    e.stopPropagation();
    if (!jobId) {
      return;
    }
    $selectedPayloadType.set(payload.key);
    $isDetailModalOpen.set(true);
  }

  return (
    <>
      <div className="grid grid-cols-3 gap-4">
        {PAYLOAD_DEFINITIONS.map((payload) => {
          const hasArrived = payloadStatus[payload.payloadField];

          return (
            <Card
              key={payload.key}
              className={cn(
                "p-4 cursor-pointer hover:opacity-90 transition-opacity",
                hasArrived ? "opacity-100" : "opacity-60"
              )}
              onClick={(e) => handleCardClick(payload, e)}
            >
              <p className="text-sm font-medium">{payload.label}</p>
            </Card>
          );
        })}
      </div>

      <PayloadDetailModal />
    </>
  );
}
