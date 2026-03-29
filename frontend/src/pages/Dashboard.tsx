import { useMemo } from "react";
import { Link } from "react-router-dom";
import {
  TrendingUp,
  TrendingDown,
  Minus,
  AlertTriangle,
  RefreshCw,
} from "lucide-react";
import { AreaChart, Area, ResponsiveContainer } from "recharts";
import { useExecutiveSummary } from "@/api/hooks/useDashboard";
import { formatINR } from "@/utils/indian-formatting";
import { classifyRisk, RISK_BANDS } from "@/utils/risk-bands";
import { ConfidenceBadge } from "@/components/data-display/ConfidenceBadge";
import { SkeletonCard, SkeletonTable, SkeletonChart } from "@/components/data-display/LoadingSkeleton";
import { ErrorBoundary } from "@/components/shared/ErrorBoundary";
import { RevenueForecast } from "@/components/charts/RevenueForecast";
import { FunnelWaterfall } from "@/components/charts/FunnelWaterfall";
import { DealRiskScatter } from "@/components/charts/DealRiskScatter";
import { PipelineVelocity } from "@/components/charts/PipelineVelocity";
import type { KPIMetric } from "@/types/api";

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

const RISK_LEVEL_SCORE: Record<string, number> = {
  low: 20,
  medium: 45,
  high: 70,
  critical: 90,
};

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
          const riskColor = RISK_BANDS[classifyRisk(risk)].color;
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
                {risk.toFixed(0)}%
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
  const summary = data?.data;
  const kpis = summary?.kpis;
  const funnel = summary?.funnel;
  const topDeals = summary?.top_deals;
  const revenueForecast = summary?.revenue_forecast;
  const pipelineVelocity = summary?.pipeline_velocity;
  const atRiskDeals = (summary as Record<string, unknown> | undefined)?.at_risk_deals as TopDeal[] | undefined;

  const funnelChartStages = useMemo(
    () => {
      const stages = Array.isArray(funnel?.stages) ? funnel.stages : [];
      return stages.map((s, index) => {
        const stage = s as Record<string, unknown>;
        return {
          name: String(stage.name ?? stage.stage_name ?? `Stage ${index + 1}`),
          count: Number(stage.count ?? 0),
          conversionRate: Number(stage.conversion_rate ?? stage.conversionRate ?? 0),
        };
      });
    },
    [funnel],
  );

  const velocityData = useMemo(
    () => {
      const source = Array.isArray(pipelineVelocity)
        ? pipelineVelocity
        : Array.isArray((pipelineVelocity as { data?: unknown[] } | undefined)?.data)
          ? (pipelineVelocity as { data: unknown[] }).data
          : [];

      return source.map((row, index) => {
        const point = row as Record<string, unknown>;
        const avgDays = Number(point.avg_days_in_stage ?? 0);
        return {
          week: String(point.week ?? point.stage ?? `Point ${index + 1}`),
          avgDaysInStage: avgDays,
          throughput: Number(point.throughput ?? point.deal_count ?? 0),
          rollingMeanDays: Number(point.rolling_mean_days ?? avgDays),
          upperControlLimit: Number(point.upper_control_limit ?? avgDays),
          lowerControlLimit: Number(point.lower_control_limit ?? avgDays),
        };
      });
    },
    [pipelineVelocity],
  );

  const revenueForecastSeries = useMemo(() => {
    if (!revenueForecast) {
      return { historical: [], forecast: [] };
    }

    if (Array.isArray(revenueForecast)) {
      const forecast = revenueForecast.map((row, index) => {
        const point = row as Record<string, unknown>;
        const p50 = Number(point.forecast_value ?? point.p50 ?? 0);
        return {
          date: String(point.period ?? point.date ?? `T+${index + 1}`),
          p10: Number(point.lower_bound ?? point.p10 ?? p50),
          p50,
          p90: Number(point.upper_bound ?? point.p90 ?? p50),
        };
      });
      return { historical: [], forecast };
    }

    const payload = revenueForecast as Record<string, unknown>;
    const historical = Array.isArray(payload.historical)
      ? payload.historical.map((row, index) => {
          const point = row as Record<string, unknown>;
          return {
            date: String(point.date ?? `H${index + 1}`),
            revenue: Number(point.revenue ?? 0),
          };
        })
      : [];

    const forecast = Array.isArray(payload.forecast)
      ? payload.forecast.map((row, index) => {
          const point = row as Record<string, unknown>;
          const p50 = Number(point.p50 ?? point.forecast_value ?? 0);
          return {
            date: String(point.date ?? point.period ?? `F${index + 1}`),
            p10: Number(point.p10 ?? point.lower_bound ?? p50),
            p50,
            p90: Number(point.p90 ?? point.upper_bound ?? p50),
          };
        })
      : [];

    return { historical, forecast };
  }, [revenueForecast]);

  const dealBubbles = useMemo(
    () =>
      (topDeals ?? []).map((d, i) => ({
        id: d.id ?? String(i),
        name: d.prospect_name ?? d.name ?? d.account ?? "Unknown",
        value: d.value_inr ?? d.value ?? 0,
        riskScore: d.risk_score ?? RISK_LEVEL_SCORE[d.risk_level ?? "medium"] ?? 50,
        daysInStage: d.days_in_stage,
        stage: d.stage,
      })),
    [topDeals],
  );

  if (isLoading) return <DashboardSkeleton />;
  if (error) return <DashboardError error={error as Error} refetch={refetch} />;
  if (!summary || !kpis) {
    return (
      <DashboardError
        error={new Error("No dashboard data returned from API")}
        refetch={refetch}
      />
    );
  }

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
              Revenue Forecast
            </h3>
            {revenueForecastSeries.historical.length > 0 || revenueForecastSeries.forecast.length > 0 ? (
              <RevenueForecast
                historical={revenueForecastSeries.historical}
                forecast={revenueForecastSeries.forecast}
              />
            ) : (
              <p className="text-sm text-text-tertiary">No revenue data available</p>
            )}
          </div>

          <div className="card p-6">
            <h3 className="mb-4 text-sm font-semibold uppercase tracking-wider text-text-secondary">
              Pipeline Funnel
            </h3>
            {funnelChartStages.length ? (
              <FunnelWaterfall stages={funnelChartStages} />
            ) : (
              <p className="text-sm text-text-tertiary">No funnel data available</p>
            )}
          </div>
        </div>

        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          <div className="card p-6">
            <h3 className="mb-4 text-sm font-semibold uppercase tracking-wider text-text-secondary">
              Pipeline Velocity
            </h3>
            {velocityData.length ? (
              <PipelineVelocity data={velocityData} />
            ) : (
              <p className="text-sm text-text-tertiary">No velocity data available</p>
            )}
          </div>

          <div className="card p-6">
            <h3 className="mb-4 text-sm font-semibold uppercase tracking-wider text-text-secondary">
              Deal Risk Map
            </h3>
            {dealBubbles.length ? (
              <DealRiskScatter deals={dealBubbles} />
            ) : (
              <p className="text-sm text-text-tertiary">No deal risk data available</p>
            )}
          </div>
        </div>

        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          <div className="card p-6">
            <TopDealsTable
              deals={(topDeals as unknown as TopDeal[]) ?? []}
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
