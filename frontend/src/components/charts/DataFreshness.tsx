import { memo, useMemo } from "react";

export interface DataSourceFreshness {
  name: string;
  lastUpdated: string | Date;
  sla?: number;
}

interface DataFreshnessProps {
  sources: DataSourceFreshness[];
  className?: string;
}

function getMinutesAgo(d: Date): number {
  return Math.max(0, Math.floor((Date.now() - d.getTime()) / 60_000));
}

function getStatus(minutes: number): "fresh" | "aging" | "stale" {
  if (minutes <= 5) return "fresh";
  if (minutes <= 60) return "aging";
  return "stale";
}

const STATUS_CONFIG = {
  fresh: {
    ring: "stroke-revenue-positive",
    text: "text-revenue-positive",
    bg: "bg-revenue-positive-bg",
    label: "Fresh",
  },
  aging: {
    ring: "stroke-caution",
    text: "text-caution",
    bg: "bg-caution-bg",
    label: "Aging",
  },
  stale: {
    ring: "stroke-risk",
    text: "text-risk",
    bg: "bg-risk-bg",
    label: "Stale",
  },
};

function CircularGauge({
  minutes,
  maxMinutes = 120,
}: {
  minutes: number;
  maxMinutes?: number;
}) {
  const status = getStatus(minutes);
  const cfg = STATUS_CONFIG[status];
  const pct = Math.min(1, minutes / maxMinutes);
  const r = 28;
  const circumference = 2 * Math.PI * r;
  const offset = circumference * (1 - pct);

  return (
    <svg width={72} height={72} className="-rotate-90">
      <circle
        cx={36}
        cy={36}
        r={r}
        fill="none"
        stroke="currentColor"
        strokeWidth={5}
        className="text-neutral-bg"
      />
      <circle
        cx={36}
        cy={36}
        r={r}
        fill="none"
        strokeWidth={5}
        strokeDasharray={circumference}
        strokeDashoffset={offset}
        strokeLinecap="round"
        className={cfg.ring}
      />
    </svg>
  );
}

function formatDuration(minutes: number): string {
  if (minutes < 1) return "<1m";
  if (minutes < 60) return `${minutes}m`;
  const h = Math.floor(minutes / 60);
  const m = minutes % 60;
  return m > 0 ? `${h}h ${m}m` : `${h}h`;
}

export const DataFreshness = memo(function DataFreshness({
  sources,
  className = "",
}: DataFreshnessProps) {
  const items = useMemo(
    () =>
      sources.map((s) => {
        const d = s.lastUpdated instanceof Date ? s.lastUpdated : new Date(s.lastUpdated);
        const mins = getMinutesAgo(d);
        return { ...s, date: d, minutes: mins, status: getStatus(mins) };
      }),
    [sources],
  );

  return (
    <div className={`grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-6 ${className}`}>
      {items.map((item) => {
        const cfg = STATUS_CONFIG[item.status];
        return (
          <div
            key={item.name}
            className="flex flex-col items-center rounded-md bg-surface-card p-4 shadow-card"
          >
            <div className="relative">
              <CircularGauge minutes={item.minutes} />
              <div className="absolute inset-0 flex rotate-90 items-center justify-center">
                <span className={`text-xs font-bold ${cfg.text}`}>
                  {formatDuration(item.minutes)}
                </span>
              </div>
            </div>
            <p className="mt-2 text-center text-xs font-medium text-text-primary">
              {item.name}
            </p>
            <span
              className={`mt-1 rounded-full px-2 py-0.5 text-[10px] font-medium ${cfg.bg} ${cfg.text}`}
            >
              {cfg.label}
            </span>
          </div>
        );
      })}
    </div>
  );
});
