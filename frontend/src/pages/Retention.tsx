import {
  AlertTriangle,
  RefreshCw,
  ShieldAlert,
  Users,
  TrendingDown,
  DollarSign,
} from "lucide-react";
import { useRetentionOverview } from "@/api/hooks/useRetention";
import { formatINR } from "@/utils/indian-formatting";
import { SkeletonCard, SkeletonTable } from "@/components/data-display/LoadingSkeleton";
import { ErrorBoundary } from "@/components/shared/ErrorBoundary";
import type { RetentionOverviewData } from "@/api/hooks/useRetention";

const RISK_CONFIG: Record<string, { label: string; color: string; bg: string }> = {
  low: { label: "Low", color: "bg-revenue-positive", bg: "text-revenue-positive" },
  medium: { label: "Medium", color: "bg-caution", bg: "text-caution" },
  high: { label: "High", color: "bg-risk", bg: "text-risk" },
  critical: { label: "Critical", color: "bg-red-800", bg: "text-red-800" },
};

function RetentionSkeleton() {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <SkeletonCard key={i} />
        ))}
      </div>
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <SkeletonCard />
        <SkeletonCard />
      </div>
      <SkeletonTable rows={5} cols={5} />
    </div>
  );
}

function RiskDistributionBars({ dist }: { dist: Record<string, number> }) {
  const total = Object.values(dist).reduce((s, v) => s + v, 0) || 1;
  const entries = Object.entries(dist).sort((a, b) => {
    const order = ["low", "medium", "high", "critical"];
    return order.indexOf(a[0]) - order.indexOf(b[0]);
  });

  return (
    <div className="space-y-4">
      <div className="flex h-5 overflow-hidden rounded-full">
        {entries.map(([level, count]) => (
          <div
            key={level}
            className={RISK_CONFIG[level]?.color ?? "bg-neutral-bg"}
            style={{ width: `${(count / total) * 100}%` }}
          />
        ))}
      </div>
      <div className="grid grid-cols-2 gap-2">
        {entries.map(([level, count]) => {
          const cfg = RISK_CONFIG[level];
          return (
            <div key={level} className="flex items-center gap-2">
              <div className={`h-3 w-3 rounded-full ${cfg?.color ?? "bg-neutral-bg"}`} />
              <span className="text-xs text-text-secondary">{cfg?.label ?? level}</span>
              <span className="ml-auto text-xs font-medium text-text-primary">
                {count}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function LossReasons({ reasons }: { reasons: Record<string, number> }) {
  const entries = Object.entries(reasons).sort((a, b) => b[1] - a[1]);
  const max = Math.max(...entries.map(([, v]) => v), 1);

  if (entries.length === 0) {
    return <p className="text-sm text-text-tertiary">No loss reasons recorded</p>;
  }

  return (
    <div className="space-y-3">
      {entries.map(([reason, count]) => (
        <div key={reason}>
          <div className="mb-1 flex justify-between text-xs">
            <span className="capitalize text-text-secondary">{reason.replace(/_/g, " ")}</span>
            <span className="font-medium text-text-primary">{count}</span>
          </div>
          <div className="h-2.5 overflow-hidden rounded-full bg-neutral-bg">
            <div
              className="h-full rounded-full bg-gradient-to-r from-risk/60 to-risk"
              style={{ width: `${(count / max) * 100}%` }}
            />
          </div>
        </div>
      ))}
    </div>
  );
}

function AtRiskTable({ deals }: { deals: RetentionOverviewData["at_risk_deals"] }) {
  if (!deals?.length) {
    return (
      <div className="flex min-h-[120px] items-center justify-center">
        <p className="text-sm text-text-tertiary">No at-risk customers</p>
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-left text-sm">
        <thead>
          <tr className="border-b border-neutral-bg bg-neutral-bg/50">
            <th className="px-4 py-3 font-medium text-text-secondary">Account</th>
            <th className="px-4 py-3 font-medium text-text-secondary text-right">Value</th>
            <th className="px-4 py-3 font-medium text-text-secondary text-center">Risk</th>
            <th className="px-4 py-3 font-medium text-text-secondary text-center">Churn Prob</th>
            <th className="px-4 py-3 font-medium text-text-secondary">Drivers</th>
          </tr>
        </thead>
        <tbody>
          {deals.map((d) => {
            const riskPct = Math.round(d.risk_score ?? 0);
            const churnPct = Math.round((d.churn_probability ?? 0) * 100);
            const riskBand = d.risk_band ?? "medium";
            const cfg = RISK_CONFIG[riskBand] ?? RISK_CONFIG.medium;
            return (
              <tr
                key={d.id}
                className="border-b border-neutral-bg/50 transition-colors hover:bg-neutral-bg/30"
              >
                <td className="px-4 py-3">
                  <p className="font-medium text-text-primary">{d.account_name}</p>
                  {d.days_since_last_activity != null && (
                    <p className="text-xs text-text-tertiary">
                      {d.days_since_last_activity}d since last activity
                    </p>
                  )}
                </td>
                <td className="px-4 py-3 text-right font-medium text-text-primary">
                  {formatINR(d.value_inr, { compact: true })}
                </td>
                <td className="px-4 py-3 text-center">
                  <span
                    className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-semibold text-white ${cfg?.color}`}
                  >
                    {riskPct}%
                  </span>
                </td>
                <td className="px-4 py-3 text-center text-xs font-medium text-risk">
                  {churnPct}%
                </td>
                <td className="px-4 py-3">
                  <div className="flex flex-wrap gap-1">
                    {(d.drivers ?? []).slice(0, 3).map((driver) => (
                      <span
                        key={driver}
                        className="rounded bg-neutral-bg px-1.5 py-0.5 text-[10px] text-text-secondary"
                      >
                        {driver}
                      </span>
                    ))}
                  </div>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

export default function Retention() {
  const { data, isLoading, error, refetch } = useRetentionOverview();

  if (isLoading) return <RetentionSkeleton />;

  if (error) {
    return (
      <div className="flex min-h-[400px] flex-col items-center justify-center rounded-lg bg-surface-card p-8 text-center shadow-card">
        <AlertTriangle className="h-8 w-8 text-risk" />
        <h2 className="mt-4 font-display text-lg font-semibold text-text-primary">
          Failed to load retention data
        </h2>
        <p className="mt-2 text-sm text-text-secondary">{(error as Error).message}</p>
        <button
          onClick={() => refetch()}
          className="mt-4 inline-flex items-center gap-2 rounded-lg bg-primary-500 px-4 py-2 text-sm font-semibold text-white hover:bg-primary-600"
        >
          <RefreshCw size={16} /> Retry
        </button>
      </div>
    );
  }

  const overview = data?.data;

  if (!overview) {
    return (
      <div className="flex min-h-[300px] items-center justify-center rounded-lg bg-surface-card p-8 shadow-card">
        <p className="text-sm text-text-tertiary">No retention data available</p>
      </div>
    );
  }

  const retentionColor =
    overview.retention_rate >= 80
      ? "text-revenue-positive"
      : overview.retention_rate >= 60
        ? "text-caution"
        : "text-risk";

  return (
    <ErrorBoundary>
      <div className="space-y-6">
        <div>
          <h2 className="text-xl font-semibold text-text-primary">
            Retention &amp; Churn
          </h2>
          <p className="mt-1 text-sm text-text-secondary">
            Predict and prevent customer churn with data-driven retention analysis.
          </p>
        </div>

        <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
          <div className="card p-4">
            <div className="flex items-center gap-2">
              <Users size={14} className="text-primary-500" />
              <p className="text-xs font-semibold uppercase tracking-wider text-text-tertiary">
                Total Customers
              </p>
            </div>
            <p className="mt-1 font-display text-2xl font-bold text-text-primary">
              {overview.total_customers}
            </p>
          </div>

          <div className="card p-4">
            <div className="flex items-center gap-2">
              <TrendingDown size={14} className={retentionColor} />
              <p className="text-xs font-semibold uppercase tracking-wider text-text-tertiary">
                Retention Rate
              </p>
            </div>
            <p className={`mt-1 font-display text-2xl font-bold ${retentionColor}`}>
              {overview.retention_rate.toFixed(1)}%
            </p>
          </div>

          <div className="card border-l-4 border-l-risk p-4">
            <div className="flex items-center gap-2">
              <ShieldAlert size={14} className="text-risk" />
              <p className="text-xs font-semibold uppercase tracking-wider text-risk">
                At Risk
              </p>
            </div>
            <p className="mt-1 font-display text-2xl font-bold text-risk">
              {overview.at_risk_count}
            </p>
          </div>

          <div className="card p-4">
            <div className="flex items-center gap-2">
              <DollarSign size={14} className="text-risk" />
              <p className="text-xs font-semibold uppercase tracking-wider text-text-tertiary">
                Value at Risk
              </p>
            </div>
            <p className="mt-1 font-display text-2xl font-bold text-text-primary">
              {formatINR(overview.total_value_at_risk, { compact: true })}
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          <div className="card p-6">
            <h3 className="mb-4 text-sm font-semibold uppercase tracking-wider text-text-secondary">
              Risk Distribution
            </h3>
            <RiskDistributionBars dist={overview.risk_distribution} />
          </div>

          <div className="card p-6">
            <h3 className="mb-4 text-sm font-semibold uppercase tracking-wider text-text-secondary">
              Loss Reasons
            </h3>
            <LossReasons reasons={overview.loss_reasons} />
          </div>
        </div>

        <div className="card overflow-hidden">
          <div className="border-b border-neutral-bg px-4 py-3">
            <h3 className="text-sm font-semibold uppercase tracking-wider text-text-secondary">
              At-Risk Customers
            </h3>
          </div>
          <AtRiskTable deals={overview.at_risk_deals} />
        </div>
      </div>
    </ErrorBoundary>
  );
}
