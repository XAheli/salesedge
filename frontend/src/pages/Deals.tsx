import { useMemo } from "react";
import { Link } from "react-router-dom";
import {
  AlertTriangle,
  TrendingUp,
  TrendingDown,
  Clock,
  RefreshCw,
  Briefcase,
  ShieldAlert,
  Trophy,
} from "lucide-react";
import {
  useDealList,
  useDealRiskSummary,
  computeRiskLevel,
  type DealItem,
} from "@/api/hooks/useDeals";
import { formatINR } from "@/utils/indian-formatting";
import { formatRelativeTime } from "@/utils/date-helpers";
import { SkeletonCard } from "@/components/data-display/LoadingSkeleton";
import { ErrorBoundary } from "@/components/shared/ErrorBoundary";

function riskLevelColor(level: string): string {
  switch (level) {
    case "critical":
      return "text-red-800";
    case "high":
      return "text-risk";
    case "medium":
      return "text-caution";
    default:
      return "text-revenue-positive";
  }
}

function riskBorder(level: string): string {
  switch (level) {
    case "critical":
    case "high":
      return "border-l-risk";
    case "medium":
      return "border-l-caution";
    default:
      return "border-l-primary-300";
  }
}

function DealCard({ deal }: { deal: DealItem }) {
  const riskLevel = computeRiskLevel(deal.risk_score);
  const riskPct = Math.round(deal.risk_score);
  const border =
    deal.stage === "Won"
      ? "border-l-revenue-positive"
      : riskBorder(riskLevel);

  return (
    <Link
      to={`/deals/${deal.id}`}
      className={`card border-l-4 ${border} p-4 transition-shadow hover:shadow-md`}
    >
      <div className="flex items-start justify-between">
        <div className="min-w-0 flex-1">
          <p className="truncate text-sm font-semibold text-text-primary">
            {deal.prospect_name}
          </p>
          <p className="text-xs text-text-tertiary capitalize">{deal.stage}</p>
        </div>
        <span className="font-display text-lg font-bold text-text-primary">
          {formatINR(deal.value_inr, { compact: true })}
        </span>
      </div>

      <div className="mt-3 flex flex-wrap items-center gap-3 text-xs text-text-secondary">
        <span className="rounded bg-neutral-bg px-1.5 py-0.5 capitalize">
          {deal.stage}
        </span>
        {deal.stage !== "Won" && deal.stage !== "Lost" && (
          <>
            <span className="flex items-center gap-1">
              <Clock size={12} /> {deal.days_in_stage}d in stage
            </span>
            <span className={`font-medium ${riskLevelColor(riskLevel)}`}>
              Risk: {riskPct}%
            </span>
          </>
        )}
      </div>

      <div className="mt-2 flex items-center justify-between text-xs">
        <span className="text-text-tertiary">{deal.owner}</span>
        {deal.last_activity && (
          <span className="text-text-tertiary">
            {formatRelativeTime(deal.last_activity)}
          </span>
        )}
      </div>
    </Link>
  );
}

function SummaryKpi({
  label,
  value,
  icon,
  accent,
}: {
  label: string;
  value: string | number;
  icon: React.ReactNode;
  accent?: string;
}) {
  return (
    <div className={`card p-4 ${accent ?? ""}`}>
      <div className="flex items-center gap-2">
        {icon}
        <p className="text-xs font-semibold uppercase tracking-wider text-text-tertiary">
          {label}
        </p>
      </div>
      <p className="mt-1 font-display text-xl font-bold text-text-primary">
        {value}
      </p>
    </div>
  );
}

function DealsSkeleton() {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <SkeletonCard key={i} />
        ))}
      </div>
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {Array.from({ length: 6 }).map((_, i) => (
          <SkeletonCard key={i} />
        ))}
      </div>
    </div>
  );
}

export default function Deals() {
  const {
    data: dealData,
    isLoading: dealsLoading,
    error: dealsError,
    refetch: refetchDeals,
  } = useDealList({ page_size: 100 });
  const {
    data: riskData,
    isLoading: riskLoading,
    error: riskError,
  } = useDealRiskSummary();

  const isLoading = dealsLoading || riskLoading;
  const error = dealsError || riskError;

  const deals = dealData?.items ?? [];
  const riskSummary = riskData?.data;

  const { atRisk, healthy, won, lost } = useMemo(() => {
    const atRisk: DealItem[] = [];
    const healthy: DealItem[] = [];
    const won: DealItem[] = [];
    const lost: DealItem[] = [];

    for (const d of deals) {
      if (d.stage === "Won") {
        won.push(d);
      } else if (d.stage === "Lost") {
        lost.push(d);
      } else {
        const level = computeRiskLevel(d.risk_score);
        if (level === "high" || level === "critical") {
          atRisk.push(d);
        } else {
          healthy.push(d);
        }
      }
    }
    return { atRisk, healthy, won, lost };
  }, [deals]);

  const totalPipeline = useMemo(
    () =>
      deals
        .filter((d) => d.stage !== "Won" && d.stage !== "Lost")
        .reduce((sum, d) => sum + d.value_inr, 0),
    [deals],
  );

  if (isLoading) return <DealsSkeleton />;

  if (error) {
    return (
      <div className="flex min-h-[400px] flex-col items-center justify-center rounded-lg bg-surface-card p-8 text-center shadow-card">
        <AlertTriangle className="h-8 w-8 text-risk" />
        <h2 className="mt-4 font-display text-lg font-semibold text-text-primary">
          Failed to load deals
        </h2>
        <p className="mt-2 text-sm text-text-secondary">
          {(error as Error).message}
        </p>
        <button
          onClick={() => refetchDeals()}
          className="mt-4 inline-flex items-center gap-2 rounded-lg bg-primary-500 px-4 py-2 text-sm font-semibold text-white hover:bg-primary-600"
        >
          <RefreshCw size={16} /> Retry
        </button>
      </div>
    );
  }

  const riskDist = riskSummary?.risk_distribution ?? {};
  const activeCount =
    riskSummary?.total_active ??
    deals.filter((d) => d.stage !== "Won" && d.stage !== "Lost").length;

  return (
    <ErrorBoundary>
      <div className="space-y-6">
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
          <SummaryKpi
            label="Total Pipeline"
            value={formatINR(totalPipeline, { compact: true })}
            icon={<Briefcase size={14} className="text-primary-500" />}
          />
          <SummaryKpi
            label="Active Deals"
            value={activeCount}
            icon={<TrendingUp size={14} className="text-primary-500" />}
          />
          <SummaryKpi
            label="At Risk"
            value={
              (riskDist.high ?? 0) + (riskDist.critical ?? 0) || atRisk.length
            }
            icon={<ShieldAlert size={14} className="text-risk" />}
            accent="border-l-4 border-l-risk"
          />
          <SummaryKpi
            label="Won This Period"
            value={won.length}
            icon={<Trophy size={14} className="text-revenue-positive" />}
            accent="border-l-4 border-l-revenue-positive"
          />
        </div>

        {atRisk.length > 0 && (
          <section>
            <h3 className="mb-3 flex items-center gap-2 text-sm font-semibold text-risk">
              <AlertTriangle size={16} /> Deals at Risk ({atRisk.length})
            </h3>
            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
              {atRisk.map((d) => (
                <DealCard key={d.id} deal={d} />
              ))}
            </div>
          </section>
        )}

        {healthy.length > 0 && (
          <section>
            <h3 className="mb-3 flex items-center gap-2 text-sm font-semibold text-text-secondary">
              <TrendingUp size={16} /> Healthy Pipeline ({healthy.length})
            </h3>
            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
              {healthy.map((d) => (
                <DealCard key={d.id} deal={d} />
              ))}
            </div>
          </section>
        )}

        {won.length > 0 && (
          <section>
            <h3 className="mb-3 flex items-center gap-2 text-sm font-semibold text-revenue-positive">
              <Trophy size={16} /> Won ({won.length})
            </h3>
            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
              {won.map((d) => (
                <DealCard key={d.id} deal={d} />
              ))}
            </div>
          </section>
        )}

        {lost.length > 0 && (
          <section>
            <h3 className="mb-3 flex items-center gap-2 text-sm font-semibold text-text-tertiary">
              <TrendingDown size={16} /> Lost ({lost.length})
            </h3>
            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
              {lost.map((d) => (
                <DealCard key={d.id} deal={d} />
              ))}
            </div>
          </section>
        )}

        {deals.length === 0 && (
          <div className="flex min-h-[200px] items-center justify-center rounded-lg bg-surface-card p-8 shadow-card">
            <p className="text-sm text-text-tertiary">No deals found</p>
          </div>
        )}
      </div>
    </ErrorBoundary>
  );
}
