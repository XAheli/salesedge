export interface APIResponse<T> {
  success: boolean;
  data: T | null;
  error: ErrorDetail | null;
  metadata: ResponseMetadata;
}

export interface ResponseMetadata {
  timestamp: string;
  request_id: string;
  data_freshness: string | null;
  source_attribution: SourceAttribution[];
  confidence_score: number | null;
  cache_status: "hit" | "miss" | "stale";
}

export interface SourceAttribution {
  source_name: string;
  source_url: string | null;
  last_updated: string;
  reliability_tier: "tier1" | "tier2" | "tier3";
}

export interface ErrorDetail {
  code: string;
  message: string;
  details: Record<string, unknown> | null;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  pages?: number;
}

export interface PaginationInfo {
  page: number;
  page_size: number;
  total_items: number;
  total_pages: number;
  has_next: boolean;
  has_previous: boolean;
}
