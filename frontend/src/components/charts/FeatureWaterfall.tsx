import { memo, useMemo } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
  ReferenceLine,
} from "recharts";

export interface FeatureContribution {
  feature: string;
  contribution: number;
}

interface FeatureWaterfallProps {
  features: FeatureContribution[];
  baseValue: number;
  finalScore: number;
  className?: string;
}

export const FeatureWaterfall = memo(function FeatureWaterfall({
  features,
  baseValue,
  finalScore,
  className = "",
}: FeatureWaterfallProps) {
  const data = useMemo(() => {
    const sorted = [...features].sort(
      (a, b) => Math.abs(b.contribution) - Math.abs(a.contribution),
    );

    let running = baseValue;
    return sorted.map((f) => {
      const start = running;
      running += f.contribution;
      return {
        feature: f.feature,
        contribution: f.contribution,
        start: Math.min(start, running),
        end: Math.max(start, running),
        fill: f.contribution >= 0 ? "#059669" : "#DC2626",
      };
    });
  }, [features, baseValue]);

  return (
    <div className={className}>
      <div className="mb-3 flex items-center justify-between px-1 text-xs text-text-secondary">
        <span>
          Base: <span className="font-semibold text-text-primary">{baseValue.toFixed(2)}</span>
        </span>
        <span>
          Final: <span className="font-semibold text-text-primary">{finalScore.toFixed(2)}</span>
        </span>
      </div>

      <ResponsiveContainer width="100%" height={Math.max(200, data.length * 36 + 40)}>
        <BarChart
          data={data}
          layout="vertical"
          margin={{ top: 4, right: 40, bottom: 4, left: 120 }}
        >
          <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#F3F4F6" />
          <XAxis type="number" hide />
          <YAxis
            dataKey="feature"
            type="category"
            tick={{ fontSize: 11, fill: "#57534E" }}
            axisLine={false}
            tickLine={false}
            width={115}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: "#FFFFFF",
              border: "1px solid #F3F4F6",
              borderRadius: 8,
              fontSize: 12,
            }}
            formatter={(value: number, name: string) => [
              `${value >= 0 ? "+" : ""}${value.toFixed(3)}`,
              "Contribution",
            ]}
          />

          <Bar dataKey="start" stackId="waterfall" fill="transparent" isAnimationActive={false} />

          <Bar dataKey="contribution" stackId="waterfall" radius={[0, 4, 4, 0]} barSize={18}>
            {data.map((d, i) => (
              <Cell key={i} fill={d.fill} fillOpacity={0.85} />
            ))}
          </Bar>

          <ReferenceLine x={baseValue} stroke="#A8A29E" strokeDasharray="4 4" />
        </BarChart>
      </ResponsiveContainer>

      <div className="mt-2 flex items-center justify-center gap-4 text-[10px] text-text-tertiary">
        <span className="flex items-center gap-1">
          <span className="inline-block h-2.5 w-4 rounded bg-revenue-positive/85" /> Positive
        </span>
        <span className="flex items-center gap-1">
          <span className="inline-block h-2.5 w-4 rounded bg-risk/85" /> Negative
        </span>
        <span className="flex items-center gap-1">
          <span className="inline-block h-px w-4 border-t border-dashed border-text-tertiary" /> Base
        </span>
      </div>
    </div>
  );
});
