import { memo, useCallback } from "react";
import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ZAxis,
  Cell,
} from "recharts";
import { formatINR } from "@/utils/indian-formatting";

export interface DealBubble {
  id: string;
  name: string;
  value: number;
  riskScore: number;
  daysInStage: number;
  stage: string;
  riskFactors?: string[];
}

interface DealRiskScatterProps {
  deals: DealBubble[];
  onDealClick?: (deal: DealBubble) => void;
  className?: string;
}

function getRiskColor(risk: number): string {
  if (risk >= 0.7) return "#DC2626";
  if (risk >= 0.4) return "#D97706";
  return "#059669";
}

function CustomTooltip({ active, payload }: { active?: boolean; payload?: Array<{ payload: DealBubble }> }) {
  if (!active || !payload?.length) return null;
  const deal = payload[0]!.payload;

  return (
    <div className="rounded-md border border-neutral-bg bg-surface-card p-3 shadow-lg">
      <p className="text-sm font-semibold text-text-primary">{deal.name}</p>
      <div className="mt-1.5 space-y-0.5 text-xs text-text-secondary">
        <p>Value: {formatINR(deal.value, { compact: true })}</p>
        <p>Risk: {(deal.riskScore * 100).toFixed(0)}%</p>
        <p>Days in Stage: {deal.daysInStage}</p>
        <p>Stage: {deal.stage}</p>
        {deal.riskFactors?.length ? (
          <div className="mt-1 border-t border-neutral-bg pt-1">
            <p className="font-medium text-text-primary">Risk Factors:</p>
            <ul className="list-inside list-disc">
              {deal.riskFactors.map((f) => (
                <li key={f}>{f}</li>
              ))}
            </ul>
          </div>
        ) : null}
      </div>
    </div>
  );
}

export const DealRiskScatter = memo(function DealRiskScatter({
  deals,
  onDealClick,
  className = "",
}: DealRiskScatterProps) {
  const valueCr = (v: number) => `₹${(v / 1_00_00_000).toFixed(1)}Cr`;

  return (
    <div className={className}>
      <ResponsiveContainer width="100%" height={360}>
        <ScatterChart margin={{ top: 8, right: 20, bottom: 20, left: 10 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#F3F4F6" />
          <XAxis
            dataKey="value"
            type="number"
            name="Deal Value"
            tick={{ fontSize: 11, fill: "#57534E" }}
            axisLine={{ stroke: "#F3F4F6" }}
            tickLine={false}
            tickFormatter={valueCr}
            label={{
              value: "Deal Value (₹Cr)",
              position: "insideBottom",
              offset: -10,
              style: { fontSize: 10, fill: "#A8A29E" },
            }}
          />
          <YAxis
            dataKey="riskScore"
            type="number"
            name="Risk Score"
            domain={[0, 1]}
            tick={{ fontSize: 11, fill: "#57534E" }}
            axisLine={false}
            tickLine={false}
            tickFormatter={(v: number) => `${(v * 100).toFixed(0)}%`}
            label={{
              value: "Risk Score",
              angle: -90,
              position: "insideLeft",
              offset: 10,
              style: { fontSize: 10, fill: "#A8A29E" },
            }}
          />
          <ZAxis
            dataKey="daysInStage"
            type="number"
            range={[60, 400]}
            name="Days in Stage"
          />
          <Tooltip content={<CustomTooltip />} />
          <Scatter
            data={deals}
            onClick={(entry) => onDealClick?.(entry as unknown as DealBubble)}
            cursor={onDealClick ? "pointer" : undefined}
          >
            {deals.map((deal) => (
              <Cell
                key={deal.id}
                fill={getRiskColor(deal.riskScore)}
                fillOpacity={0.7}
                stroke={getRiskColor(deal.riskScore)}
                strokeWidth={1}
              />
            ))}
          </Scatter>
        </ScatterChart>
      </ResponsiveContainer>

      <div className="mt-2 flex items-center justify-center gap-4 text-[10px] text-text-tertiary">
        <span className="flex items-center gap-1">
          <span className="inline-block h-2.5 w-2.5 rounded-full bg-risk" /> High Risk
        </span>
        <span className="flex items-center gap-1">
          <span className="inline-block h-2.5 w-2.5 rounded-full bg-caution" /> Medium
        </span>
        <span className="flex items-center gap-1">
          <span className="inline-block h-2.5 w-2.5 rounded-full bg-revenue-positive" /> Healthy
        </span>
        <span className="text-text-tertiary">Bubble size = days in stage</span>
      </div>
    </div>
  );
});
