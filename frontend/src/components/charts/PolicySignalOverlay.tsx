import { memo } from "react";
import {
  ComposedChart,
  Line,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceArea,
  ReferenceLine,
} from "recharts";

export interface SignalDataPoint {
  date: string;
  [key: string]: string | number | undefined;
}

export interface PolicyMarker {
  date: string;
  label: string;
  type: "RBI" | "SEBI" | "Budget" | "other";
}

export interface PolicyPeriod {
  startDate: string;
  endDate: string;
  label: string;
  color?: string;
}

interface PolicySignalOverlayProps {
  data: SignalDataPoint[];
  series: Array<{
    key: string;
    label: string;
    yAxisId: string;
    color: string;
    type?: "line" | "area";
  }>;
  markers?: PolicyMarker[];
  periods?: PolicyPeriod[];
  className?: string;
}

const MARKER_COLORS: Record<PolicyMarker["type"], string> = {
  RBI: "#2563EB",
  SEBI: "#7C3AED",
  Budget: "#F97316",
  other: "#6B7280",
};

export const PolicySignalOverlay = memo(function PolicySignalOverlay({
  data,
  series,
  markers = [],
  periods = [],
  className = "",
}: PolicySignalOverlayProps) {
  const yAxisIds = [...new Set(series.map((s) => s.yAxisId))];

  return (
    <div className={className}>
      <ResponsiveContainer width="100%" height={360}>
        <ComposedChart data={data} margin={{ top: 8, right: 16, bottom: 4, left: 8 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#F3F4F6" />
          <XAxis
            dataKey="date"
            tick={{ fontSize: 11, fill: "#57534E" }}
            axisLine={{ stroke: "#F3F4F6" }}
            tickLine={false}
          />

          {yAxisIds.map((id, idx) => (
            <YAxis
              key={id}
              yAxisId={id}
              orientation={idx === 0 ? "left" : "right"}
              tick={{ fontSize: 11, fill: "#57534E" }}
              axisLine={false}
              tickLine={false}
            />
          ))}

          <Tooltip
            contentStyle={{
              backgroundColor: "#FFFFFF",
              border: "1px solid #F3F4F6",
              borderRadius: 8,
              fontSize: 12,
            }}
          />

          {periods.map((p, i) => (
            <ReferenceArea
              key={i}
              x1={p.startDate}
              x2={p.endDate}
              fill={p.color ?? "#F3F4F6"}
              fillOpacity={0.3}
              label={{
                value: p.label,
                position: "insideTopLeft",
                fill: "#57534E",
                fontSize: 9,
              }}
            />
          ))}

          {markers.map((m, i) => (
            <ReferenceLine
              key={i}
              x={m.date}
              stroke={MARKER_COLORS[m.type]}
              strokeDasharray="4 2"
              strokeWidth={1.5}
              label={{
                value: m.label,
                position: "top",
                fill: MARKER_COLORS[m.type],
                fontSize: 9,
                fontWeight: 600,
              }}
            />
          ))}

          {series.map((s) =>
            s.type === "area" ? (
              <Area
                key={s.key}
                yAxisId={s.yAxisId}
                type="monotone"
                dataKey={s.key}
                stroke={s.color}
                fill={s.color}
                fillOpacity={0.1}
                strokeWidth={2}
                dot={false}
                name={s.label}
              />
            ) : (
              <Line
                key={s.key}
                yAxisId={s.yAxisId}
                type="monotone"
                dataKey={s.key}
                stroke={s.color}
                strokeWidth={2}
                dot={false}
                name={s.label}
              />
            ),
          )}
        </ComposedChart>
      </ResponsiveContainer>

      <div className="mt-2 flex flex-wrap items-center justify-center gap-3 text-[10px]">
        {series.map((s) => (
          <span key={s.key} className="flex items-center gap-1 text-text-tertiary">
            <span
              className="inline-block h-0.5 w-4 rounded"
              style={{ backgroundColor: s.color }}
            />
            {s.label}
          </span>
        ))}
        {markers.length > 0 && (
          <>
            <span className="mx-1 h-3 w-px bg-neutral-bg" />
            {[...new Set(markers.map((m) => m.type))].map((type) => (
              <span key={type} className="flex items-center gap-1 text-text-tertiary">
                <span
                  className="inline-block h-3 w-0.5 rounded"
                  style={{ backgroundColor: MARKER_COLORS[type] }}
                />
                {type}
              </span>
            ))}
          </>
        )}
      </div>
    </div>
  );
});
