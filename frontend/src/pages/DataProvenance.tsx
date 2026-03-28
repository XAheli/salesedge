import { useDataSourceList, useHealthReady, type DataSourceHealthItem } from "@/api/hooks/useDataSources";
import { CheckCircle2, AlertCircle, XCircle, Database, Wifi, RefreshCw } from "lucide-react";

const STATUS_COLORS: Record<string, { text: string; bg: string }> = {
  healthy: { text: "text-revenue-positive", bg: "bg-revenue-positive/10" },
  degraded: { text: "text-caution", bg: "bg-caution/10" },
  down: { text: "text-risk", bg: "bg-risk/10" },
  unknown: { text: "text-text-tertiary", bg: "bg-neutral-bg" },
};

function StatusIcon({ status }: { status: string }) {
  if (status === "healthy") return <CheckCircle2 size={18} className="text-revenue-positive" />;
  if (status === "degraded") return <AlertCircle size={18} className="text-caution" />;
  if (status === "down") return <XCircle size={18} className="text-risk" />;
  return <AlertCircle size={18} className="text-text-tertiary" />;
}

export default function DataProvenance() {
  const { data: srcData, isLoading: srcLoading, error: srcError, refetch } = useDataSourceList();
  const { data: healthData, isLoading: healthLoading } = useHealthReady();

  if (srcLoading || healthLoading) {
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="card animate-pulse p-5">
              <div className="h-4 w-32 rounded bg-neutral-bg" />
              <div className="mt-3 h-6 w-20 rounded bg-neutral-bg" />
              <div className="mt-2 h-3 w-24 rounded bg-neutral-bg" />
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (srcError) {
    return (
      <div className="flex min-h-[400px] flex-col items-center justify-center card p-8 text-center">
        <XCircle className="h-8 w-8 text-risk" />
        <h2 className="mt-4 font-display text-lg font-semibold text-text-primary">Failed to load data sources</h2>
        <p className="mt-2 text-sm text-text-secondary">{(srcError as Error).message}</p>
        <button onClick={() => refetch()} className="mt-4 inline-flex items-center gap-2 rounded-lg bg-primary-500 px-4 py-2 text-sm font-semibold text-white hover:bg-primary-600">
          <RefreshCw size={16} /> Retry
        </button>
      </div>
    );
  }

  // Extract sources array from the nested response
  const rawData = srcData?.data;
  const sources: DataSourceHealthItem[] = Array.isArray(rawData) ? rawData : (rawData as { sources?: DataSourceHealthItem[] })?.sources ?? [];
  const healthStatus =
    healthData?.data?.status ?? (healthData as { status?: string } | undefined)?.status ?? "unknown";

  const healthyCount = sources.filter(s => s.status === "healthy").length;
  const issueCount = sources.filter(s => s.status !== "healthy").length;
  const tier1 = sources.filter(s => s.tier === 1);
  const tier2 = sources.filter(s => s.tier === 2);
  const tier3 = sources.filter(s => s.tier === 3);

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-text-primary">Data Provenance</h2>
        <p className="mt-1 text-sm text-text-secondary">
          Full transparency on data sources, freshness, quality scores, and ingestion health.
        </p>
      </div>

      {/* Summary KPIs */}
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        <div className="card p-4">
          <div className="flex items-center gap-2">
            <Database size={14} className="text-primary-500" />
            <p className="text-xs font-semibold uppercase tracking-wider text-text-tertiary">Total Sources</p>
          </div>
          <p className="mt-1 font-display text-2xl font-bold text-text-primary">{sources.length}</p>
        </div>
        <div className="card p-4">
          <div className="flex items-center gap-2">
            <CheckCircle2 size={14} className="text-revenue-positive" />
            <p className="text-xs font-semibold uppercase tracking-wider text-text-tertiary">Healthy</p>
          </div>
          <p className="mt-1 font-display text-2xl font-bold text-revenue-positive">{healthyCount}</p>
        </div>
        <div className="card p-4">
          <div className="flex items-center gap-2">
            <AlertCircle size={14} className="text-risk" />
            <p className="text-xs font-semibold uppercase tracking-wider text-text-tertiary">Issues</p>
          </div>
          <p className="mt-1 font-display text-2xl font-bold text-risk">{issueCount}</p>
        </div>
        <div className="card p-4">
          <div className="flex items-center gap-2">
            <Wifi size={14} className="text-primary-500" />
            <p className="text-xs font-semibold uppercase tracking-wider text-text-tertiary">API Status</p>
          </div>
          <p className={`mt-1 font-display text-lg font-bold capitalize ${healthStatus === "alive" || healthStatus === "ok" ? "text-revenue-positive" : "text-risk"}`}>
            {healthStatus === "alive" ? "Operational" : healthStatus}
          </p>
        </div>
      </div>

      {/* Tier 1: Government */}
      {tier1.length > 0 && (
        <SourceSection title="Tier 1 — Government & Official" sources={tier1} />
      )}

      {/* Tier 2: Market & Exchange */}
      {tier2.length > 0 && (
        <SourceSection title="Tier 2 — Market & Exchange" sources={tier2} />
      )}

      {/* Tier 3: Enrichment */}
      {tier3.length > 0 && (
        <SourceSection title="Tier 3 — Enrichment" sources={tier3} />
      )}

      {/* If no tier grouping worked, show all flat */}
      {tier1.length === 0 && tier2.length === 0 && tier3.length === 0 && sources.length > 0 && (
        <SourceSection title="All Data Sources" sources={sources} />
      )}
    </div>
  );
}

function SourceSection({ title, sources }: { title: string; sources: DataSourceHealthItem[] }) {
  return (
    <div>
      <h3 className="mb-3 text-sm font-semibold uppercase tracking-wider text-text-secondary">{title}</h3>
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {sources.map((s, i) => (
          <SourceCard key={s.name + i} source={s} />
        ))}
      </div>
    </div>
  );
}

function SourceCard({ source }: { source: DataSourceHealthItem }) {
  const colors =
    STATUS_COLORS[source.status] ??
    ({ text: "text-text-tertiary", bg: "bg-neutral-bg" } as const);
  return (
    <div className={`card overflow-hidden p-4 border-l-4 ${source.status === "healthy" ? "border-l-revenue-positive" : source.status === "degraded" ? "border-l-caution" : "border-l-neutral"}`}>
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-2">
          <StatusIcon status={source.status} />
          <div>
            <p className="text-sm font-semibold text-text-primary">{source.name}</p>
            <p className="text-xs text-text-tertiary">Tier {source.tier}</p>
          </div>
        </div>
        <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-[10px] font-semibold capitalize ${colors.text} ${colors.bg}`}>
          {source.status}
        </span>
      </div>
      <div className="mt-3 grid grid-cols-3 gap-2">
        <div>
          <p className="text-[10px] font-medium uppercase tracking-wider text-text-tertiary">Latency</p>
          <p className="mt-0.5 text-sm font-semibold text-text-primary">{source.response_time_ms}ms</p>
        </div>
        <div>
          <p className="text-[10px] font-medium uppercase tracking-wider text-text-tertiary">Freshness</p>
          <p className="mt-0.5 text-xs font-medium text-text-secondary">{source.data_freshness}</p>
        </div>
        <div>
          <p className="text-[10px] font-medium uppercase tracking-wider text-text-tertiary">Cache Hit</p>
          <p className="mt-0.5 text-sm font-semibold text-text-primary">{Math.round(source.cache_hit_rate * 100)}%</p>
        </div>
      </div>
      {source.error_rate > 0.01 && (
        <div className="mt-2 rounded bg-risk/5 px-2 py-1">
          <p className="text-xs text-risk">Error rate: {(source.error_rate * 100).toFixed(1)}%</p>
        </div>
      )}
    </div>
  );
}
