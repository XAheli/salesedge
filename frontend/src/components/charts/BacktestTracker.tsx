import { memo, useMemo } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import { ChartContainer } from "./ChartContainer";

export interface BacktestDataPoint {
  date: string;
  mape?: number;
  mae?: number;
  rmse?: number;
  brierScore?: number;
}

interface BacktestTrackerProps {
  data: BacktestDataPoint[];
  loading?: boolean;
  error?: string | null;
  className?: string;
}

const METRIC_CONFIG = {
  mape: { label: "MAPE (%)", color: "#F97316", fmt: (v: number) => `${v.toFixed(2)}%` },
  mae: { label: "MAE", color: "#059669", fmt: (v: number) => v.toFixed(4) },
  rmse: { label: "RMSE", color: "#2563EB", fmt: (v: number) => v.toFixed(4) },
  brierScore: { label: "Brier Score", color: "#7C3AED", fmt: (v: number) => v.toFixed(4) },
} as const;

type MetricKey = keyof typeof METRIC_CONFIG;

export const BacktestTracker = memo(function BacktestTracker({
  data,
  loading,
  error,
  className = "",
}: BacktestTrackerProps) {
  const isEmpty = !loading && !error && data.length === 0;

  const activeMetrics = useMemo(() => {
    const keys = new Set<MetricKey>();
    for (const d of data) {
      if (d.mape !== undefined) keys.add("mape");
      if (d.mae !== undefined) keys.add("mae");
      if (d.rmse !== undefined) keys.add("rmse");
      if (d.brierScore !== undefined) keys.add("brierScore");
    }
    return [...keys];
  }, [data]);

  const latestScores = useMemo(() => {
    if (!data.length) return null;
    const last = data[data.length - 1]!;
    return activeMetrics
      .map((k) => {
        const val = last[k];
        return val !== undefined ? `${METRIC_CONFIG[k].label}: ${METRIC_CONFIG[k].fmt(val)}` : null;
      })
      .filter(Boolean)
      .join(" · ");
  }, [data, activeMetrics]);

  const textSummary = useMemo(() => {
    if (!data.length) return "No backtest data available.";
    const latest = latestScores ? `Latest — ${latestScores}.` : "";
    return `Backtest history: ${data.length} data points from ${data[0]!.date} to ${data[data.length - 1]!.date}. ${latest}`;
  }, [data, latestScores]);

  return (
    <ChartContainer
      title="Backtest Performance"
      subtitle={latestScores ?? "Historical accuracy metrics over time"}
      loading={loading}
      error={error}
      empty={isEmpty}
      emptyMessage="No backtest data"
      className={className}
    >
      <ResponsiveContainer width="100%" height={320}>
        <LineChart data={data} margin={{ top: 8, right: 12, bottom: 4, left: 10 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#F3F4F6" />
          <XAxis
            dataKey="date"
            tick={{ fontSize: 11, fill: "#57534E" }}
            axisLine={{ stroke: "#F3F4F6" }}
            tickLine={false}
          />
          <YAxis
            tick={{ fontSize: 11, fill: "#57534E" }}
            axisLine={false}
            tickLine={false}
            label={{
              value: "Score",
              angle: -90,
              position: "insideLeft",
              offset: 10,
              style: { fontSize: 10, fill: "#A8A29E" },
            }}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: "#FFFFFF",
              border: "1px solid #F3F4F6",
              borderRadius: 8,
              fontSize: 12,
            }}
            formatter={(value: number, name: string) => {
              const cfg = METRIC_CONFIG[name as MetricKey];
              return cfg ? [cfg.fmt(value), cfg.label] : [value.toFixed(4), name];
            }}
          />
          <Legend
            wrapperStyle={{ fontSize: 10, paddingTop: 8 }}
            formatter={(value: string) => METRIC_CONFIG[value as MetricKey]?.label ?? value}
          />
          {activeMetrics.map((k) => (
            <Line
              key={k}
              type="monotone"
              dataKey={k}
              stroke={METRIC_CONFIG[k].color}
              strokeWidth={2}
              dot={{ r: 2, fill: METRIC_CONFIG[k].color }}
              activeDot={{ r: 4 }}
              connectNulls
            />
          ))}
        </LineChart>
      </ResponsiveContainer>

      <details className="mt-3 text-xs text-text-secondary">
        <summary className="cursor-pointer font-medium">View as text</summary>
        <p className="mt-1">{textSummary}</p>
      </details>
    </ChartContainer>
  );
});

export default BacktestTracker;
