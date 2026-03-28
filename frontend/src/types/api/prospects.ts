export interface ProspectSummary {
  id: string;
  company_name: string;
  industry: string;
  nic_code: string | null;
  segment: "enterprise" | "mid_market" | "smb" | "startup";
  territory: string;
  state: string;
  fit_score: number;
  fit_confidence: number;
  enrichment_completeness: number;
  last_activity: string | null;
  status: "new" | "researching" | "qualified" | "outreach" | "engaged" | "disqualified";
  estimated_revenue: number | null;
  estimated_revenue_formatted: string | null;
  source: string;
  created_at: string;
}

export interface ProspectDetail {
  id: string;
  company_name: string;
  legal_name: string | null;
  cin: string | null;
  gst_number: string | null;
  pan: string | null;
  industry: string;
  nic_code: string | null;
  nic_description: string | null;
  segment: "enterprise" | "mid_market" | "smb" | "startup";
  territory: string;
  state: string;
  city: string | null;
  website: string | null;
  employee_count: number | null;
  annual_revenue: number | null;
  annual_revenue_formatted: string | null;
  founded_year: number | null;
  listed: boolean;
  exchange: "NSE" | "BSE" | "both" | null;
  ticker: string | null;
  dpiit_recognized: boolean;

  fit_score: FitScoreBreakdown;
  enrichment: EnrichmentData;
  contacts: ProspectContact[];
  timeline: EnrichmentEvent[];
  outreach_sequences: OutreachSequence[];
  industry_context: IndustryContext;
}

export interface FitScoreBreakdown {
  overall: number;
  confidence: number;
  factors: Array<{
    name: string;
    weight: number;
    score: number;
    normalized: number;
    source: string;
  }>;
  last_computed: string;
}

export interface EnrichmentData {
  completeness: number;
  sources: Array<{
    source: string;
    status: "complete" | "partial" | "pending" | "failed";
    last_updated: string | null;
    fields_populated: number;
    fields_total: number;
  }>;
  mca_data: MCAData | null;
  financial_data: FinancialData | null;
  gst_data: GSTData | null;
}

export interface MCAData {
  company_status: string;
  registration_date: string;
  authorized_capital: number | null;
  paid_up_capital: number | null;
  directors: Array<{
    name: string;
    din: string;
    designation: string;
  }>;
}

export interface FinancialData {
  revenue_ttm: number | null;
  revenue_growth_yoy: number | null;
  net_profit_ttm: number | null;
  market_cap: number | null;
  pe_ratio: number | null;
  debt_to_equity: number | null;
  last_filing_date: string | null;
}

export interface GSTData {
  gst_status: "active" | "inactive" | "cancelled" | "suspended";
  registration_date: string;
  filing_frequency: string;
  last_filed: string | null;
  compliance_rating: string | null;
}

export interface ProspectContact {
  id: string;
  name: string;
  title: string;
  email: string | null;
  phone: string | null;
  linkedin_url: string | null;
  is_decision_maker: boolean;
  engagement_score: number;
}

export interface EnrichmentEvent {
  id: string;
  timestamp: string;
  event_type: "enrichment" | "signal" | "outreach" | "score_change" | "status_change";
  source: string;
  description: string;
  details: Record<string, unknown>;
}

export interface OutreachSequence {
  id: string;
  name: string;
  status: "draft" | "active" | "paused" | "completed";
  steps: Array<{
    step: number;
    channel: "email" | "linkedin" | "call" | "sms";
    subject: string | null;
    status: "pending" | "sent" | "opened" | "replied" | "bounced";
    scheduled_at: string;
    sent_at: string | null;
  }>;
  metrics: {
    open_rate: number | null;
    reply_rate: number | null;
    meeting_rate: number | null;
  };
}

export interface IndustryContext {
  sector_growth_rate: number | null;
  sector_outlook: "positive" | "neutral" | "negative" | null;
  government_schemes: string[];
  regulatory_changes: string[];
  key_indicators: Array<{
    name: string;
    value: string;
    trend: "up" | "down" | "flat";
    source: string;
  }>;
}

export interface ProspectFilterParams {
  search?: string;
  segment?: string[];
  territory?: string[];
  industry?: string[];
  status?: string[];
  fit_score_min?: number;
  fit_score_max?: number;
  sort_by?: string;
  sort_order?: "asc" | "desc";
  page?: number;
  page_size?: number;
}
