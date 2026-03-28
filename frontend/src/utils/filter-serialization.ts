import type { TimeWindow } from "@/stores/useFilterStore";

export interface FilterState {
  timeWindow: TimeWindow;
  customDateRange: { start: string; end: string } | null;
  territory: string[];
  segment: string[];
  industry: string[];
}

function isTimeWindow(v: string | null): v is TimeWindow {
  return v === "7d" || v === "30d" || v === "90d" || v === "1y" || v === "custom";
}

export function serializeFilters(filters: FilterState): URLSearchParams {
  const p = new URLSearchParams();
  p.set("tw", filters.timeWindow);
  if (filters.customDateRange) {
    p.set("start", filters.customDateRange.start);
    p.set("end", filters.customDateRange.end);
  }
  if (filters.territory.length) {
    p.set("territory", filters.territory.join(","));
  }
  if (filters.segment.length) {
    p.set("segment", filters.segment.join(","));
  }
  if (filters.industry.length) {
    p.set("industry", filters.industry.join(","));
  }
  return p;
}

export function deserializeFilters(params: URLSearchParams): FilterState {
  const twRaw = params.get("tw");
  const timeWindow: TimeWindow = isTimeWindow(twRaw) ? twRaw : "30d";
  const start = params.get("start");
  const end = params.get("end");
  const customDateRange =
    timeWindow === "custom" && start && end ? { start, end } : null;

  const split = (key: string) =>
    params
      .get(key)
      ?.split(",")
      .map((s) => s.trim())
      .filter(Boolean) ?? [];

  return {
    timeWindow,
    customDateRange,
    territory: split("territory"),
    segment: split("segment"),
    industry: split("industry"),
  };
}

export function mergeFiltersIntoUrl(
  baseUrl: string,
  filters: FilterState,
): string {
  const url = new URL(baseUrl, typeof window !== "undefined" ? window.location.origin : "http://localhost");
  const next = serializeFilters(filters);
  next.forEach((v, k) => url.searchParams.set(k, v));
  return url.pathname + url.search;
}
