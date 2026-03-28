import { useQuery } from "@tanstack/react-query";
import { get, getPaginated } from "../client";
import type { DealDetail, DealFilterParams } from "@/types/api";

export interface DealItem {
  id: string;
  prospect_name: string;
  stage: string;
  value_inr: number;
  risk_score: number;
  days_in_stage: number;
  owner: string;
  last_activity: string | null;
}

export interface DealRiskSummary {
  total_active: number;
  risk_distribution: Record<string, number>;
  critical_deal_ids: string[];
  high_deal_ids: string[];
}

export function computeRiskLevel(
  riskScore: number,
): "critical" | "high" | "medium" | "low" {
  if (riskScore >= 0.7) return "critical";
  if (riskScore >= 0.5) return "high";
  if (riskScore >= 0.3) return "medium";
  return "low";
}

export function useDealList(filters: DealFilterParams = {}) {
  const {
    search,
    stage,
    risk_level,
    owner,
    value_min,
    value_max,
    expected_close_before,
    expected_close_after,
    sort_by,
    sort_order,
    page,
    page_size,
  } = filters;

  return useQuery({
    queryKey: ["deals", "list", filters],
    queryFn: () =>
      getPaginated<DealItem>("/v1/deals", {
        params: {
          search,
          value_min,
          value_max,
          expected_close_before,
          expected_close_after,
          sort_by,
          sort_order,
          page,
          page_size,
          stage: stage?.length ? stage.join(",") : undefined,
          risk_level: risk_level?.length ? risk_level.join(",") : undefined,
          owner: owner?.length ? owner.join(",") : undefined,
        },
      }),
    placeholderData: (prev) => prev,
  });
}

export function useDealDetail(dealId: string | undefined) {
  return useQuery({
    queryKey: ["deals", "detail", dealId],
    queryFn: async () => {
      if (!dealId) {
        throw new Error("dealId is required");
      }
      return get<DealDetail>(`/v1/deals/${dealId}`);
    },
    enabled: Boolean(dealId),
  });
}

export function useDealRiskSummary() {
  return useQuery({
    queryKey: ["deals", "risk-summary"],
    queryFn: () => get<DealRiskSummary>("/v1/deals/risk-summary"),
    staleTime: 2 * 60 * 1000,
  });
}
