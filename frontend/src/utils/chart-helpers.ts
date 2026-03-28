import { format, parseISO } from "date-fns";
import { toIndianUnits } from "./indian-formatting";

export type ChartGranularity = "hour" | "day" | "week" | "month" | "quarter" | "year";

const CHART_PALETTE = [
  "#2563eb",
  "#059669",
  "#d97706",
  "#dc2626",
  "#7c3aed",
  "#db2777",
  "#0d9488",
  "#ea580c",
  "#4f46e5",
  "#65a30d",
] as const;

export function formatChartDate(date: Date | string, granularity: ChartGranularity): string {
  const d = typeof date === "string" ? parseISO(date) : date;
  if (Number.isNaN(d.getTime())) {
    return "";
  }
  switch (granularity) {
    case "hour":
      return format(d, "MMM d, HH:mm");
    case "day":
      return format(d, "MMM d");
    case "week":
      return format(d, "'W'w yyyy");
    case "month":
      return format(d, "MMM yyyy");
    case "quarter":
      return format(d, "QQQ yyyy");
    case "year":
      return format(d, "yyyy");
    default:
      return format(d, "MMM d");
  }
}

export function generateSparklineData(values: number[]): number[] {
  if (!values.length) {
    return [];
  }
  const min = Math.min(...values);
  const max = Math.max(...values);
  const span = max - min || 1;
  return values.map((v) => (v - min) / span);
}

export function calculateTrendDirection(
  current: number,
  previous: number,
  epsilon = 1e-9,
): "up" | "down" | "flat" {
  const delta = current - previous;
  if (Math.abs(delta) <= epsilon) {
    return "flat";
  }
  return delta > 0 ? "up" : "down";
}

export function getChartColor(index: number): string {
  return CHART_PALETTE[Math.abs(index) % CHART_PALETTE.length]!;
}

export type AxisValueType = "inr" | "percent" | "count" | "default";

export function formatAxisValue(value: number, type: AxisValueType): string {
  if (!Number.isFinite(value)) {
    return "";
  }
  switch (type) {
    case "percent":
      return `${value.toFixed(0)}%`;
    case "count":
      return value >= 1_000_000
        ? `${(value / 1_000_000).toFixed(1)}M`
        : value >= 1000
          ? `${(value / 1000).toFixed(1)}K`
          : `${Math.round(value)}`;
    case "inr": {
      const { value: v, unit } = toIndianUnits(value);
      const rounded = unit ? Number(v.toFixed(2)) : Math.round(v);
      return unit ? `${rounded}${unit}` : `${rounded}`;
    }
    case "default":
    default: {
      const abs = Math.abs(value);
      if (abs >= 1_00_00_000) {
        return `${(value / 1_00_00_000).toFixed(1)}Cr`;
      }
      if (abs >= 1_00_000) {
        return `${(value / 1_00_000).toFixed(1)}L`;
      }
      if (abs >= 1000) {
        return `${(value / 1000).toFixed(1)}K`;
      }
      return value.toFixed(value % 1 === 0 ? 0 : 1);
    }
  }
}
