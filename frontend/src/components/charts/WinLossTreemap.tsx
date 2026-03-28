import { memo } from "react";
import { ResponsiveTreeMap } from "@nivo/treemap";

export interface WinLossReason {
  reason: string;
  count: number;
  outcome: "win" | "loss";
}

interface WinLossTreemapProps {
  data: WinLossReason[];
  className?: string;
}

export const WinLossTreemap = memo(function WinLossTreemap({
  data,
  className = "",
}: WinLossTreemapProps) {
  const treeData = {
    id: "root",
    children: [
      {
        id: "Wins",
        children: data
          .filter((d) => d.outcome === "win")
          .map((d) => ({
            id: d.reason,
            value: d.count,
            outcome: "win" as const,
          })),
      },
      {
        id: "Losses",
        children: data
          .filter((d) => d.outcome === "loss")
          .map((d) => ({
            id: d.reason,
            value: d.count,
            outcome: "loss" as const,
          })),
      },
    ],
  };

  return (
    <div className={`h-[360px] ${className}`}>
      <ResponsiveTreeMap
        data={treeData}
        identity="id"
        value="value"
        margin={{ top: 4, right: 4, bottom: 4, left: 4 }}
        tile="squarify"
        innerPadding={3}
        outerPadding={3}
        borderRadius={6}
        borderWidth={0}
        colors={(node) => {
          if (node.data.outcome === "win") return "#059669";
          if (node.data.outcome === "loss") return "#DC2626";
          const parent = node.pathComponents[1];
          return parent === "Wins" ? "#059669" : parent === "Losses" ? "#DC2626" : "#F3F4F6";
        }}
        nodeOpacity={0.85}
        labelSkipSize={40}
        label={(node) => `${node.id} (${node.formattedValue})`}
        labelTextColor="#FFFFFF"
        parentLabelPosition="top"
        parentLabelTextColor="#FFFFFF"
        tooltip={({ node }) => (
          <div className="rounded-md border border-neutral-bg bg-surface-card px-3 py-2 shadow-lg">
            <p className="text-xs font-semibold text-text-primary">{node.id}</p>
            <p className="text-xs text-text-secondary">Count: {node.formattedValue}</p>
          </div>
        )}
      />

      <div className="mt-2 flex items-center justify-center gap-4 text-[10px] text-text-tertiary">
        <span className="flex items-center gap-1">
          <span className="inline-block h-2.5 w-2.5 rounded bg-revenue-positive" /> Wins
        </span>
        <span className="flex items-center gap-1">
          <span className="inline-block h-2.5 w-2.5 rounded bg-risk" /> Losses
        </span>
      </div>
    </div>
  );
});
