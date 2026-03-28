import { memo, type ReactNode } from "react";
import {
  AreaChart,
  Area,
  ResponsiveContainer,
} from "recharts";
import { TrendingUp, TrendingDown, Minus, Info } from "lucide-react";
import { formatINR } from "@/utils/indian-formatting";
import { ConfidenceBadge } from "./ConfidenceBadge";

export interface KPITrend {
  direction: "up" | "down" | "flat";
  value: number;
  period: string;
  isPositive: boolean;
}

export interface KPICardProps {
  title: string;
  value: string | number;
  unit?: "₹" | "%" | "days" | string;
  format?: "inr" | "percent" | "number" | "days";
  trend?: KPITrend;
  sparkline?: number[];
  confidence?: number;
  source?: string;
  lastUpdated?: string;
  onClick?: () => void;
  className?: string;
  children?: ReactNode;
}

function formatValue(
  value: string | number,
  format?: KPICardProps["format"],
  unit?: string,
): string {
  if (typeof value === "string") return value;

  switch (format) {
    case "inr":
      return formatINR(value, { compact: true });
    case "percent":
      return `${value.toFixed(1)}%`;
    case "days":
      return `${Math.round(value)}d`;
    case "number":
    default:
      return value.toLocaleString("en-IN");
  }
}

const TrendIcon = memo(function TrendIcon({
  direction,
}: {
  direction: KPITrend["direction"];
}) {
  switch (direction) {
    case "up":
      return <TrendingUp size={14} />;
    case "down":
      return <TrendingDown size={14} />;
    default:
      return <Minus size={14} />;
  }
});

const MiniSparkline = memo(function MiniSparkline({
  data,
  isPositive,
}: {
  data: number[];
  isPositive?: boolean;
}) {
  const color = isPositive === false ? "#DC2626" : "#059669";
  const chartData = data.map((v, i) => ({ i, v }));

  return (
    <div className="h-8 w-20">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={chartData} margin={{ top: 0, right: 0, bottom: 0, left: 0 }}>
          <defs>
            <linearGradient id={`spark-${color}`} x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={color} stopOpacity={0.3} />
              <stop offset="100%" stopColor={color} stopOpacity={0} />
            </linearGradient>
          </defs>
          <Area
            type="monotone"
            dataKey="v"
            stroke={color}
            strokeWidth={1.5}
            fill={`url(#spark-${color})`}
            dot={false}
            isAnimationActive={false}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
});

export const KPICard = memo(function KPICard({
  title,
  value,
  unit,
  format,
  trend,
  sparkline,
  confidence,
  source,
  lastUpdated,
  onClick,
  className = "",
}: KPICardProps) {
  const displayValue = formatValue(value, format, unit);
  const isClickable = !!onClick;

  return (
    <div
      className={`
        relative rounded-md bg-surface-card shadow-card p-4
        ${isClickable ? "cursor-pointer transition-shadow hover:shadow-md" : ""}
        ${className}
      `}
      onClick={onClick}
      role={isClickable ? "button" : undefined}
      tabIndex={isClickable ? 0 : undefined}
      onKeyDown={
        isClickable
          ? (e) => {
              if (e.key === "Enter" || e.key === " ") onClick?.();
            }
          : undefined
      }
    >
      <div className="flex items-start justify-between gap-2">
        <p className="text-xs font-medium uppercase tracking-wider text-text-secondary">
          {title}
        </p>
        {confidence !== undefined && <ConfidenceBadge confidence={confidence} size="sm" />}
      </div>

      <div className="mt-2 flex items-end justify-between gap-3">
        <div className="min-w-0 flex-1">
          <p className="font-display text-[28px] font-bold leading-tight text-text-primary">
            {displayValue}
            {unit && format !== "inr" && format !== "percent" && format !== "days" && (
              <span className="ml-1 text-base font-medium text-text-secondary">{unit}</span>
            )}
          </p>

          {trend && (
            <div
              className={`mt-1.5 inline-flex items-center gap-1 text-xs font-medium ${
                trend.isPositive ? "text-revenue-positive" : "text-risk"
              }`}
            >
              <TrendIcon direction={trend.direction} />
              <span>
                {trend.direction !== "flat" && (trend.value > 0 ? "+" : "")}
                {trend.value.toFixed(1)}%
              </span>
              <span className="text-text-tertiary">{trend.period}</span>
            </div>
          )}
        </div>

        {sparkline && sparkline.length > 1 && (
          <MiniSparkline data={sparkline} isPositive={trend?.isPositive} />
        )}
      </div>

      {(source || lastUpdated) && (
        <div className="mt-3 flex items-center justify-between border-t border-neutral-bg pt-2">
          {lastUpdated && (
            <span className="text-[10px] text-text-tertiary">{lastUpdated}</span>
          )}
          {source && (
            <span className="flex items-center gap-0.5 text-[10px] text-text-tertiary">
              <Info size={10} />
              {source}
            </span>
          )}
        </div>
      )}
    </div>
  );
});
