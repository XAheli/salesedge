import { useQuery } from "@tanstack/react-query";
import { get, getPaginated } from "../client";
import type { APIResponse } from "@/types/api";

export interface IntelligenceOverviewData {
  total_signals: number;
  signal_types: Record<string, number>;
  policy_signals: Array<{
    id: string;
    title: string;
    source: string;
    impact_score: number;
    impact: string;
    category: string;
    summary: string;
    published_at: string;
    source_url: string | null;
  }>;
  competitor_signals: Array<{
    id: string;
    title: string;
    competitor_name: string;
    source: string;
    impact_score: number;
    context: string;
    published_at: string;
  }>;
  market_signals: Array<{
    id: string;
    title: string;
    indicator: string;
    source: string;
    impact_score: number;
    value: string;
    change_pct: number | null;
    direction: string;
    published_at: string;
  }>;
  latest_signals: Array<{
    id: string;
    title: string;
    type: string;
    source: string;
    impact_score: number;
    published_at: string;
    summary: string;
  }>;
}

export function useIntelligenceOverview() {
  return useQuery({
    queryKey: ["competitive", "overview"],
    queryFn: async () => {
      const res = await get<IntelligenceOverviewData>("/v1/competitive/overview");
      if (!res.success && res.error) {
        throw new Error(res.error.message);
      }
      return res as APIResponse<IntelligenceOverviewData>;
    },
    staleTime: 60_000,
  });
}

export interface CompetitiveMention {
  id: string;
  deal_id: string | null;
  competitor_name: string;
  context: string;
  sentiment: "positive" | "neutral" | "negative" | null;
  detected_at: string;
  source: string;
}

export interface Battlecard {
  competitor_name: string;
  positioning: string;
  strengths: string[];
  weaknesses: string[];
  landmines: string[];
  proof_points: string[];
  last_updated: string;
}

export interface PolicySignal {
  id: string;
  title: string;
  category: string;
  impact: "low" | "medium" | "high";
  effective_date: string | null;
  summary: string;
  source_url: string | null;
}

export interface MarketSignal {
  id: string;
  indicator: string;
  value: string;
  change_pct: number | null;
  direction: "up" | "down" | "flat";
  geography: string;
  as_of: string;
}

export interface MarketSignalFilters {
  geography?: string[];
  category?: string[];
  page?: number;
  page_size?: number;
}

export function useCompetitiveMentions(dealId?: string) {
  return useQuery({
    queryKey: ["competitive", "mentions", dealId ?? "all"],
    queryFn: () =>
      getPaginated<CompetitiveMention>("/v1/competitive/mentions", {
        params: { deal_id: dealId },
      }),
  });
}

export function useBattlecards(competitorName?: string) {
  return useQuery({
    queryKey: ["competitive", "battlecards", competitorName ?? "all"],
    queryFn: async () => {
      const res = await get<Battlecard | Battlecard[]>("/v1/competitive/battlecards", {
        params: { competitor: competitorName },
      });
      if (!res.success && res.error) {
        throw new Error(res.error.message);
      }
      const raw = res.data;
      const normalized: Battlecard[] = Array.isArray(raw)
        ? raw
        : raw
          ? [raw]
          : [];
      return { ...res, data: normalized } as APIResponse<Battlecard[]>;
    },
  });
}

export function usePolicySignals(timeWindow: "7d" | "30d" | "90d" | "1y" = "30d") {
  return useQuery({
    queryKey: ["competitive", "policy-signals", timeWindow],
    queryFn: async () => {
      const res = await get<PolicySignal[]>("/v1/competitive/policy-signals", {
        params: { time_window: timeWindow },
      });
      if (!res.success && res.error) {
        throw new Error(res.error.message);
      }
      return res as APIResponse<PolicySignal[]>;
    },
    staleTime: 10 * 60 * 1000,
  });
}

export function useMarketSignals(filters: MarketSignalFilters = {}) {
  const { geography, category, page, page_size } = filters;

  return useQuery({
    queryKey: ["competitive", "market-signals", filters],
    queryFn: () =>
      getPaginated<MarketSignal>("/v1/competitive/market-signals", {
        params: {
          page,
          page_size,
          geography: geography?.length ? geography.join(",") : undefined,
          category: category?.length ? category.join(",") : undefined,
        },
      }),
    placeholderData: (prev) => prev,
  });
}
