import { memo, useMemo } from "react";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

const CHART_PALETTE = [
  "#F97316", "#059669", "#7C3AED", "#2563EB",
  "#DC2626", "#D97706", "#0891B2", "#BE185D",
];

export interface CompetitorDataPoint {
  date: string;
  [competitor: string]: string | number;
}

interface CompetitiveTrendProps {
  data: CompetitorDataPoint[];
  competitors: string[];
  className?: string;
}

export const CompetitiveTrend = memo(function CompetitiveTrend({
  data,
  competitors,
  className = "",
}: CompetitiveTrendProps) {
  const colorMap = useMemo(
    () =>
      Object.fromEntries(
        competitors.map((c, i) => [c, CHART_PALETTE[i % CHART_PALETTE.length]]),
      ),
    [competitors],
  );

  return (
    <div className={className}>
      <ResponsiveContainer width="100%" height={320}>
        <AreaChart data={data} margin={{ top: 8, right: 12, bottom: 4, left: 0 }}>
          <defs>
            {competitors.map((c) => (
              <linearGradient key={c} id={`compGrad-${c}`} x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor={colorMap[c]} stopOpacity={0.2} />
                <stop offset="100%" stopColor={colorMap[c]} stopOpacity={0} />
              </linearGradient>
            ))}
          </defs>
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
              value: "Mentions",
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
          {competitors.map((c) => (
            <Area
              key={c}
              type="monotone"
              dataKey={c}
              stroke={colorMap[c]}
              strokeWidth={2}
              fill={`url(#compGrad-${c})`}
              dot={false}
              activeDot={{ r: 4 }}
              name={c}
            />
          ))}
        </AreaChart>
      </ResponsiveContainer>

      <div className="mt-2 flex flex-wrap items-center justify-center gap-3 text-[10px]">
        {competitors.map((c) => (
          <span key={c} className="flex items-center gap-1 text-text-tertiary">
            <span
              className="inline-block h-2 w-2 rounded-full"
              style={{ backgroundColor: colorMap[c] }}
            />
            {c}
          </span>
        ))}
      </div>
    </div>
  );
});
