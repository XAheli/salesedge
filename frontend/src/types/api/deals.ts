export interface DealListItem {
  id: string;
  name: string;
  account_name: string;
  account_id: string;
  value: number;
  value_formatted: string;
  currency: "INR";
  stage: DealStage;
  probability: number;
  risk_score: number;
  risk_level: "low" | "medium" | "high" | "critical";
  risk_factors_count: number;
  owner: string;
  days_in_stage: number;
  expected_close_date: string;
  last_activity_date: string | null;
  engagement_score: number;
  competitor_mentions: number;
  created_at: string;
}

export type DealStage =
  | "lead"
  | "mql"
  | "sql"
  | "opportunity"
  | "proposal"
  | "negotiation"
  | "won"
  | "lost";

export interface DealDetail {
  id: string;
  name: string;
  account_name: string;
  account_id: string;
  value: number;
  value_formatted: string;
  currency: "INR";
  stage: DealStage;
  probability: number;
  expected_close_date: string;
  actual_close_date: string | null;
  owner: string;
  team: string[];
  created_at: string;
  last_modified: string;

  risk_assessment: DealRiskAssessment;
  stakeholders: DealStakeholder[];
  engagement_timeline: EngagementEvent[];
  competitor_intel: CompetitorIntel[];
  recovery_plays: RecoveryPlay[];
  stage_history: StageTransition[];
  notes: DealNote[];
}

export interface DealRiskAssessment {
  overall_score: number;
  level: "low" | "medium" | "high" | "critical";
  confidence: number;
  factors: Array<{
    factor_id: string;
    name: string;
    category: "engagement" | "stakeholder" | "competitive" | "timing" | "value" | "sentiment";
    severity: "low" | "medium" | "high" | "critical";
    score: number;
    weight: number;
    description: string;
    evidence: string[];
    trend: "improving" | "stable" | "deteriorating";
  }>;
  last_assessed: string;
}

export interface DealStakeholder {
  id: string;
  name: string;
  title: string;
  role: "champion" | "decision_maker" | "influencer" | "blocker" | "end_user";
  sentiment: "positive" | "neutral" | "negative" | "unknown";
  engagement_level: "high" | "medium" | "low" | "none";
  last_interaction: string | null;
  interaction_count: number;
  power_score: number;
  interest_score: number;
}

export interface EngagementEvent {
  id: string;
  timestamp: string;
  type: "email" | "call" | "meeting" | "demo" | "proposal" | "contract" | "note" | "signal";
  direction: "inbound" | "outbound";
  participants: string[];
  summary: string;
  sentiment: "positive" | "neutral" | "negative" | null;
  signals: string[];
}

export interface CompetitorIntel {
  id: string;
  competitor_name: string;
  mention_date: string;
  context: string;
  source: string;
  threat_level: "low" | "medium" | "high";
  battlecard_available: boolean;
}

export interface RecoveryPlay {
  id: string;
  title: string;
  description: string;
  priority: "high" | "medium" | "low";
  type: "outreach" | "escalation" | "content" | "meeting" | "pricing" | "stakeholder";
  estimated_impact: number;
  confidence: number;
  suggested_actions: Array<{
    action: string;
    owner: string;
    deadline: string;
    status: "pending" | "in_progress" | "completed" | "skipped";
  }>;
  generated_at: string;
  ai_reasoning: string;
}

export interface StageTransition {
  from_stage: DealStage | null;
  to_stage: DealStage;
  timestamp: string;
  days_in_previous: number | null;
  triggered_by: string;
}

export interface DealNote {
  id: string;
  author: string;
  content: string;
  created_at: string;
  tags: string[];
}

export interface DealFilterParams {
  search?: string;
  stage?: DealStage[];
  risk_level?: string[];
  owner?: string[];
  value_min?: number;
  value_max?: number;
  expected_close_before?: string;
  expected_close_after?: string;
  sort_by?: string;
  sort_order?: "asc" | "desc";
  page?: number;
  page_size?: number;
}
