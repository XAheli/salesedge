import { memo, useMemo } from "react";

interface FreshnessPulseProps {
  lastUpdated: string | Date;
  freshThresholdMinutes?: number;
  agingThresholdMinutes?: number;
  className?: string;
}

function getMinutesAgo(d: Date): number {
  return Math.max(0, Math.floor((Date.now() - d.getTime()) / 60_000));
}

function formatTimeAgo(minutes: number): string {
  if (minutes < 1) return "Just now";
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  return `${days}d ago`;
}

export const FreshnessPulse = memo(function FreshnessPulse({
  lastUpdated,
  freshThresholdMinutes = 5,
  agingThresholdMinutes = 60,
  className = "",
}: FreshnessPulseProps) {
  const date = useMemo(
    () => (lastUpdated instanceof Date ? lastUpdated : new Date(lastUpdated)),
    [lastUpdated],
  );
  const minutes = getMinutesAgo(date);

  const status =
    minutes <= freshThresholdMinutes
      ? "fresh"
      : minutes <= agingThresholdMinutes
        ? "aging"
        : "stale";

  const dotColor = {
    fresh: "bg-revenue-positive",
    aging: "bg-caution",
    stale: "bg-risk",
  }[status];

  const pulseColor = {
    fresh: "bg-revenue-positive/40",
    aging: "bg-caution/40",
    stale: "bg-risk/40",
  }[status];

  return (
    <span className={`inline-flex items-center gap-1.5 text-xs text-text-secondary ${className}`}>
      <span className="relative flex h-2.5 w-2.5">
        {status === "fresh" && (
          <span
            className={`absolute inline-flex h-full w-full animate-ping rounded-full ${pulseColor}`}
          />
        )}
        <span className={`relative inline-flex h-2.5 w-2.5 rounded-full ${dotColor}`} />
      </span>
      Updated {formatTimeAgo(minutes)}
    </span>
  );
});
