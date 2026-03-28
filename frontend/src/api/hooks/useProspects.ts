import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { get, getPaginated, post } from "../client";
import type { APIResponse, ProspectDetail } from "@/types/api";

export interface ProspectListItem {
  id: string;
  company_name: string;
  industry: string;
  nic_code: string | null;
  revenue_band_inr: string | null;
  employee_count: number | null;
  state: string;
  fit_score: number | null;
  confidence: number | null;
  last_enriched: string | null;
}

export interface ProspectListFilters {
  search?: string;
  sort_by?: string;
  sort_order?: "asc" | "desc";
  page?: number;
  page_size?: number;
  state?: string[];
  industry?: string[];
  min_fit_score?: number;
}

function buildProspectListParams(
  filters: ProspectListFilters,
): Record<string, string | number | undefined> {
  return {
    search: filters.search,
    sort_by: filters.sort_by,
    sort_order: filters.sort_order,
    page: filters.page,
    page_size: filters.page_size,
    min_fit_score: filters.min_fit_score,
    state: filters.state?.length ? filters.state.join(",") : undefined,
    industry: filters.industry?.length ? filters.industry.join(",") : undefined,
  };
}

export function useProspectList(filters: ProspectListFilters = {}) {
  return useQuery({
    queryKey: ["prospects", "list", filters],
    queryFn: () =>
      getPaginated<ProspectListItem>("/v1/prospects", {
        params: buildProspectListParams(filters),
      }),
    placeholderData: (prev) => prev,
  });
}

export function useProspectDetail(prospectId: string | undefined) {
  return useQuery({
    queryKey: ["prospects", "detail", prospectId],
    queryFn: async () => {
      if (!prospectId) {
        throw new Error("prospectId is required");
      }
      return get<ProspectDetail>(`/v1/prospects/${prospectId}`);
    },
    enabled: Boolean(prospectId),
  });
}

export function useEnrichProspect() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (prospectId: string) => {
      return post<{ status: string; job_id?: string }>(
        `/v1/prospects/${prospectId}/enrich`,
      );
    },
    onSuccess: async (_data, prospectId) => {
      await queryClient.invalidateQueries({
        queryKey: ["prospects", "detail", prospectId],
      });
      await queryClient.invalidateQueries({
        queryKey: ["prospects", "list"],
      });
    },
  });
}
