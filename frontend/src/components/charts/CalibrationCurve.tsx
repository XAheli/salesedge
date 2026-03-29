import { memo, useMemo } from "react";
import {
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

export interface CalibrationPoint {
  predictedProbability: number;
  actualFrequency: number;
  binSize: number;
}

interface CalibrationCurveProps {
  data: CalibrationPoint[];
  modelName?: string;
  loading?: boolean;
  error?: string | null;
  className?: string;
}

function pctFmt(v: number): string {
  return `${(v * 100).toFixed(0)}%`;
}

export const CalibrationCurve = memo(function CalibrationCurve({
  data,
  modelName = "Model",
  loading,
  error,
  className = "",
}: CalibrationCurveProps) {
  const isEmpty = !loading && !error && data.length === 0;

  const brierScore = useMemo(() => {
    if (!data.length) return null;
    const totalSamples = data.reduce((s, d) => s + d.binSize, 0);
    if (totalSamples === 0) return null;
    return data.reduce(
      (s, d) =>
        s + (d.binSize / totalSamples) * (d.predictedProbability - d.actualFrequency) ** 2,
      0,
    );
  }, [data]);

  const textSummary = useMemo(() => {
    if (!data.length) return "No calibration data available.";
    const lines = data.map(
      (d) =>
        `Predicted ${pctFmt(d.predictedProbability)} → Actual ${pctFmt(d.actualFrequency)} (n=${d.binSize})`,
    );
    const brier = brierScore !== null ? ` Brier score: ${brierScore.toFixed(4)}.` : "";
    return lines.join("; ") + "." + brier;
  }, [data, brierScore]);

  return (
    <ChartContainer
      title="Calibration Curve"
      subtitle={`${modelName} — predicted probability vs actual frequency${brierScore !== null ? ` (Brier: ${brierScore.toFixed(4)})` : ""}`}
      loading={loading}
      error={error}
      empty={isEmpty}
      emptyMessage="No calibration data"
      className={className}
    >
      <ResponsiveContainer width="100%" height={360}>
        <ScatterChart margin={{ top: 8, right: 12, bottom: 20, left: 10 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#F3F4F6" />
          <XAxis
            dataKey="predictedProbability"
            type="number"
            domain={[0, 1]}
            tick={{ fontSize: 11, fill: "#57534E" }}
            axisLine={{ stroke: "#F3F4F6" }}
            tickLine={false}
            tickFormatter={pctFmt}
            label={{
              value: "Predicted Probability",
              position: "insideBottom",
              offset: -10,
              style: { fontSize: 10, fill: "#A8A29E" },
            }}
          />
          <YAxis
            dataKey="actualFrequency"
            type="number"
            domain={[0, 1]}
            tick={{ fontSize: 11, fill: "#57534E" }}
            axisLine={false}
            tickLine={false}
            tickFormatter={pctFmt}
            label={{
              value: "Actual Frequency",
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
              const labels: Record<string, string> = {
                predictedProbability: "Predicted",
                actualFrequency: "Actual",
              };
              return [pctFmt(value), labels[name] ?? name];
            }}
          />
          <ReferenceLine
            segment={[
              { x: 0, y: 0 },
              { x: 1, y: 1 },
            ]}
            stroke="#A8A29E"
            strokeDasharray="6 3"
            strokeWidth={1}
          />
          <Scatter
            data={data}
            fill="#F97316"
            stroke="#EA580C"
            strokeWidth={1}
            fillOpacity={0.8}
            line={{ stroke: "#F97316", strokeWidth: 2 }}
            lineType="joint"
          />
        </ScatterChart>
      </ResponsiveContainer>

      <div className="mt-2 flex items-center justify-center gap-4 text-[10px] text-text-tertiary">
        <span className="flex items-center gap-1">
          <span className="inline-block h-2.5 w-2.5 rounded-full bg-primary-500" /> {modelName}
        </span>
        <span className="flex items-center gap-1">
          <span className="inline-block h-px w-4 border-t border-dashed border-text-tertiary" /> Perfect Calibration
        </span>
      </div>

      <details className="mt-3 text-xs text-text-secondary">
        <summary className="cursor-pointer font-medium">View as text</summary>
        <p className="mt-1">{textSummary}</p>
      </details>
    </ChartContainer>
  );
});

export default CalibrationCurve;
