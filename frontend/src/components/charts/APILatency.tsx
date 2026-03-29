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

export interface LatencyDataPoint {
  timestamp: string;
  endpoint: string;
  p50: number;
  p95: number;
  p99: number;
}

interface APILatencyProps {
  data: LatencyDataPoint[];
  endpoints?: string[];
  loading?: boolean;
  error?: string | null;
  className?: string;
}

const ENDPOINT_COLORS = [
  "#F97316", "#059669", "#2563EB", "#7C3AED",
  "#DC2626", "#D97706", "#0891B2", "#BE185D",
];

const PERCENTILE_STYLES = {
  p50: { strokeWidth: 2, strokeDasharray: undefined },
  p95: { strokeWidth: 1.5, strokeDasharray: "6 3" },
  p99: { strokeWidth: 1, strokeDasharray: "3 3" },
} as const;

export const APILatency = memo(function APILatency({
  data,
  endpoints: endpointsProp,
  loading,
  error,
  className = "",
}: APILatencyProps) {
  const isEmpty = !loading && !error && data.length === 0;

  const endpoints = useMemo(
    () => endpointsProp ?? [...new Set(data.map((d) => d.endpoint))],
    [endpointsProp, data],
  );

  const pivoted = useMemo(() => {
    const byTime = new Map<string, Record<string, number | string>>();
    for (const d of data) {
      if (!byTime.has(d.timestamp)) {
        byTime.set(d.timestamp, { timestamp: d.timestamp });
      }
      const row = byTime.get(d.timestamp)!;
      row[`${d.endpoint}_p50`] = d.p50;
      row[`${d.endpoint}_p95`] = d.p95;
      row[`${d.endpoint}_p99`] = d.p99;
    }
    return [...byTime.values()].sort((a, b) =>
      String(a.timestamp).localeCompare(String(b.timestamp)),
    );
  }, [data]);

  const colorMap = useMemo(
    () => Object.fromEntries(endpoints.map((e, i) => [e, ENDPOINT_COLORS[i % ENDPOINT_COLORS.length]])),
    [endpoints],
  );

  const textSummary = useMemo(() => {
    if (!data.length) return "No latency data available.";
    const grouped = new Map<string, LatencyDataPoint[]>();
    for (const d of data) {
      if (!grouped.has(d.endpoint)) grouped.set(d.endpoint, []);
      grouped.get(d.endpoint)!.push(d);
    }
    return [...grouped.entries()]
      .map(([ep, pts]) => {
        const avgP50 = pts.reduce((s, p) => s + p.p50, 0) / pts.length;
        const avgP95 = pts.reduce((s, p) => s + p.p95, 0) / pts.length;
        const avgP99 = pts.reduce((s, p) => s + p.p99, 0) / pts.length;
        return `${ep}: avg p50=${avgP50.toFixed(0)}ms, p95=${avgP95.toFixed(0)}ms, p99=${avgP99.toFixed(0)}ms`;
      })
      .join(". ");
  }, [data]);

  return (
    <ChartContainer
      title="API Latency"
      subtitle="Response time percentiles over time per endpoint"
      loading={loading}
      error={error}
      empty={isEmpty}
      emptyMessage="No latency data"
      className={className}
    >
      <ResponsiveContainer width="100%" height={360}>
        <LineChart data={pivoted} margin={{ top: 8, right: 12, bottom: 4, left: 10 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#F3F4F6" />
          <XAxis
            dataKey="timestamp"
            tick={{ fontSize: 11, fill: "#57534E" }}
            axisLine={{ stroke: "#F3F4F6" }}
            tickLine={false}
          />
          <YAxis
            tick={{ fontSize: 11, fill: "#57534E" }}
            axisLine={false}
            tickLine={false}
            tickFormatter={(v: number) => `${v}ms`}
            label={{
              value: "Latency (ms)",
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
            formatter={(value: number, name: string) => [`${value.toFixed(1)}ms`, name]}
          />
          <Legend wrapperStyle={{ fontSize: 10, paddingTop: 8 }} />
          {endpoints.map((ep) =>
            (["p50", "p95", "p99"] as const).map((pct) => (
              <Line
                key={`${ep}_${pct}`}
                type="monotone"
                dataKey={`${ep}_${pct}`}
                stroke={colorMap[ep]}
                strokeWidth={PERCENTILE_STYLES[pct].strokeWidth}
                strokeDasharray={PERCENTILE_STYLES[pct].strokeDasharray}
                dot={false}
                name={`${ep} ${pct}`}
                opacity={pct === "p50" ? 1 : pct === "p95" ? 0.7 : 0.5}
              />
            )),
          )}
        </LineChart>
      </ResponsiveContainer>

      <details className="mt-3 text-xs text-text-secondary">
        <summary className="cursor-pointer font-medium">View as text</summary>
        <p className="mt-1">{textSummary}</p>
      </details>
    </ChartContainer>
  );
});

export default APILatency;
