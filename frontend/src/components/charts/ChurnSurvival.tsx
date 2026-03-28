import { memo } from "react";
import {
  AreaChart,
  Area,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from "recharts";

export interface SurvivalPoint {
  day: number;
  probability: number;
  lower?: number;
  upper?: number;
}

interface ChurnSurvivalProps {
  data: SurvivalPoint[];
  medianSurvivalDays?: number;
  className?: string;
}

export const ChurnSurvival = memo(function ChurnSurvival({
  data,
  medianSurvivalDays,
  className = "",
}: ChurnSurvivalProps) {
  return (
    <div className={className}>
      <ResponsiveContainer width="100%" height={320}>
        <AreaChart data={data} margin={{ top: 8, right: 12, bottom: 20, left: 10 }}>
          <defs>
            <linearGradient id="survivalBand" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#059669" stopOpacity={0.15} />
              <stop offset="100%" stopColor="#059669" stopOpacity={0.02} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#F3F4F6" />
          <XAxis
            dataKey="day"
            type="number"
            tick={{ fontSize: 11, fill: "#57534E" }}
            axisLine={{ stroke: "#F3F4F6" }}
            tickLine={false}
            label={{
              value: "Days Since Risk Onset",
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
            tickFormatter={(v: number) => `${(v * 100).toFixed(0)}%`}
            label={{
              value: "Survival Probability",
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
              `${(value * 100).toFixed(1)}%`,
              name === "probability" ? "Survival" : name === "upper" ? "Upper CI" : "Lower CI",
            ]}
            labelFormatter={(day: number) => `Day ${day}`}
          />

          {data[0]?.upper !== undefined && (
            <>
              <Area
                type="stepAfter"
                dataKey="upper"
                stroke="none"
                fill="url(#survivalBand)"
                isAnimationActive={false}
              />
              <Area
                type="stepAfter"
                dataKey="lower"
                stroke="none"
                fill="#FFFFFF"
                isAnimationActive={false}
              />
            </>
          )}

          <Line
            type="stepAfter"
            dataKey="probability"
            stroke="#059669"
            strokeWidth={2}
            dot={false}
            name="Survival"
          />

          {medianSurvivalDays !== undefined && (
            <>
              <ReferenceLine
                y={0.5}
                stroke="#A8A29E"
                strokeDasharray="4 4"
                strokeWidth={1}
              />
              <ReferenceLine
                x={medianSurvivalDays}
                stroke="#F97316"
                strokeDasharray="4 4"
                strokeWidth={1}
                label={{
                  value: `Median: ${medianSurvivalDays}d`,
                  position: "top",
                  fill: "#F97316",
                  fontSize: 10,
                  fontWeight: 600,
                }}
              />
            </>
          )}
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
});
