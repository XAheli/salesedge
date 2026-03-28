import {
  AlertTriangle,
  RefreshCw,
  Zap,
  Shield,
  BarChart3,
  Radio,
  ExternalLink,
  ArrowUpRight,
  ArrowDownRight,
  Minus,
} from "lucide-react";
import { useIntelligenceOverview } from "@/api/hooks/useCompetitive";
import { formatIST } from "@/utils/indian-formatting";
import { formatRelativeTime } from "@/utils/date-helpers";
import { SkeletonCard, SkeletonTable } from "@/components/data-display/LoadingSkeleton";
import { ErrorBoundary } from "@/components/shared/ErrorBoundary";
import type { IntelligenceOverviewData } from "@/api/hooks/useCompetitive";

function impactColor(score: number): string {
  if (score >= 0.7) return "text-risk";
  if (score >= 0.4) return "text-caution";
  return "text-revenue-positive";
}

function impactBadge(impact: string): string {
  switch (impact) {
    case "high":
      return "bg-risk/10 text-risk";
    case "medium":
      return "bg-caution/10 text-caution";
    default:
      return "bg-revenue-positive/10 text-revenue-positive";
  }
}

function CompetitiveSkeleton() {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <SkeletonCard key={i} />
        ))}
      </div>
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <SkeletonTable rows={5} cols={3} />
        <SkeletonTable rows={5} cols={3} />
      </div>
      <SkeletonTable rows={5} cols={4} />
    </div>
  );
}

function SignalTypeCards({ types, total }: { types: Record<string, number>; total: number }) {
  const icons: Record<string, React.ReactNode> = {
    policy: <Shield size={16} className="text-primary-500" />,
    competitor: <Zap size={16} className="text-caution" />,
    market: <BarChart3 size={16} className="text-revenue-positive" />,
  };

  return (
    <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
      <div className="card p-4">
        <div className="flex items-center gap-2">
          <Radio size={14} className="text-primary-500" />
          <p className="text-xs font-semibold uppercase tracking-wider text-text-tertiary">
            Total Signals
          </p>
        </div>
        <p className="mt-1 font-display text-2xl font-bold text-text-primary">{total}</p>
      </div>
      {Object.entries(types).map(([type, count]) => (
        <div key={type} className="card p-4">
          <div className="flex items-center gap-2">
            {icons[type] ?? <Zap size={14} className="text-text-tertiary" />}
            <p className="text-xs font-semibold uppercase tracking-wider text-text-tertiary capitalize">
              {type}
            </p>
          </div>
          <p className="mt-1 font-display text-2xl font-bold text-text-primary">{count}</p>
        </div>
      ))}
    </div>
  );
}

function PolicyTimeline({ signals }: { signals: IntelligenceOverviewData["policy_signals"] }) {
  if (!signals?.length) {
    return <p className="py-8 text-center text-sm text-text-tertiary">No policy signals</p>;
  }

  return (
    <div className="space-y-3">
      {signals.map((s) => (
        <div
          key={s.id}
          className="rounded-lg border border-neutral-bg p-3 transition-colors hover:bg-neutral-bg/30"
        >
          <div className="flex items-start justify-between gap-2">
            <div className="min-w-0 flex-1">
              <p className="text-sm font-medium text-text-primary">{s.title}</p>
              <p className="mt-0.5 text-xs text-text-tertiary">
                {s.category} · {s.source}
              </p>
            </div>
            <span
              className={`inline-flex rounded-full px-2 py-0.5 text-[10px] font-semibold ${impactBadge(s.impact)}`}
            >
              {s.impact}
            </span>
          </div>
          {s.summary && (
            <p className="mt-2 text-xs text-text-secondary line-clamp-2">{s.summary}</p>
          )}
          <div className="mt-2 flex items-center justify-between text-[10px] text-text-tertiary">
            <span>{s.published_at ? formatRelativeTime(s.published_at) : ""}</span>
            {s.source_url && (
              <a
                href={s.source_url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-0.5 text-primary-500 hover:text-primary-600"
              >
                Source <ExternalLink size={10} />
              </a>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}

function CompetitorFeed({ signals }: { signals: IntelligenceOverviewData["competitor_signals"] }) {
  if (!signals?.length) {
    return <p className="py-8 text-center text-sm text-text-tertiary">No competitor signals</p>;
  }

  return (
    <div className="space-y-3">
      {signals.map((s) => (
        <div
          key={s.id}
          className="rounded-lg border border-neutral-bg p-3 transition-colors hover:bg-neutral-bg/30"
        >
          <div className="flex items-start justify-between gap-2">
            <div className="min-w-0 flex-1">
              <p className="text-sm font-medium text-text-primary">{s.title}</p>
              <p className="mt-0.5 text-xs text-text-tertiary">
                {s.competitor_name} · {s.source}
              </p>
            </div>
            <span className={`text-xs font-medium ${impactColor(s.impact_score)}`}>
              {Math.round(s.impact_score * 100)}%
            </span>
          </div>
          {s.context && (
            <p className="mt-2 text-xs text-text-secondary line-clamp-2">{s.context}</p>
          )}
          <p className="mt-1.5 text-[10px] text-text-tertiary">
            {s.published_at ? formatRelativeTime(s.published_at) : ""}
          </p>
        </div>
      ))}
    </div>
  );
}

function MarketFeed({ signals }: { signals: IntelligenceOverviewData["market_signals"] }) {
  if (!signals?.length) {
    return <p className="py-8 text-center text-sm text-text-tertiary">No market signals</p>;
  }

  return (
    <div className="space-y-3">
      {signals.map((s) => {
        const DirIcon =
          s.direction === "up"
            ? ArrowUpRight
            : s.direction === "down"
              ? ArrowDownRight
              : Minus;
        const dirColor =
          s.direction === "up"
            ? "text-revenue-positive"
            : s.direction === "down"
              ? "text-risk"
              : "text-text-tertiary";
        return (
          <div
            key={s.id}
            className="flex items-center gap-3 rounded-lg border border-neutral-bg p-3 transition-colors hover:bg-neutral-bg/30"
          >
            <DirIcon size={16} className={dirColor} />
            <div className="min-w-0 flex-1">
              <p className="text-sm font-medium text-text-primary">{s.title ?? s.indicator}</p>
              <p className="text-xs text-text-tertiary">{s.source}</p>
            </div>
            <div className="text-right">
              <p className="text-sm font-semibold text-text-primary">{s.value}</p>
              {s.change_pct != null && (
                <p className={`text-xs font-medium ${dirColor}`}>
                  {s.change_pct > 0 ? "+" : ""}
                  {s.change_pct.toFixed(1)}%
                </p>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}

export default function Competitive() {
  const { data, isLoading, error, refetch } = useIntelligenceOverview();

  if (isLoading) return <CompetitiveSkeleton />;

  if (error) {
    return (
      <div className="flex min-h-[400px] flex-col items-center justify-center rounded-lg bg-surface-card p-8 text-center shadow-card">
        <AlertTriangle className="h-8 w-8 text-risk" />
        <h2 className="mt-4 font-display text-lg font-semibold text-text-primary">
          Failed to load competitive intelligence
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
        <p className="text-sm text-text-tertiary">No intelligence data available</p>
      </div>
    );
  }

  return (
    <ErrorBoundary>
      <div className="space-y-6">
        <div>
          <h2 className="text-xl font-semibold text-text-primary">
            Competitive &amp; Policy Signals
          </h2>
          <p className="mt-1 text-sm text-text-secondary">
            Track market changes, RBI/SEBI policy shifts, and competitive activity mapped to active deals.
          </p>
        </div>

        <SignalTypeCards
          types={overview.signal_types}
          total={overview.total_signals}
        />

        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          <div className="card p-6">
            <h3 className="mb-4 text-sm font-semibold uppercase tracking-wider text-text-secondary">
              Policy Signals
            </h3>
            <div className="max-h-[420px] overflow-y-auto pr-1">
              <PolicyTimeline signals={overview.policy_signals} />
            </div>
          </div>

          <div className="card p-6">
            <h3 className="mb-4 text-sm font-semibold uppercase tracking-wider text-text-secondary">
              Competitor Activity
            </h3>
            <div className="max-h-[420px] overflow-y-auto pr-1">
              <CompetitorFeed signals={overview.competitor_signals} />
            </div>
          </div>
        </div>

        <div className="card p-6">
          <h3 className="mb-4 text-sm font-semibold uppercase tracking-wider text-text-secondary">
            Market Signals
          </h3>
          <div className="max-h-[400px] overflow-y-auto pr-1">
            <MarketFeed signals={overview.market_signals} />
          </div>
        </div>
      </div>
    </ErrorBoundary>
  );
}
