import { memo } from "react";

interface ConfidenceBadgeProps {
  confidence: number;
  size?: "sm" | "md" | "lg";
  showLabel?: boolean;
  className?: string;
}

function getConfidenceConfig(c: number) {
  if (c >= 0.8) return { label: "High", color: "text-revenue-positive", bg: "bg-revenue-positive-bg", stroke: "#059669" };
  if (c >= 0.5) return { label: "Medium", color: "text-caution", bg: "bg-caution-bg", stroke: "#D97706" };
  return { label: "Low", color: "text-risk", bg: "bg-risk-bg", stroke: "#DC2626" };
}

const SIZE_MAP = {
  sm: { pill: "px-1.5 py-0.5 text-[10px]", ring: 16, strokeWidth: 2 },
  md: { pill: "px-2 py-0.5 text-xs", ring: 24, strokeWidth: 2.5 },
  lg: { pill: "px-2.5 py-1 text-sm", ring: 32, strokeWidth: 3 },
};

export const ConfidenceBadge = memo(function ConfidenceBadge({
  confidence,
  size = "sm",
  showLabel = false,
  className = "",
}: ConfidenceBadgeProps) {
  const cfg = getConfidenceConfig(confidence);
  const sz = SIZE_MAP[size];
  const pct = Math.round(confidence * 100);

  if (showLabel) {
    const r = sz.ring / 2;
    const circumference = 2 * Math.PI * (r - sz.strokeWidth);
    const offset = circumference * (1 - confidence);

    return (
      <div className={`inline-flex items-center gap-1.5 ${className}`}>
        <svg width={sz.ring} height={sz.ring} className="-rotate-90">
          <circle
            cx={r}
            cy={r}
            r={r - sz.strokeWidth}
            fill="none"
            stroke="currentColor"
            strokeWidth={sz.strokeWidth}
            className="text-neutral-bg"
          />
          <circle
            cx={r}
            cy={r}
            r={r - sz.strokeWidth}
            fill="none"
            stroke={cfg.stroke}
            strokeWidth={sz.strokeWidth}
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            strokeLinecap="round"
          />
        </svg>
        <span className={`font-medium ${cfg.color} ${sz.pill}`}>
          {pct}% {cfg.label}
        </span>
      </div>
    );
  }

  return (
    <span
      className={`inline-flex items-center rounded-full font-medium ${cfg.bg} ${cfg.color} ${sz.pill} ${className}`}
    >
      {pct}%
    </span>
  );
});
