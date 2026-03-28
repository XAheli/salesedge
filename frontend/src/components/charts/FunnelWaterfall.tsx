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
  LabelList,
} from "recharts";

export interface FunnelStage {
  name: string;
  count: number;
  conversionRate: number;
}

interface FunnelWaterfallProps {
  stages: FunnelStage[];
  comparisonStages?: FunnelStage[];
  className?: string;
}

const GRADIENT_COLORS = [
  "#FDBA74", "#FB923C", "#F97316", "#EA580C", "#C2410C", "#9A3412", "#7C2D12",
];

function ConversionLabel({ x, y, width, index, stages }: {
  x: number;
  y: number;
  width: number;
  index: number;
  stages: FunnelStage[];
}) {
  if (index >= stages.length - 1) return null;
  const rate = stages[index + 1]?.conversionRate;
  if (rate === undefined) return null;

  return (
    <text
      x={x + width + 8}
      y={y + 10}
      fill="#A8A29E"
      fontSize={10}
      fontWeight={500}
    >
      {rate.toFixed(1)}%
    </text>
  );
}

export const FunnelWaterfall = memo(function FunnelWaterfall({
  stages,
  comparisonStages,
  className = "",
}: FunnelWaterfallProps) {
  const maxCount = useMemo(() => Math.max(...stages.map((s) => s.count)), [stages]);

  const data = useMemo(
    () =>
      stages.map((s, i) => ({
        name: s.name,
        count: s.count,
        comparison: comparisonStages?.[i]?.count,
        conversionRate: s.conversionRate,
      })),
    [stages, comparisonStages],
  );

  return (
    <div className={className}>
      <ResponsiveContainer width="100%" height={stages.length * 48 + 40}>
        <BarChart
          data={data}
          layout="vertical"
          margin={{ top: 4, right: 60, bottom: 4, left: 80 }}
        >
          <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#F3F4F6" />
          <XAxis type="number" hide />
          <YAxis
            dataKey="name"
            type="category"
            tick={{ fontSize: 12, fill: "#57534E" }}
            axisLine={false}
            tickLine={false}
            width={75}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: "#FFFFFF",
              border: "1px solid #F3F4F6",
              borderRadius: 8,
              fontSize: 12,
            }}
            formatter={(value: number, name: string) => [
              value.toLocaleString("en-IN"),
              name === "comparison" ? "Previous Period" : "Current",
            ]}
          />
          {comparisonStages && (
            <Bar
              dataKey="comparison"
              fill="#F3F4F6"
              radius={[0, 4, 4, 0]}
              barSize={16}
            />
          )}
          <Bar dataKey="count" radius={[0, 4, 4, 0]} barSize={20}>
            {data.map((_, idx) => (
              <Cell
                key={idx}
                fill={GRADIENT_COLORS[Math.min(idx, GRADIENT_COLORS.length - 1)]}
              />
            ))}
            <LabelList
              dataKey="count"
              position="right"
              formatter={(v: number) => v.toLocaleString("en-IN")}
              style={{ fontSize: 11, fill: "#1C1917", fontWeight: 500 }}
            />
          </Bar>
        </BarChart>
      </ResponsiveContainer>

      <div className="mt-2 flex flex-wrap items-center gap-4 px-2">
        {stages.slice(0, -1).map((s, i) => (
          <div key={s.name} className="flex items-center gap-1 text-[10px] text-text-tertiary">
            <span>{s.name}</span>
            <span className="text-text-secondary">→</span>
            <span className="font-medium text-text-primary">
              {stages[i + 1]?.conversionRate.toFixed(1)}%
            </span>
          </div>
        ))}
      </div>
    </div>
  );
});
