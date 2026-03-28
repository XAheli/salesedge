import { memo, useState, useRef, useCallback, type ReactNode } from "react";
import {
  Info,
  Download,
  Image as ImageIcon,
  ChevronDown,
  Loader2,
  AlertTriangle,
} from "lucide-react";
import { EmptyState } from "@/components/data-display/EmptyState";
import { SkeletonChart } from "@/components/data-display/LoadingSkeleton";

export type TimeWindow = "7d" | "30d" | "90d" | "1y";

export interface ChartMetadata {
  metricOwner?: string;
  formula?: string;
  dataSource?: string[];
  refreshSLA?: string;
  confidenceMethod?: string;
  lastRefreshed?: string;
  sampleSize?: number;
}

export interface ChartContainerProps {
  title: string;
  subtitle?: string;
  children: ReactNode;
  metadata?: ChartMetadata;
  timeWindow?: TimeWindow;
  onTimeWindowChange?: (tw: TimeWindow) => void;
  exportFormats?: ("csv" | "png")[];
  loading?: boolean;
  error?: string | null;
  empty?: boolean;
  emptyMessage?: string;
  className?: string;
}

const TIME_OPTIONS: TimeWindow[] = ["7d", "30d", "90d", "1y"];

export const ChartContainer = memo(function ChartContainer({
  title,
  subtitle,
  children,
  metadata,
  timeWindow,
  onTimeWindowChange,
  exportFormats,
  loading,
  error,
  empty,
  emptyMessage,
  className = "",
}: ChartContainerProps) {
  const [showMeta, setShowMeta] = useState(false);
  const chartRef = useRef<HTMLDivElement>(null);

  const handlePngExport = useCallback(() => {
    if (!chartRef.current) return;
    const svg = chartRef.current.querySelector("svg");
    if (!svg) return;

    const canvas = document.createElement("canvas");
    const rect = svg.getBoundingClientRect();
    canvas.width = rect.width * 2;
    canvas.height = rect.height * 2;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    ctx.scale(2, 2);
    const data = new XMLSerializer().serializeToString(svg);
    const img = new window.Image();
    img.onload = () => {
      ctx.drawImage(img, 0, 0);
      const a = document.createElement("a");
      a.download = `${title.replace(/\s+/g, "_").toLowerCase()}.png`;
      a.href = canvas.toDataURL("image/png");
      a.click();
    };
    img.src = "data:image/svg+xml;base64," + btoa(unescape(encodeURIComponent(data)));
  }, [title]);

  return (
    <div className={`rounded-md bg-surface-card shadow-card ${className}`}>
      <div className="flex flex-wrap items-start justify-between gap-2 border-b border-neutral-bg px-4 py-3">
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-1.5">
            <h3 className="font-display text-sm font-semibold text-text-primary">{title}</h3>
            {metadata && (
              <div className="relative">
                <button
                  onClick={() => setShowMeta(!showMeta)}
                  className="rounded p-0.5 text-text-tertiary transition-colors hover:text-text-secondary"
                  aria-label="Chart metadata"
                >
                  <Info size={14} />
                </button>
                {showMeta && (
                  <>
                    <div className="fixed inset-0 z-40" onClick={() => setShowMeta(false)} />
                    <div className="absolute left-0 top-full z-50 mt-1 w-72 rounded-md border border-neutral-bg bg-surface-card p-3 shadow-lg">
                      <dl className="space-y-2 text-xs">
                        {metadata.metricOwner && (
                          <div>
                            <dt className="font-medium text-text-secondary">Owner</dt>
                            <dd className="text-text-primary">{metadata.metricOwner}</dd>
                          </div>
                        )}
                        {metadata.formula && (
                          <div>
                            <dt className="font-medium text-text-secondary">Formula</dt>
                            <dd className="font-mono text-text-primary">{metadata.formula}</dd>
                          </div>
                        )}
                        {metadata.dataSource?.length && (
                          <div>
                            <dt className="font-medium text-text-secondary">Sources</dt>
                            <dd className="text-text-primary">{metadata.dataSource.join(", ")}</dd>
                          </div>
                        )}
                        {metadata.refreshSLA && (
                          <div>
                            <dt className="font-medium text-text-secondary">Refresh SLA</dt>
                            <dd className="text-text-primary">{metadata.refreshSLA}</dd>
                          </div>
                        )}
                        {metadata.confidenceMethod && (
                          <div>
                            <dt className="font-medium text-text-secondary">Confidence</dt>
                            <dd className="text-text-primary">{metadata.confidenceMethod}</dd>
                          </div>
                        )}
                        {metadata.sampleSize !== undefined && (
                          <div>
                            <dt className="font-medium text-text-secondary">Sample Size</dt>
                            <dd className="text-text-primary">
                              {metadata.sampleSize.toLocaleString("en-IN")}
                            </dd>
                          </div>
                        )}
                        {metadata.lastRefreshed && (
                          <div>
                            <dt className="font-medium text-text-secondary">Last Refreshed</dt>
                            <dd className="text-text-primary">{metadata.lastRefreshed}</dd>
                          </div>
                        )}
                      </dl>
                    </div>
                  </>
                )}
              </div>
            )}
          </div>
          {subtitle && <p className="mt-0.5 text-xs text-text-secondary">{subtitle}</p>}
        </div>

        <div className="flex items-center gap-2">
          {timeWindow && onTimeWindowChange && (
            <div className="inline-flex rounded-md border border-neutral-bg">
              {TIME_OPTIONS.map((tw) => (
                <button
                  key={tw}
                  onClick={() => onTimeWindowChange(tw)}
                  className={`px-2.5 py-1 text-xs font-medium transition-colors first:rounded-l-md last:rounded-r-md ${
                    timeWindow === tw
                      ? "bg-primary-500 text-white"
                      : "text-text-secondary hover:bg-neutral-bg"
                  }`}
                >
                  {tw}
                </button>
              ))}
            </div>
          )}

          {exportFormats && exportFormats.length > 0 && (
            <div className="flex gap-1">
              {exportFormats.includes("png") && (
                <button
                  onClick={handlePngExport}
                  className="rounded-md border border-neutral-bg p-1.5 text-text-secondary transition-colors hover:bg-neutral-bg"
                  aria-label="Export PNG"
                >
                  <ImageIcon size={14} />
                </button>
              )}
              {exportFormats.includes("csv") && (
                <button
                  className="rounded-md border border-neutral-bg p-1.5 text-text-secondary transition-colors hover:bg-neutral-bg"
                  aria-label="Export CSV"
                >
                  <Download size={14} />
                </button>
              )}
            </div>
          )}
        </div>
      </div>

      <div ref={chartRef} className="p-4">
        {loading ? (
          <div className="flex h-64 items-center justify-center">
            <Loader2 className="h-6 w-6 animate-spin text-primary-400" />
          </div>
        ) : error ? (
          <div className="flex h-64 flex-col items-center justify-center gap-2 text-center">
            <AlertTriangle className="h-8 w-8 text-risk" />
            <p className="text-sm text-text-secondary">{error}</p>
          </div>
        ) : empty ? (
          <EmptyState title={emptyMessage ?? "No chart data"} />
        ) : (
          children
        )}
      </div>
    </div>
  );
});
