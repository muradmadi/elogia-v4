import { useState } from "react";
import { cn } from "@/lib/utils";

interface VideoEmbedProps {
  videoId: string;
  title: string;
}

export function VideoEmbed({ videoId, title }: VideoEmbedProps) {
  const [loaded, setLoaded] = useState(false);

  const thumbnailUrl = `https://img.youtube.com/vi/${videoId}/maxresdefault.jpg`;

  return (
    <div className="relative aspect-video w-full overflow-hidden rounded-lg border border-border bg-card">
      {loaded ? (
        <iframe
          src={`https://www.youtube.com/embed/${videoId}?autoplay=1`}
          title={title}
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
          allowFullScreen
          className="absolute inset-0 h-full w-full"
        />
      ) : (
        <button
          onClick={() => setLoaded(true)}
          className="group absolute inset-0 flex h-full w-full items-center justify-center bg-background"
          aria-label={`Play ${title}`}
        >
          <img
            src={thumbnailUrl}
            alt={title}
            className="absolute inset-0 h-full w-full object-cover opacity-60 transition-opacity group-hover:opacity-80"
          />
          {/* Play Button */}
          <div className="relative z-10 flex h-16 w-16 items-center justify-center rounded-full bg-destructive transition-transform group-hover:scale-110">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="ml-1 h-7 w-7 text-destructive-foreground"
              fill="currentColor"
              viewBox="0 0 24 24"
            >
              <path d="M8 5v14l11-7z" />
            </svg>
          </div>
        </button>
      )}
    </div>
  );
}
