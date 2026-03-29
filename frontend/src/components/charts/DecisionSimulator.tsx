import { memo, useMemo, useState, useCallback } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
  Legend,
  ReferenceLine,
} from "recharts";
import { ChartContainer } from "./ChartContainer";

export interface Scenario {
  id: string;
  name: string;
  predictedRevenue: number;
  predictedWinRate: number;
  predictedDealCycle: number;
  riskScore: number;
  actions: string[];
}

interface DecisionSimulatorProps {
  scenarios: Scenario[];
  baselineScenarioId?: string;
  loading?: boolean;
  error?: string | null;
  className?: string;
}

type Metric = "predictedRevenue" | "predictedWinRate" | "predictedDealCycle" | "riskScore";

const METRIC_CONFIG: Record<Metric, { label: string; fmt: (v: number) => string; color: string }> = {
  predictedRevenue: {
    label: "Predicted Revenue (₹Cr)",
    fmt: (v) => `₹${(v / 1_00_00_000).toFixed(1)}Cr`,
    color: "#F97316",
  },
  predictedWinRate: {
    label: "Win Rate (%)",
    fmt: (v) => `${v.toFixed(1)}%`,
    color: "#059669",
  },
  predictedDealCycle: {
    label: "Deal Cycle (days)",
    fmt: (v) => `${v.toFixed(0)}d`,
    color: "#2563EB",
  },
  riskScore: {
    label: "Risk Score",
    fmt: (v) => v.toFixed(1),
    color: "#DC2626",
  },
};

function getBarColor(metric: Metric, value: number, baselineValue: number | null): string {
  if (baselineValue === null) return METRIC_CONFIG[metric].color;
  const better =
    metric === "riskScore" || metric === "predictedDealCycle"
      ? value < baselineValue
      : value > baselineValue;
  return better ? "#059669" : "#DC2626";
}

export const DecisionSimulator = memo(function DecisionSimulator({
  scenarios,
  baselineScenarioId,
  loading,
  error,
  className = "",
}: DecisionSimulatorProps) {
  const isEmpty = !loading && !error && scenarios.length === 0;
  const [activeMetric, setActiveMetric] = useState<Metric>("predictedRevenue");

  const baseline = useMemo(
    () => (baselineScenarioId ? scenarios.find((s) => s.id === baselineScenarioId) : null),
    [scenarios, baselineScenarioId],
  );

  const chartData = useMemo(
    () =>
      scenarios.map((s) => ({
        name: s.name,
        value: s[activeMetric],
        id: s.id,
        isBaseline: s.id === baselineScenarioId,
      })),
    [scenarios, activeMetric, baselineScenarioId],
  );

  const handleMetricChange = useCallback((e: React.ChangeEvent<HTMLSelectElement>) => {
    setActiveMetric(e.target.value as Metric);
  }, []);

  const cfg = METRIC_CONFIG[activeMetric];

  const textSummary = useMemo(() => {
    if (!scenarios.length) return "No scenario data available.";
    return scenarios
      .map((s) => {
        const acts = s.actions.length ? ` (Actions: ${s.actions.join(", ")})` : "";
        return `${s.name}: Rev ${METRIC_CONFIG.predictedRevenue.fmt(s.predictedRevenue)}, Win ${METRIC_CONFIG.predictedWinRate.fmt(s.predictedWinRate)}, Cycle ${METRIC_CONFIG.predictedDealCycle.fmt(s.predictedDealCycle)}, Risk ${METRIC_CONFIG.riskScore.fmt(s.riskScore)}${acts}`;
      })
      .join(". ");
  }, [scenarios]);

  return (
    <ChartContainer
      title="Decision Simulator"
      subtitle="Paper-trade scenario comparison — what-if analysis"
      loading={loading}
      error={error}
      empty={isEmpty}
      emptyMessage="No scenarios to compare"
      className={className}
    >
      <div className="mb-3 flex items-center gap-3 px-1">
        <label htmlFor="sim-metric" className="text-xs font-medium text-text-secondary">
          Metric:
        </label>
        <select
          id="sim-metric"
          value={activeMetric}
          onChange={handleMetricChange}
          className="rounded-md border border-neutral-bg bg-surface-card px-2 py-1 text-xs text-text-primary"
        >
          {(Object.keys(METRIC_CONFIG) as Metric[]).map((k) => (
            <option key={k} value={k}>
              {METRIC_CONFIG[k].label}
            </option>
          ))}
        </select>
      </div>

      <ResponsiveContainer width="100%" height={Math.max(200, scenarios.length * 52 + 40)}>
        <BarChart
          data={chartData}
          layout="vertical"
          margin={{ top: 4, right: 60, bottom: 4, left: 100 }}
        >
          <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#F3F4F6" />
          <XAxis
            type="number"
            tick={{ fontSize: 11, fill: "#57534E" }}
            axisLine={{ stroke: "#F3F4F6" }}
            tickLine={false}
            tickFormatter={cfg.fmt}
          />
          <YAxis
            dataKey="name"
            type="category"
            tick={{ fontSize: 11, fill: "#57534E" }}
            axisLine={false}
            tickLine={false}
            width={95}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: "#FFFFFF",
              border: "1px solid #F3F4F6",
              borderRadius: 8,
              fontSize: 12,
            }}
            formatter={(value: number) => [cfg.fmt(value), cfg.label]}
          />
          {baseline && (
            <ReferenceLine
              x={baseline[activeMetric]}
              stroke="#A8A29E"
              strokeDasharray="6 3"
              label={{
                value: "Baseline",
                position: "top",
                fill: "#A8A29E",
                fontSize: 10,
              }}
            />
          )}
          <Bar dataKey="value" radius={[0, 4, 4, 0]} barSize={24}>
            {chartData.map((d, i) => (
              <Cell
                key={i}
                fill={getBarColor(activeMetric, d.value, baseline ? baseline[activeMetric] : null)}
                fillOpacity={d.isBaseline ? 0.5 : 0.85}
                stroke={d.isBaseline ? "#A8A29E" : undefined}
                strokeWidth={d.isBaseline ? 1.5 : 0}
                strokeDasharray={d.isBaseline ? "4 2" : undefined}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>

      <div className="mt-3 space-y-2 px-1">
        {scenarios.map((s) => (
          <div key={s.id} className="flex items-start gap-2 text-xs text-text-secondary">
            <span className="font-medium text-text-primary">{s.name}:</span>
            <span>{s.actions.join(", ") || "No actions"}</span>
          </div>
        ))}
      </div>

      <details className="mt-3 text-xs text-text-secondary">
        <summary className="cursor-pointer font-medium">View as text</summary>
        <p className="mt-1">{textSummary}</p>
      </details>
    </ChartContainer>
  );
});

export default DecisionSimulator;
