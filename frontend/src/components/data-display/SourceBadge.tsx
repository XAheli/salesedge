import { memo } from "react";

type Tier = "tier1" | "tier2" | "tier3";

interface SourceBadgeProps {
  name: string;
  tier: Tier;
  className?: string;
}

const TIER_STYLES: Record<Tier, string> = {
  tier1: "bg-revenue-positive-bg text-revenue-positive",
  tier2: "bg-info-bg text-info",
  tier3: "bg-data-quality-bg text-data-quality",
};

export const SourceBadge = memo(function SourceBadge({
  name,
  tier,
  className = "",
}: SourceBadgeProps) {
  return (
    <span
      className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[10px] font-medium ${TIER_STYLES[tier]} ${className}`}
    >
      <span
        className={`inline-block h-1.5 w-1.5 rounded-full ${
          tier === "tier1"
            ? "bg-revenue-positive"
            : tier === "tier2"
              ? "bg-info"
              : "bg-data-quality"
        }`}
      />
      {name}
    </span>
  );
});
