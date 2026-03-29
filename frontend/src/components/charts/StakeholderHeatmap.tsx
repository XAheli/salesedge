import { memo } from "react";
import { ResponsiveHeatMap } from "@nivo/heatmap";

export interface StakeholderInteraction {
  stakeholder: string;
  email: number;
  call: number;
  meeting: number;
  demo: number;
}

interface StakeholderHeatmapProps {
  data: StakeholderInteraction[];
  className?: string;
}

export const StakeholderHeatmap = memo(function StakeholderHeatmap({
  data,
  className = "",
}: StakeholderHeatmapProps) {
  const nivoData = data.map((row) => ({
    id: row.stakeholder,
    data: [
      { x: "Email", y: row.email },
      { x: "Call", y: row.call },
      { x: "Meeting", y: row.meeting },
      { x: "Demo", y: row.demo },
    ],
  }));

  return (
    <div className={`${className}`}>
      <div className="h-[320px]">
      <ResponsiveHeatMap
        data={nivoData}
        margin={{ top: 40, right: 20, bottom: 20, left: 100 }}
        axisTop={{
          tickSize: 0,
          tickPadding: 8,
          tickRotation: 0,
        }}
        axisLeft={{
          tickSize: 0,
          tickPadding: 8,
          tickRotation: 0,
        }}
        colors={{
          type: "sequential",
          scheme: "oranges",
          minValue: 0,
        }}
        emptyColor="#F3F4F6"
        borderRadius={4}
        borderWidth={2}
        borderColor="#FFFFFF"
        labelTextColor={{ from: "color", modifiers: [["darker", 2.5]] }}
        hoverTarget="cell"
        tooltip={({ cell }) => (
          <div className="rounded-md border border-neutral-bg bg-surface-card px-3 py-2 shadow-lg">
            <p className="text-xs font-semibold text-text-primary">
              {cell.serieId} &middot; {cell.data.x}
            </p>
            <p className="text-xs text-text-secondary">
              {cell.data.y === 0
                ? "No interactions — coverage gap"
                : `${cell.data.y} interaction(s)`}
            </p>
          </div>
        )}
        animate
        motionConfig="gentle"
      />
      </div>

      <details className="mt-3 text-xs text-text-secondary">
        <summary className="cursor-pointer font-medium">View as text</summary>
        <div className="mt-1 max-h-40 overflow-y-auto">
          {data.map((row) => (
            <p key={row.stakeholder}>
              {row.stakeholder}: Email={row.email}, Call={row.call}, Meeting={row.meeting}, Demo={row.demo}
            </p>
          ))}
        </div>
      </details>
    </div>
  );
});
