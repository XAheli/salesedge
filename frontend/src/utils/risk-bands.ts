export const RISK_BANDS = {
  critical: { min: 70, color: "text-red-700", bg: "bg-risk" },
  high: { min: 50, color: "text-risk", bg: "bg-risk/80" },
  medium: { min: 30, color: "text-caution", bg: "bg-caution" },
  low: { min: 0, color: "text-revenue-positive", bg: "bg-revenue-positive" },
} as const;

export function classifyRisk(score: number): keyof typeof RISK_BANDS {
  if (score >= 70) return "critical";
  if (score >= 50) return "high";
  if (score >= 30) return "medium";
  return "low";
}
