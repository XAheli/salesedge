import { memo, useMemo, useState, useCallback } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceDot,
} from "recharts";
import { ChartContainer } from "./ChartContainer";

export interface PRPoint {
  threshold: number;
  precision: number;
  recall: number;
  f1?: number;
}

interface PrecisionRecallProps {
  data: PRPoint[];
  loading?: boolean;
  error?: string | null;
  className?: string;
}

function pctFmt(v: number): string {
  return `${(v * 100).toFixed(0)}%`;
}

export const PrecisionRecall = memo(function PrecisionRecall({
  data,
  loading,
  error,
  className = "",
}: PrecisionRecallProps) {
  const isEmpty = !loading && !error && data.length === 0;
  const sorted = useMemo(() => [...data].sort((a, b) => a.recall - b.recall), [data]);

  const [threshold, setThreshold] = useState(0.5);

  const selectedPoint = useMemo(() => {
    if (!sorted.length) return null;
    return sorted.reduce((best, pt) =>
      Math.abs(pt.threshold - threshold) < Math.abs(best.threshold - threshold) ? pt : best,
    );
  }, [sorted, threshold]);

  const handleSlider = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    setThreshold(parseFloat(e.target.value));
  }, []);

  const auc = useMemo(() => {
    if (sorted.length < 2) return null;
    let area = 0;
    for (let i = 1; i < sorted.length; i++) {
      const dx = sorted[i]!.recall - sorted[i - 1]!.recall;
      const avgY = (sorted[i]!.precision + sorted[i - 1]!.precision) / 2;
      area += dx * avgY;
    }
    return Math.abs(area);
  }, [sorted]);

  const textSummary = useMemo(() => {
    if (!sorted.length) return "No precision-recall data available.";
    const aucStr = auc !== null ? `AUC-PR: ${auc.toFixed(4)}. ` : "";
    const sel = selectedPoint
      ? `At threshold ${selectedPoint.threshold.toFixed(2)}: Precision ${pctFmt(selectedPoint.precision)}, Recall ${pctFmt(selectedPoint.recall)}.`
      : "";
    return `${aucStr}${sel} ${sorted.length} data points.`;
  }, [sorted, auc, selectedPoint]);

  return (
    <ChartContainer
      title="Precision-Recall Curve"
      subtitle={auc !== null ? `AUC-PR: ${auc.toFixed(4)}` : undefined}
      loading={loading}
      error={error}
      empty={isEmpty}
      emptyMessage="No precision-recall data"
      className={className}
    >
      <ResponsiveContainer width="100%" height={320}>
        <LineChart data={sorted} margin={{ top: 8, right: 12, bottom: 20, left: 10 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#F3F4F6" />
          <XAxis
            dataKey="recall"
            type="number"
            domain={[0, 1]}
            tick={{ fontSize: 11, fill: "#57534E" }}
            axisLine={{ stroke: "#F3F4F6" }}
            tickLine={false}
            tickFormatter={pctFmt}
            label={{
              value: "Recall",
              position: "insideBottom",
              offset: -10,
              style: { fontSize: 10, fill: "#A8A29E" },
            }}
          />
          <YAxis
            domain={[0, 1]}
            tick={{ fontSize: 11, fill: "#57534E" }}
            axisLine={false}
            tickLine={false}
            tickFormatter={pctFmt}
            label={{
              value: "Precision",
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
              pctFmt(value),
              name === "precision" ? "Precision" : name === "f1" ? "F1" : name,
            ]}
            labelFormatter={(recall: number) => `Recall: ${pctFmt(recall)}`}
          />
          <Line
            type="monotone"
            dataKey="precision"
            stroke="#F97316"
            strokeWidth={2}
            dot={false}
            activeDot={{ r: 4 }}
          />
          {sorted.some((d) => d.f1 !== undefined) && (
            <Line
              type="monotone"
              dataKey="f1"
              stroke="#7C3AED"
              strokeWidth={1.5}
              strokeDasharray="4 2"
              dot={false}
            />
          )}
          {selectedPoint && (
            <ReferenceDot
              x={selectedPoint.recall}
              y={selectedPoint.precision}
              r={6}
              fill="#F97316"
              stroke="#FFFFFF"
              strokeWidth={2}
            />
          )}
        </LineChart>
      </ResponsiveContainer>

      <div className="mt-3 px-2">
        <div className="flex items-center gap-3">
          <label className="text-xs font-medium text-text-secondary" htmlFor="pr-threshold">
            Threshold: {threshold.toFixed(2)}
          </label>
          <input
            id="pr-threshold"
            type="range"
            min={0}
            max={1}
            step={0.01}
            value={threshold}
            onChange={handleSlider}
            className="h-1.5 flex-1 cursor-pointer appearance-none rounded-full bg-neutral-bg accent-primary-500"
          />
        </div>
        {selectedPoint && (
          <div className="mt-1.5 flex gap-4 text-xs text-text-secondary">
            <span>Precision: <span className="font-semibold text-text-primary">{pctFmt(selectedPoint.precision)}</span></span>
            <span>Recall: <span className="font-semibold text-text-primary">{pctFmt(selectedPoint.recall)}</span></span>
            {selectedPoint.f1 !== undefined && (
              <span>F1: <span className="font-semibold text-text-primary">{pctFmt(selectedPoint.f1)}</span></span>
            )}
          </div>
        )}
      </div>

      <div className="mt-2 flex items-center justify-center gap-4 text-[10px] text-text-tertiary">
        <span className="flex items-center gap-1">
          <span className="inline-block h-0.5 w-4 bg-primary-500" /> PR Curve
        </span>
        {sorted.some((d) => d.f1 !== undefined) && (
          <span className="flex items-center gap-1">
            <span className="inline-block h-0.5 w-4 border-t-2 border-dashed border-[#7C3AED]" /> F1
          </span>
        )}
      </div>

      <details className="mt-3 text-xs text-text-secondary">
        <summary className="cursor-pointer font-medium">View as text</summary>
        <p className="mt-1">{textSummary}</p>
      </details>
    </ChartContainer>
  );
});

export default PrecisionRecall;
