import { useQuery } from "@tanstack/react-query";
import { Link, useParams } from "react-router-dom";
import {
  ArrowLeft,
  RefreshCw,
  AlertTriangle,
  IndianRupee,
  GitBranch,
  Gauge,
  CalendarClock,
  User,
  Percent,
} from "lucide-react";
import { get } from "@/api/client";
import { computeRiskLevel } from "@/api/hooks/useDeals";
import { SkeletonCard } from "@/components/data-display/LoadingSkeleton";
import { formatINR, formatIST } from "@/utils/indian-formatting";
import { formatRelativeTime } from "@/utils/date-helpers";

/** Shape returned in `data` from GET /api/v1/deals/{id}. */
interface DealDetailPayload {
  id: string;
  prospect_name: string;
  title?: string | null;
  stage: string;
  value_inr: number;
  risk_score: number;
  days_in_stage: number;
  owner: string | null;
  last_activity: string | null;
  expected_close_date: string | null;
  win_probability: number | null;
  engagement_score: number | null;
}

function riskBarFillClass(level: ReturnType<typeof computeRiskLevel>): string {
  switch (level) {
    case "critical":
      return "bg-red-600";
    case "high":
      return "bg-risk";
    case "medium":
      return "bg-caution";
    default:
      return "bg-revenue-positive";
  }
}

function riskLabelClass(level: ReturnType<typeof computeRiskLevel>): string {
  switch (level) {
    case "critical":
      return "text-red-700";
    case "high":
      return "text-risk";
    case "medium":
      return "text-caution";
    default:
      return "text-revenue-positive";
  }
}

function formatWinProbability(p: number | null): string {
  if (p == null || !Number.isFinite(p)) return "—";
  const pct = p <= 1 ? p * 100 : p;
  return `${Math.round(pct)}%`;
}

function KpiCard({
  label,
  value,
  icon,
}: {
  label: string;
  value: React.ReactNode;
  icon: React.ReactNode;
}) {
  return (
    <div className="card p-4">
      <div className="flex items-center gap-2 text-text-tertiary">
        {icon}
        <span className="text-xs font-semibold uppercase tracking-wider">{label}</span>
      </div>
      <div className="mt-2 text-lg font-bold text-text-primary">{value}</div>
    </div>
  );
}

function DealDetailSkeleton() {
  return (
    <div className="space-y-6">
      <div className="h-10 w-3/4 max-w-lg rounded bg-neutral-bg" />
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {Array.from({ length: 6 }).map((_, i) => (
          <SkeletonCard key={i} />
        ))}
      </div>
      <SkeletonCard className="min-h-[120px]" />
    </div>
  );
}

export default function DealDetail() {
  const { id } = useParams<{ id: string }>();

  const { data, isLoading, error, refetch, isFetching } = useQuery({
    queryKey: ["deals", "detail", id],
    queryFn: async () => {
      if (!id) throw new Error("Missing deal id");
      const res = await get<DealDetailPayload>(`/v1/deals/${id}`);
      if (res.data == null) {
        throw new Error("Deal not found");
      }
      return res.data;
    },
    enabled: Boolean(id),
  });

  if (!id) {
    return (
      <div className="rounded-lg bg-surface-card p-8 text-center shadow-card">
        <p className="text-sm text-text-secondary">Invalid deal link.</p>
        <Link to="/deals" className="mt-4 inline-block text-sm font-semibold text-primary-500">
          Back to Deals
        </Link>
      </div>
    );
  }

  if (isLoading) {
    return <DealDetailSkeleton />;
  }

  if (error) {
    return (
      <div className="flex min-h-[400px] flex-col items-center justify-center rounded-lg bg-surface-card p-8 text-center shadow-card">
        <AlertTriangle className="h-8 w-8 text-risk" />
        <h2 className="mt-4 font-display text-lg font-semibold text-text-primary">
          Failed to load deal
        </h2>
        <p className="mt-2 text-sm text-text-secondary">{(error as Error).message}</p>
        <button
          type="button"
          onClick={() => refetch()}
          disabled={isFetching}
          className="mt-4 inline-flex items-center gap-2 rounded-lg bg-primary-500 px-4 py-2 text-sm font-semibold text-white hover:bg-primary-600 disabled:opacity-60"
        >
          <RefreshCw size={16} className={isFetching ? "animate-spin" : ""} />
          Retry
        </button>
        <Link to="/deals" className="mt-4 text-sm font-medium text-primary-500 hover:text-primary-600">
          Back to Deals
        </Link>
      </div>
    );
  }

  const d = data!;
  const riskPct = Math.min(100, Math.max(0, Math.round(d.risk_score)));
  const riskLevel = computeRiskLevel(d.risk_score);
  const barClass = riskBarFillClass(riskLevel);
  const labelClass = riskLabelClass(riskLevel);

  return (
    <div className="space-y-6">
      <div>
        <Link
          to="/deals"
          className="mb-3 inline-flex items-center gap-1.5 text-sm font-medium text-primary-500 hover:text-primary-600"
        >
          <ArrowLeft size={16} />
          Back to Deals
        </Link>
        <h1 className="font-display text-3xl font-bold tracking-tight text-text-primary">
          {d.prospect_name}
        </h1>
        {d.title ? (
          <p className="mt-1 text-lg text-text-secondary">{d.title}</p>
        ) : null}
        <div className="mt-2 flex flex-wrap gap-x-4 gap-y-1 text-xs text-text-tertiary">
          {d.last_activity && <span>Last activity {formatRelativeTime(d.last_activity)}</span>}
          {d.engagement_score != null && Number.isFinite(d.engagement_score) && (
            <span>Engagement score {Math.round(d.engagement_score)}</span>
          )}
        </div>
      </div>

      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        <KpiCard
          label="Value"
          icon={<IndianRupee size={14} className="text-primary-500" />}
          value={formatINR(d.value_inr)}
        />
        <KpiCard
          label="Stage"
          icon={<GitBranch size={14} className="text-primary-500" />}
          value={
            <span className="inline-flex rounded-md bg-neutral-bg px-2 py-0.5 text-base capitalize text-text-primary">
              {d.stage}
            </span>
          }
        />
        <KpiCard
          label="Risk score"
          icon={<Gauge size={14} className="text-primary-500" />}
          value={<span className={labelClass}>{riskPct} / 100</span>}
        />
        <KpiCard
          label="Days in stage"
          icon={<CalendarClock size={14} className="text-primary-500" />}
          value={d.days_in_stage}
        />
        <KpiCard
          label="Owner"
          icon={<User size={14} className="text-primary-500" />}
          value={d.owner ?? "—"}
        />
        <KpiCard
          label="Win probability"
          icon={<Percent size={14} className="text-primary-500" />}
          value={formatWinProbability(d.win_probability)}
        />
      </div>

      <div className="card p-5">
        <div className="flex items-center justify-between gap-4">
          <h2 className="text-sm font-semibold text-text-primary">Risk level</h2>
          <span className={`text-sm font-bold capitalize ${labelClass}`}>{riskLevel}</span>
        </div>
        <p className="mt-1 text-xs text-text-tertiary">Scale 0 (low) — 100 (high)</p>
        <div className="mt-4 h-3 w-full overflow-hidden rounded-full bg-neutral-bg">
          <div
            className={`h-full rounded-full transition-all ${barClass}`}
            style={{ width: `${riskPct}%` }}
            role="progressbar"
            aria-valuenow={riskPct}
            aria-valuemin={0}
            aria-valuemax={100}
          />
        </div>
      </div>

      {d.expected_close_date ? (
        <div className="card p-4">
          <p className="text-xs font-semibold uppercase tracking-wider text-text-tertiary">
            Expected close date
          </p>
          <p className="mt-2 text-sm font-medium text-text-primary">
            {formatIST(d.expected_close_date, "full")}
          </p>
        </div>
      ) : null}
    </div>
  );
}
