import { useQuery } from "@tanstack/react-query";
import { Link, useParams } from "react-router-dom";
import { ArrowLeft, RefreshCw, AlertTriangle } from "lucide-react";
import { get } from "@/api/client";
import { SkeletonCard } from "@/components/data-display/LoadingSkeleton";
import { formatINR } from "@/utils/indian-formatting";
import { formatRelativeTime } from "@/utils/date-helpers";

/** Shape returned in `data` from GET /api/v1/prospects/{id} (may include extra fields as API evolves). */
interface ProspectDetailPayload {
  id: string;
  company_name: string;
  industry: string | null;
  nic_code: string | null;
  employee_count: number | null;
  state: string | null;
  city: string | null;
  gst_number: string | null;
  website: string | null;
  listed_exchange: string | null;
  bse_code: string | null;
  nse_symbol: string | null;
  dpiit_recognized: boolean;
  fit_score: number | null;
  confidence: number | null;
  last_enriched: string | null;
  revenue_band_inr?: string | null;
  financial_health?: { revenue_inr: number | null } | null;
}

function fitScoreBadgeClass(score: number): string {
  if (score >= 85) return "bg-revenue-positive text-white";
  if (score >= 70) return "bg-caution text-white";
  if (score >= 50) return "bg-amber-400 text-white";
  return "bg-risk text-white";
}

function formatEmployees(count: number | null): string {
  if (count == null) return "—";
  return new Intl.NumberFormat("en-IN").format(count);
}

function formatRevenue(p: ProspectDetailPayload): string {
  if (p.revenue_band_inr?.trim()) return p.revenue_band_inr;
  const rev = p.financial_health?.revenue_inr;
  if (rev != null && Number.isFinite(rev)) return formatINR(rev);
  return "—";
}

function normalizeWebsite(url: string): string {
  const t = url.trim();
  if (!t) return t;
  if (/^https?:\/\//i.test(t)) return t;
  return `https://${t}`;
}

function DetailCard({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="card p-4">
      <p className="text-xs font-semibold uppercase tracking-wider text-text-tertiary">
        {label}
      </p>
      <div className="mt-2 text-sm font-medium text-text-primary">{children}</div>
    </div>
  );
}

function ProspectDetailSkeleton() {
  return (
    <div className="space-y-6">
      <div className="h-10 w-2/3 max-w-md rounded bg-neutral-bg" />
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {Array.from({ length: 9 }).map((_, i) => (
          <SkeletonCard key={i} />
        ))}
      </div>
    </div>
  );
}

export default function ProspectDetail() {
  const { id } = useParams<{ id: string }>();

  const { data, isLoading, error, refetch, isFetching } = useQuery({
    queryKey: ["prospects", "detail", id],
    queryFn: async () => {
      if (!id) throw new Error("Missing prospect id");
      const res = await get<ProspectDetailPayload>(`/v1/prospects/${id}`);
      if (res.data == null) {
        throw new Error("Prospect not found");
      }
      return res.data;
    },
    enabled: Boolean(id),
  });

  if (!id) {
    return (
      <div className="rounded-lg bg-surface-card p-8 text-center shadow-card">
        <p className="text-sm text-text-secondary">Invalid prospect link.</p>
        <Link to="/prospects" className="mt-4 inline-block text-sm font-semibold text-primary-500">
          Back to Prospects
        </Link>
      </div>
    );
  }

  if (isLoading) {
    return <ProspectDetailSkeleton />;
  }

  if (error) {
    return (
      <div className="flex min-h-[400px] flex-col items-center justify-center rounded-lg bg-surface-card p-8 text-center shadow-card">
        <AlertTriangle className="h-8 w-8 text-risk" />
        <h2 className="mt-4 font-display text-lg font-semibold text-text-primary">
          Failed to load prospect
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
        <Link
          to="/prospects"
          className="mt-4 text-sm font-medium text-primary-500 hover:text-primary-600"
        >
          Back to Prospects
        </Link>
      </div>
    );
  }

  const p = data!;

  const location = [p.state, p.city].filter(Boolean).join(", ") || "—";
  const codesLine =
    p.bse_code || p.nse_symbol
      ? [p.bse_code && `BSE ${p.bse_code}`, p.nse_symbol && `NSE ${p.nse_symbol}`].filter(Boolean).join(" · ")
      : null;

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <Link
            to="/prospects"
            className="mb-3 inline-flex items-center gap-1.5 text-sm font-medium text-primary-500 hover:text-primary-600"
          >
            <ArrowLeft size={16} />
            Back to Prospects
          </Link>
          <h1 className="font-display text-3xl font-bold tracking-tight text-text-primary">
            {p.company_name}
          </h1>
          <div className="mt-3 flex flex-wrap items-center gap-2">
            {p.fit_score != null ? (
              <span
                className={`inline-flex rounded-md px-2.5 py-1 text-xs font-semibold ${fitScoreBadgeClass(p.fit_score)}`}
              >
                Fit score {p.fit_score.toFixed(0)}
                {p.confidence != null && (
                  <span className="ml-1 opacity-90">
                    ({Math.round(p.confidence * 100)}% confidence)
                  </span>
                )}
              </span>
            ) : (
              <span className="inline-flex rounded-md bg-neutral-bg px-2.5 py-1 text-xs font-semibold text-text-secondary">
                Not scored
              </span>
            )}
            {p.last_enriched && (
              <span className="text-xs text-text-tertiary">
                Last enriched {formatRelativeTime(p.last_enriched)}
              </span>
            )}
          </div>
        </div>
      </div>

      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        <DetailCard label="Industry">{p.industry ?? "—"}</DetailCard>
        <DetailCard label="NIC Code">{p.nic_code ?? "—"}</DetailCard>
        <DetailCard label="State / City">{location}</DetailCard>
        <DetailCard label="Employees">{formatEmployees(p.employee_count)}</DetailCard>
        <DetailCard label="Revenue">{formatRevenue(p)}</DetailCard>
        <DetailCard label="Listed exchange">{p.listed_exchange ?? "—"}</DetailCard>
        <DetailCard label="BSE / NSE codes">{codesLine ?? "—"}</DetailCard>
        <DetailCard label="Website">
          {p.website ? (
            <a
              href={normalizeWebsite(p.website)}
              target="_blank"
              rel="noopener noreferrer"
              className="text-primary-500 underline-offset-2 hover:underline"
            >
              {p.website}
            </a>
          ) : (
            "—"
          )}
        </DetailCard>
        <DetailCard label="GST">{p.gst_number ?? "—"}</DetailCard>
        <DetailCard label="DPIIT recognized">{p.dpiit_recognized ? "Yes" : "No"}</DetailCard>
      </div>
    </div>
  );
}
