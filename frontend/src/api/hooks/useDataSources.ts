import { useQuery } from "@tanstack/react-query";
import { get } from "../client";

export type DataSourceStatus = "healthy" | "degraded" | "down" | "unknown";

export interface DataSourceHealthItem {
  name: string;
  status: DataSourceStatus;
  last_check: string;
  response_time_ms: number;
  error_rate: number;
  data_freshness: string;
  cache_hit_rate: number;
  records_ingested: number | null;
  tier: number;
}

interface DataSourceListResponse {
  sources: DataSourceHealthItem[];
  overall_health: string;
  stale_count: number;
  error_count: number;
}

export function useDataSourceList() {
  return useQuery({
    queryKey: ["data-sources", "list"],
    queryFn: async () => {
      const res = await get<DataSourceListResponse>("/v1/data-sources");
      return res;
    },
    refetchInterval: 60_000,
  });
}

export function useHealthReady() {
  return useQuery({
    queryKey: ["health", "ready"],
    queryFn: () => get<{ status: string; timestamp: string }>("/v1/health/ready"),
    refetchInterval: 30_000,
  });
}
