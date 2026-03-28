import { memo, useMemo } from "react";
import {
  AreaChart,
  Area,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { formatINR } from "@/utils/indian-formatting";

export interface HistoricalPoint {
  date: string;
  revenue: number;
}

export interface ForecastPoint {
  date: string;
  p10: number;
  p50: number;
  p90: number;
}

interface RevenueForecastProps {
  historical: HistoricalPoint[];
  forecast: ForecastPoint[];
  className?: string;
}

function toCrores(v: number): string {
  return `₹${(v / 1_00_00_000).toFixed(1)}Cr`;
}

export const RevenueForecast = memo(function RevenueForecast({
  historical,
  forecast,
  className = "",
}: RevenueForecastProps) {
  const data = useMemo(() => {
    const hist = historical.map((h) => ({
      date: h.date,
      actual: h.revenue,
      p10: null as number | null,
      p50: null as number | null,
      p90: null as number | null,
    }));

    const bridgePoint = historical.length > 0
      ? {
          date: historical[historical.length - 1]!.date,
          actual: historical[historical.length - 1]!.revenue,
          p10: historical[historical.length - 1]!.revenue,
          p50: historical[historical.length - 1]!.revenue,
          p90: historical[historical.length - 1]!.revenue,
        }
      : null;

    const fore = forecast.map((f) => ({
      date: f.date,
      actual: null as number | null,
      p10: f.p10,
      p50: f.p50,
      p90: f.p90,
    }));

    return bridgePoint ? [...hist, bridgePoint, ...fore] : [...hist, ...fore];
  }, [historical, forecast]);

  return (
    <div className={className}>
      <ResponsiveContainer width="100%" height={320}>
        <AreaChart data={data} margin={{ top: 8, right: 12, bottom: 4, left: 8 }}>
          <defs>
            <linearGradient id="forecastCone" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#F97316" stopOpacity={0.15} />
              <stop offset="100%" stopColor="#F97316" stopOpacity={0.02} />
            </linearGradient>
            <linearGradient id="historicalFill" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#F97316" stopOpacity={0.2} />
              <stop offset="100%" stopColor="#F97316" stopOpacity={0} />
            </linearGradient>
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
            tickFormatter={toCrores}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: "#FFFFFF",
              border: "1px solid #F3F4F6",
              borderRadius: 8,
              fontSize: 12,
            }}
            formatter={(value: number | null, name: string) => {
              if (value === null) return ["-", name];
              return [toCrores(value), name === "actual" ? "Actual" : name.toUpperCase()];
            }}
          />

          <Area
            type="monotone"
            dataKey="p90"
            stroke="none"
            fill="url(#forecastCone)"
            connectNulls={false}
            isAnimationActive={false}
          />
          <Area
            type="monotone"
            dataKey="p10"
            stroke="none"
            fill="#FFFFFF"
            connectNulls={false}
            isAnimationActive={false}
          />

          <Area
            type="monotone"
            dataKey="actual"
            stroke="#F97316"
            strokeWidth={2}
            fill="url(#historicalFill)"
            dot={{ r: 2, fill: "#F97316" }}
            connectNulls={false}
          />

          <Line
            type="monotone"
            dataKey="p50"
            stroke="#F97316"
            strokeWidth={2}
            strokeDasharray="6 3"
            dot={false}
            connectNulls={false}
          />
          <Line
            type="monotone"
            dataKey="p90"
            stroke="#F97316"
            strokeWidth={1}
            strokeDasharray="3 3"
            dot={false}
            connectNulls={false}
            opacity={0.5}
          />
          <Line
            type="monotone"
            dataKey="p10"
            stroke="#F97316"
            strokeWidth={1}
            strokeDasharray="3 3"
            dot={false}
            connectNulls={false}
            opacity={0.5}
          />
        </AreaChart>
      </ResponsiveContainer>

      <div className="mt-2 flex items-center justify-center gap-4 text-[10px] text-text-tertiary">
        <span className="flex items-center gap-1">
          <span className="inline-block h-0.5 w-4 bg-primary-500" /> Actual
        </span>
        <span className="flex items-center gap-1">
          <span className="inline-block h-0.5 w-4 border-t-2 border-dashed border-primary-500" /> P50 Forecast
        </span>
        <span className="flex items-center gap-1">
          <span className="inline-block h-3 w-4 rounded-sm bg-primary-500/10" /> P10–P90 Range
        </span>
      </div>
    </div>
  );
});
