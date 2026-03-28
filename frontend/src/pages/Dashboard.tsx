import { useMemo } from "react";
import { Link } from "react-router-dom";
import {
  TrendingUp,
  TrendingDown,
  Minus,
  AlertTriangle,
  RefreshCw,
} from "lucide-react";
import {
  AreaChart,
  Area,
  ResponsiveContainer,
  XAxis,
  YAxis,
  Tooltip,
} from "recharts";
import { useExecutiveSummary } from "@/api/hooks/useDashboard";
import { formatINR } from "@/utils/indian-formatting";
import { ConfidenceBadge } from "@/components/data-display/ConfidenceBadge";
import { SkeletonCard, SkeletonTable, SkeletonChart } from "@/components/data-display/LoadingSkeleton";
import { ErrorBoundary } from "@/components/shared/ErrorBoundary";
import type { KPIMetric, ExecutiveSummary } from "@/types/api";

function TrendIcon({ direction }: { direction: string }) {
  if (direction === "up") return <TrendingUp size={14} />;
  if (direction === "down") return <TrendingDown size={14} />;
  return <Minus size={14} />;
}

function KpiCard({ label, metric }: { label: string; metric: KPIMetric }) {
  const sparkData = useMemo(
    () => (metric.sparkline ?? []).map((v, i) => ({ i, v })),
    [metric.sparkline],
  );
  const sparkColor = metric.is_positive ? "#059669" : "#DC2626";

  return (
    <div className="relative rounded-md bg-surface-card shadow-card p-4">
      <div className="flex items-start justify-between gap-2">
        <p className="text-xs font-medium uppercase tracking-wider text-text-secondary">
          {label}
        </p>
        {metric.confidence != null && (
          <ConfidenceBadge confidence={metric.confidence} size="sm" />
        )}
      </div>

      <div className="mt-2 flex items-end justify-between gap-3">
        <div className="min-w-0 flex-1">
          <p className="font-display text-[28px] font-bold leading-tight text-text-primary">
            {metric.formatted}
          </p>
          <div
            className={`mt-1.5 inline-flex items-center gap-1 text-xs font-medium ${
              metric.is_positive ? "text-revenue-positive" : "text-risk"
            }`}
          >
            <TrendIcon direction={metric.trend_direction} />
            <span>
              {metric.trend_pct > 0 ? "+" : ""}
              {metric.trend_pct.toFixed(1)}%
            </span>
            <span className="text-text-tertiary">vs last period</span>
          </div>
        </div>

        {sparkData.length > 1 && (
          <div className="h-8 w-20">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={sparkData} margin={{ top: 0, right: 0, bottom: 0, left: 0 }}>
                <defs>
                  <linearGradient id={`spark-${label}`} x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor={sparkColor} stopOpacity={0.3} />
                    <stop offset="100%" stopColor={sparkColor} stopOpacity={0} />
                  </linearGradient>
                </defs>
                <Area
                  type="monotone"
                  dataKey="v"
                  stroke={sparkColor}
                  strokeWidth={1.5}
                  fill={`url(#spark-${label})`}
                  dot={false}
                  isAnimationActive={false}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>

      <div className="mt-3 flex items-center justify-between border-t border-neutral-bg pt-2">
        <span className="text-[10px] text-text-tertiary">
          {metric.source}
        </span>
      </div>
    </div>
  );
}

function RevenueSparkline({ kpis }: { kpis: ExecutiveSummary["kpis"] }) {
  const chartData = useMemo(() => {
    const arr = kpis.arr.sparkline ?? [];
    return arr.map((v, i) => ({ idx: i, value: v }));
  }, [kpis.arr.sparkline]);

  if (chartData.length < 2) {
    return (
      <p className="text-sm text-text-tertiary">
        Not enough data for revenue sparkline
      </p>
    );
  }

  return (
    <ResponsiveContainer width="100%" height="100%">
      <AreaChart data={chartData} margin={{ top: 8, right: 8, bottom: 0, left: 0 }}>
        <defs>
          <linearGradient id="revGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#3B82F6" stopOpacity={0.25} />
            <stop offset="100%" stopColor="#3B82F6" stopOpacity={0} />
          </linearGradient>
        </defs>
        <XAxis dataKey="idx" hide />
        <YAxis hide domain={["dataMin", "dataMax"]} />
        <Tooltip
          formatter={(v: number) => [formatINR(v, { compact: true }), "Revenue"]}
          contentStyle={{
            background: "var(--color-surface-card, #fff)",
            border: "1px solid var(--color-neutral-bg, #e5e7eb)",
            borderRadius: 8,
            fontSize: 12,
          }}
        />
        <Area
          type="monotone"
          dataKey="value"
          stroke="#3B82F6"
          strokeWidth={2}
          fill="url(#revGrad)"
          dot={false}
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}

interface FunnelStage {
  name?: string;
  stage_name?: string;
  count: number;
  value_inr?: number;
  conversion_rate: number;
}

function PipelineFunnel({ stages, overallConversion }: { stages: FunnelStage[]; overallConversion?: number }) {
  const maxCount = Math.max(...stages.map((s) => s.count), 1);
  const colors = [
    "bg-primary-200",
    "bg-primary-300",
    "bg-primary-400",
    "bg-primary-500",
    "bg-primary-600",
    "bg-primary-700",
  ];

  return (
    <div className="space-y-3">
      {stages.map((s, i) => {
        const label = s.stage_name ?? s.name ?? `Stage ${i + 1}`;
        return (
          <div key={label}>
            <div className="mb-1 flex justify-between text-xs">
              <span className="text-text-secondary">{label}</span>
              <span className="font-medium text-text-primary">
                {s.count} · {(s.conversion_rate * 100).toFixed(0)}%
                {s.value_inr != null && (
                  <span className="ml-2 text-text-tertiary">
                    {formatINR(s.value_inr, { compact: true })}
                  </span>
                )}
              </span>
            </div>
            <div className="h-3 overflow-hidden rounded-full bg-neutral-bg">
              <div
                className={`h-full rounded-full ${colors[i % colors.length]} transition-all`}
                style={{ width: `${(s.count / maxCount) * 100}%` }}
              />
            </div>
          </div>
        );
      })}
      {overallConversion != null && (
        <p className="text-xs text-text-tertiary">
          Overall conversion: {(overallConversion * 100).toFixed(1)}%
        </p>
      )}
    </div>
  );
}

interface HeatmapCell {
  segment: string;
  risk_level: string;
  deal_count: number;
  total_value_inr: number;
}

function RiskHeatmap({ cells }: { cells: HeatmapCell[] }) {
  if (!cells?.length) {
    return <p className="text-sm text-text-tertiary">No risk data available</p>;
  }

  const riskColors: Record<string, string> = {
    low: "bg-revenue-positive/20 text-revenue-positive",
    medium: "bg-caution/20 text-caution",
    high: "bg-risk/20 text-risk",
    critical: "bg-red-800/20 text-red-800",
  };

  return (
    <div className="space-y-2">
      {cells.map((cell, i) => (
        <div
          key={`${cell.segment}-${cell.risk_level}-${i}`}
          className={`flex items-center justify-between rounded-lg px-3 py-2 ${
            riskColors[cell.risk_level] ?? "bg-neutral-bg text-text-secondary"
          }`}
        >
          <div>
            <p className="text-sm font-medium">{cell.segment}</p>
            <p className="text-xs opacity-75 capitalize">{cell.risk_level} risk</p>
          </div>
          <div className="text-right">
            <p className="text-sm font-semibold">{cell.deal_count} deals</p>
            <p className="text-xs">{formatINR(cell.total_value_inr, { compact: true })}</p>
          </div>
        </div>
      ))}
    </div>
  );
}

interface TopDeal {
  id?: string;
  prospect_name?: string;
  name?: string;
  account?: string;
  stage: string;
  value_inr?: number;
  value?: number;
  risk_score?: number;
  risk_level?: string;
  days_in_stage: number;
  owner: string;
}

function TopDealsTable({ deals, title }: { deals: TopDeal[]; title: string }) {
  if (!deals?.length) {
    return <p className="text-sm text-text-tertiary">No deals to display</p>;
  }

  return (
    <div>
      <h3 className="mb-3 text-sm font-semibold uppercase tracking-wider text-text-secondary">
        {title}
      </h3>
      <div className="space-y-1.5">
        {deals.map((d, i) => {
          const displayName = d.prospect_name ?? d.name ?? d.account ?? "Unknown";
          const val = d.value_inr ?? d.value ?? 0;
          const risk = d.risk_score ?? 0;
          const riskColor =
            risk > 0.6
              ? "text-risk"
              : risk > 0.3
                ? "text-caution"
                : "text-revenue-positive";
          return (
            <Link
              key={d.id ?? i}
              to={d.id ? `/deals/${d.id}` : "#"}
              className="flex items-center gap-3 rounded-lg p-2 hover:bg-neutral-bg transition-colors"
            >
              <div className="min-w-0 flex-1">
                <p className="truncate text-sm font-medium text-text-primary">
                  {displayName}
                </p>
                <p className="text-xs text-text-tertiary">
                  {d.stage} · {d.days_in_stage}d · {d.owner}
                </p>
              </div>
              <span className="text-sm font-semibold text-text-primary">
                {formatINR(val, { compact: true })}
              </span>
              <span className={`text-xs font-medium ${riskColor}`}>
                {(risk * 100).toFixed(0)}%
              </span>
            </Link>
          );
        })}
      </div>
    </div>
  );
}

function DashboardError({ error, refetch }: { error: Error; refetch: () => void }) {
  return (
    <div className="flex min-h-[400px] flex-col items-center justify-center rounded-lg bg-surface-card p-8 text-center shadow-card">
      <div className="flex h-16 w-16 items-center justify-center rounded-full bg-risk-bg">
        <AlertTriangle className="h-8 w-8 text-risk" />
      </div>
      <h2 className="mt-6 font-display text-xl font-semibold text-text-primary">
        Failed to load dashboard
      </h2>
      <p className="mt-2 max-w-md text-sm text-text-secondary">
        {error.message}
      </p>
      <button
        onClick={refetch}
        className="mt-6 inline-flex items-center gap-2 rounded-lg bg-primary-500 px-5 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-primary-600"
      >
        <RefreshCw size={16} />
        Retry
      </button>
    </div>
  );
}

function DashboardSkeleton() {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3">
        {Array.from({ length: 6 }).map((_, i) => (
          <SkeletonCard key={i} />
        ))}
      </div>
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <SkeletonChart />
        <SkeletonChart />
      </div>
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <SkeletonChart />
        <SkeletonChart />
        <SkeletonTable rows={5} cols={4} />
      </div>
    </div>
  );
}

export default function Dashboard() {
  const { data, isLoading, error, refetch } = useExecutiveSummary({});

  if (isLoading) return <DashboardSkeleton />;
  if (error) return <DashboardError error={error as Error} refetch={refetch} />;

  const summary = data?.data;
  if (!summary) {
    return (
      <DashboardError
        error={new Error("No dashboard data returned from API")}
        refetch={refetch}
      />
    );
  }

  const { kpis, funnel, risk_heatmap, top_deals } = summary;
  const atRiskDeals = (summary as Record<string, unknown>).at_risk_deals as TopDeal[] | undefined;

  const funnelStages = (funnel as Record<string, unknown>)?.stages as FunnelStage[] | undefined;
  const overallConversion = (funnel as Record<string, unknown>)?.overall_conversion as number | undefined;
  const heatmapCells = (risk_heatmap as Record<string, unknown>)?.cells as HeatmapCell[] | undefined;

  return (
    <ErrorBoundary>
      <div className="space-y-6">
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3">
          <KpiCard label="ARR" metric={kpis.arr} />
          <KpiCard label="MRR" metric={kpis.mrr} />
          <KpiCard label="Pipeline Value" metric={kpis.pipeline_value} />
          <KpiCard label="Win Rate" metric={kpis.win_rate} />
          <KpiCard label="Avg Deal Cycle" metric={kpis.avg_deal_cycle} />
          <KpiCard label="Net Revenue Retention" metric={kpis.net_revenue_retention} />
        </div>

        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          <div className="card p-6">
            <h3 className="mb-4 text-sm font-semibold uppercase tracking-wider text-text-secondary">
              Revenue Trend
            </h3>
            <div className="h-64">
              <RevenueSparkline kpis={kpis} />
            </div>
          </div>

          <div className="card p-6">
            <h3 className="mb-4 text-sm font-semibold uppercase tracking-wider text-text-secondary">
              Pipeline Funnel
            </h3>
            {funnelStages?.length ? (
              <PipelineFunnel
                stages={funnelStages}
                overallConversion={overallConversion}
              />
            ) : (
              <p className="text-sm text-text-tertiary">No funnel data available</p>
            )}
          </div>
        </div>

        <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
          <div className="card p-6">
            <h3 className="mb-4 text-sm font-semibold uppercase tracking-wider text-text-secondary">
              Risk Heatmap
            </h3>
            <RiskHeatmap cells={heatmapCells ?? []} />
          </div>

          <div className="card p-6">
            <TopDealsTable
              deals={(top_deals as unknown as TopDeal[]) ?? []}
              title="Top Deals"
            />
          </div>

          <div className="card p-6">
            <TopDealsTable
              deals={atRiskDeals ?? []}
              title="At-Risk Deals"
            />
          </div>
        </div>
      </div>
    </ErrorBoundary>
  );
}
