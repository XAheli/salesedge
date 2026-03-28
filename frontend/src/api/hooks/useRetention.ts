import { useQuery } from "@tanstack/react-query";
import { get, getPaginated } from "../client";
import type { APIResponse } from "@/types/api";

export interface RetentionOverviewData {
  total_customers: number;
  at_risk_count: number;
  retention_rate: number;
  risk_distribution: Record<string, number>;
  at_risk_deals: Array<{
    id: string;
    account_name: string;
    value_inr: number;
    risk_score: number;
    risk_band: string;
    days_since_last_activity: number;
    churn_probability: number;
    drivers: string[];
  }>;
  loss_reasons: Record<string, number>;
  total_value_at_risk: number;
}

export function useRetentionOverview() {
  return useQuery({
    queryKey: ["retention", "overview"],
    queryFn: async () => {
      const res = await get<RetentionOverviewData>("/v1/retention/overview");
      if (!res.success && res.error) {
        throw new Error(res.error.message);
      }
      return res as APIResponse<RetentionOverviewData>;
    },
    staleTime: 60_000,
  });
}

export interface RetentionCohortRow {
  cohort_period: string;
  period_label: string;
  initial_customers: number;
  retained: number[];
  churn_rate: number[];
  revenue_retention: number[];
}

export interface RetentionCohortsResponse {
  cohorts: RetentionCohortRow[];
  granularity: "month" | "quarter";
}

export interface ChurnPrediction {
  customer_id: string;
  account_name: string;
  churn_probability: number;
  risk_band: "low" | "medium" | "high" | "critical";
  drivers: string[];
  next_review_at: string;
}

export interface ChurnPredictionFilters {
  risk_band?: string[];
  segment?: string[];
  territory?: string[];
  page?: number;
  page_size?: number;
}

export interface CustomerHealth {
  customer_id: string;
  health_score: number;
  trend: "improving" | "stable" | "declining";
  nrr_contribution: number;
  engagement_index: number;
  support_tickets_90d: number;
  payment_health: "good" | "watch" | "at_risk";
  summary: string;
  updated_at: string;
}

export function useRetentionCohorts(timeWindow: "7d" | "30d" | "90d" | "1y" = "90d") {
  return useQuery({
    queryKey: ["retention", "cohorts", timeWindow],
    queryFn: async () => {
      const res = await get<RetentionCohortsResponse>("/v1/retention/cohorts", {
        params: { time_window: timeWindow },
      });
      if (!res.success && res.error) {
        throw new Error(res.error.message);
      }
      return res as APIResponse<RetentionCohortsResponse>;
    },
    staleTime: 5 * 60 * 1000,
  });
}

export function useChurnPredictions(filters: ChurnPredictionFilters = {}) {
  const { risk_band, segment, territory, page, page_size } = filters;

  return useQuery({
    queryKey: ["retention", "churn-predictions", filters],
    queryFn: () =>
      getPaginated<ChurnPrediction>("/v1/retention/churn-predictions", {
        params: {
          page,
          page_size,
          risk_band: risk_band?.length ? risk_band.join(",") : undefined,
          segment: segment?.length ? segment.join(",") : undefined,
          territory: territory?.length ? territory.join(",") : undefined,
        },
      }),
    placeholderData: (prev) => prev,
  });
}

export function useCustomerHealth(customerId: string | undefined) {
  return useQuery({
    queryKey: ["retention", "customer-health", customerId],
    queryFn: async () => {
      if (!customerId) {
        throw new Error("customerId is required");
      }
      const res = await get<CustomerHealth>(`/v1/retention/customers/${customerId}/health`);
      if (!res.success && res.error) {
        throw new Error(res.error.message);
      }
      return res as APIResponse<CustomerHealth>;
    },
    enabled: Boolean(customerId),
  });
}
