export interface ExecutiveSummary {
  kpis: ExecutiveKPIs;
  revenue_forecast: RevenueForecast;
  pipeline_velocity: PipelineVelocityData;
  funnel: FunnelData;
  risk_heatmap: RiskHeatmapData;
  top_deals: DealSummary[];
}

export interface ExecutiveKPIs {
  arr: KPIMetric;
  mrr: KPIMetric;
  pipeline_value: KPIMetric;
  win_rate: KPIMetric;
  avg_deal_cycle: KPIMetric;
  net_revenue_retention: KPIMetric;
}

export interface KPIMetric {
  value: number;
  formatted: string;
  trend_pct: number;
  trend_direction: "up" | "down" | "flat";
  is_positive: boolean;
  sparkline: number[];
  confidence: number;
  source: string;
  last_updated: string;
}

export interface RevenueForecast {
  historical: Array<{ date: string; revenue: number }>;
  forecast: Array<{
    date: string;
    p10: number;
    p50: number;
    p90: number;
  }>;
  currency: "INR";
  format: "crores" | "lakhs";
}

export interface PipelineVelocityData {
  data: Array<{
    week: string;
    avg_days_in_stage: number;
    throughput: number;
    rolling_mean_days: number;
    upper_control_limit: number;
    lower_control_limit: number;
  }>;
}

export interface FunnelData {
  stages: Array<{
    name: string;
    count: number;
    conversion_rate: number;
    avg_time_in_stage: number;
    confidence_interval: [number, number];
    sample_size: number;
  }>;
  comparison_period?: "previous_period" | "target";
  delta_values?: number[];
}

export interface RiskHeatmapData {
  rows: Array<{
    deal_id: string;
    deal_name: string;
    account: string;
    risk_factors: Array<{
      factor: string;
      severity: "low" | "medium" | "high" | "critical";
      score: number;
    }>;
    overall_risk_score: number;
  }>;
  factors: string[];
}

export interface DealSummary {
  id: string;
  name: string;
  account: string;
  value: number;
  value_formatted: string;
  stage: string;
  probability: number;
  days_in_stage: number;
  risk_level: "low" | "medium" | "high" | "critical";
  owner: string;
  next_action: string;
  expected_close: string;
}
