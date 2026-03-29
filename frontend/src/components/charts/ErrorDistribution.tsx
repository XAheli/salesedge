import { memo, useMemo } from "react";
import {
  BarChart,
  Bar,
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from "recharts";
import { ChartContainer } from "./ChartContainer";

export interface ErrorBin {
  binStart: number;
  binEnd: number;
  count: number;
}

export interface QQPoint {
  theoretical: number;
  observed: number;
}

interface ErrorDistributionProps {
  histogram: ErrorBin[];
  qqPlot: QQPoint[];
  loading?: boolean;
  error?: string | null;
  className?: string;
}

export const ErrorDistribution = memo(function ErrorDistribution({
  histogram,
  qqPlot,
  loading,
  error,
  className = "",
}: ErrorDistributionProps) {
  const isEmpty = !loading && !error && histogram.length === 0 && qqPlot.length === 0;

  const histData = useMemo(
    () =>
      histogram.map((b) => ({
        label: `${b.binStart.toFixed(2)}`,
        midpoint: (b.binStart + b.binEnd) / 2,
        count: b.count,
      })),
    [histogram],
  );

  const stats = useMemo(() => {
    if (!histogram.length) return null;
    const totalCount = histogram.reduce((s, b) => s + b.count, 0);
    const mean =
      histogram.reduce((s, b) => s + ((b.binStart + b.binEnd) / 2) * b.count, 0) / totalCount;
    const variance =
      histogram.reduce(
        (s, b) => s + b.count * ((b.binStart + b.binEnd) / 2 - mean) ** 2,
        0,
      ) / totalCount;
    return { mean, std: Math.sqrt(variance), n: totalCount };
  }, [histogram]);

  const textSummary = useMemo(() => {
    if (!stats) return "No error distribution data available.";
    return `Error distribution (n=${stats.n}): Mean error = ${stats.mean.toFixed(4)}, Std dev = ${stats.std.toFixed(4)}. ${histogram.length} bins from ${histogram[0]?.binStart.toFixed(2)} to ${histogram[histogram.length - 1]?.binEnd.toFixed(2)}.`;
  }, [stats, histogram]);

  return (
    <ChartContainer
      title="Error Distribution"
      subtitle={
        stats
          ? `Mean: ${stats.mean.toFixed(4)} | Std: ${stats.std.toFixed(4)} | n=${stats.n}`
          : "Prediction error analysis"
      }
      loading={loading}
      error={error}
      empty={isEmpty}
      emptyMessage="No error distribution data"
      className={className}
    >
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        <div>
          <p className="mb-2 text-xs font-medium text-text-secondary">Error Histogram</p>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={histData} margin={{ top: 8, right: 12, bottom: 20, left: 10 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#F3F4F6" />
              <XAxis
                dataKey="label"
                tick={{ fontSize: 10, fill: "#57534E" }}
                axisLine={{ stroke: "#F3F4F6" }}
                tickLine={false}
                label={{
                  value: "Prediction Error",
                  position: "insideBottom",
                  offset: -10,
                  style: { fontSize: 10, fill: "#A8A29E" },
                }}
              />
              <YAxis
                tick={{ fontSize: 11, fill: "#57534E" }}
                axisLine={false}
                tickLine={false}
                label={{
                  value: "Count",
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
              />
              <ReferenceLine x={0} stroke="#A8A29E" strokeDasharray="4 4" />
              <Bar dataKey="count" fill="#F97316" fillOpacity={0.8} radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div>
          <p className="mb-2 text-xs font-medium text-text-secondary">Q-Q Plot</p>
          <ResponsiveContainer width="100%" height={260}>
            <ScatterChart margin={{ top: 8, right: 12, bottom: 20, left: 10 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#F3F4F6" />
              <XAxis
                dataKey="theoretical"
                type="number"
                tick={{ fontSize: 11, fill: "#57534E" }}
                axisLine={{ stroke: "#F3F4F6" }}
                tickLine={false}
                label={{
                  value: "Theoretical Quantiles",
                  position: "insideBottom",
                  offset: -10,
                  style: { fontSize: 10, fill: "#A8A29E" },
                }}
              />
              <YAxis
                dataKey="observed"
                type="number"
                tick={{ fontSize: 11, fill: "#57534E" }}
                axisLine={false}
                tickLine={false}
                label={{
                  value: "Observed Quantiles",
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
                formatter={(value: number, name: string) => [
                  value.toFixed(4),
                  name === "theoretical" ? "Theoretical" : "Observed",
                ]}
              />
              {qqPlot.length >= 2 && (
                <ReferenceLine
                  segment={[
                    { x: qqPlot[0]!.theoretical, y: qqPlot[0]!.theoretical },
                    {
                      x: qqPlot[qqPlot.length - 1]!.theoretical,
                      y: qqPlot[qqPlot.length - 1]!.theoretical,
                    },
                  ]}
                  stroke="#A8A29E"
                  strokeDasharray="6 3"
                />
              )}
              <Scatter data={qqPlot} fill="#059669" fillOpacity={0.7} r={3} />
            </ScatterChart>
          </ResponsiveContainer>
        </div>
      </div>

      <details className="mt-3 text-xs text-text-secondary">
        <summary className="cursor-pointer font-medium">View as text</summary>
        <p className="mt-1">{textSummary}</p>
      </details>
    </ChartContainer>
  );
});

export default ErrorDistribution;
