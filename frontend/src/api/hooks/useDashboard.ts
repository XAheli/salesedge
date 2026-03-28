import { useQuery } from "@tanstack/react-query";
import { get } from "../client";
import type { APIResponse, ExecutiveSummary } from "@/types/api";

export interface ExecutiveSummaryParams {
  time_window?: "7d" | "30d" | "90d" | "1y";
  territory?: string;
  segment?: string;
}

export function useExecutiveSummary(params: ExecutiveSummaryParams = {}) {
  return useQuery({
    queryKey: ["dashboard", "executive-summary", params],
    queryFn: async () => {
      const res = await get<ExecutiveSummary>("/v1/dashboard/executive-summary", {
        params: {
          time_window: params.time_window,
          territory: params.territory,
          segment: params.segment,
        },
      });
      if (!res.success && res.error) {
        throw new Error(res.error.message);
      }
      return res as APIResponse<ExecutiveSummary>;
    },
    staleTime: 5 * 60 * 1000,
    refetchInterval: 60 * 1000,
  });
}
