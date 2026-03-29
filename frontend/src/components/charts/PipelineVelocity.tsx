import { memo } from "react";
import {
  ComposedChart,
  Line,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from "recharts";

export interface VelocityDataPoint {
  week: string;
  avgDaysInStage: number;
  throughput: number;
  rollingMeanDays?: number;
  upperControlLimit?: number;
  lowerControlLimit?: number;
}

interface PipelineVelocityProps {
  data: VelocityDataPoint[];
  className?: string;
}

export const PipelineVelocity = memo(function PipelineVelocity({
  data,
  className = "",
}: PipelineVelocityProps) {
  const hasControlLimits = data.some((d) => d.upperControlLimit !== undefined);

  return (
    <div className={className}>
      <ResponsiveContainer width="100%" height={320}>
        <ComposedChart data={data} margin={{ top: 8, right: 12, bottom: 4, left: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#F3F4F6" />
          <XAxis
            dataKey="week"
            tick={{ fontSize: 11, fill: "#57534E" }}
            axisLine={{ stroke: "#F3F4F6" }}
            tickLine={false}
          />
          <YAxis
            yAxisId="days"
            orientation="left"
            tick={{ fontSize: 11, fill: "#57534E" }}
            axisLine={false}
            tickLine={false}
            label={{
              value: "Avg Days",
              angle: -90,
              position: "insideLeft",
              offset: 10,
              style: { fontSize: 10, fill: "#A8A29E" },
            }}
          />
          <YAxis
            yAxisId="throughput"
            orientation="right"
            tick={{ fontSize: 11, fill: "#57534E" }}
            axisLine={false}
            tickLine={false}
            label={{
              value: "Deals Moved",
              angle: 90,
              position: "insideRight",
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
          <Bar
            yAxisId="throughput"
            dataKey="throughput"
            fill="#F97316"
            opacity={0.3}
            radius={[4, 4, 0, 0]}
            barSize={24}
            name="Deals Moved"
          />
          <Line
            yAxisId="days"
            type="monotone"
            dataKey="avgDaysInStage"
            stroke="#F97316"
            strokeWidth={2}
            dot={{ r: 3, fill: "#F97316" }}
            activeDot={{ r: 5 }}
            name="Avg Days in Stage"
          />
          {hasControlLimits && (
            <>
              <Line
                yAxisId="days"
                type="monotone"
                dataKey="upperControlLimit"
                stroke="#DC2626"
                strokeWidth={1}
                strokeDasharray="6 3"
                dot={false}
                name="Upper Limit"
              />
              <Line
                yAxisId="days"
                type="monotone"
                dataKey="lowerControlLimit"
                stroke="#059669"
                strokeWidth={1}
                strokeDasharray="6 3"
                dot={false}
                name="Lower Limit"
              />
            </>
          )}
          {data.some((d) => d.rollingMeanDays !== undefined) && (
            <Line
              yAxisId="days"
              type="monotone"
              dataKey="rollingMeanDays"
              stroke="#7C3AED"
              strokeWidth={1.5}
              strokeDasharray="4 2"
              dot={false}
              name="Rolling Mean"
            />
          )}
        </ComposedChart>
      </ResponsiveContainer>

      <details className="mt-3 text-xs text-text-secondary">
        <summary className="cursor-pointer font-medium">View as text</summary>
        <div className="mt-1 max-h-40 overflow-y-auto">
          {data.map((d) => (
            <p key={d.week}>
              {d.week}: {d.avgDaysInStage}d avg, {d.throughput} deals moved
              {d.rollingMeanDays !== undefined ? `, rolling mean ${d.rollingMeanDays}d` : ""}
            </p>
          ))}
        </div>
      </details>
    </div>
  );
});
