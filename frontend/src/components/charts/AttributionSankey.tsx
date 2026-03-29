import { memo } from "react";
import { ResponsiveSankey } from "@nivo/sankey";
import { formatINR } from "@/utils/indian-formatting";

export interface SankeyNode {
  id: string;
  label?: string;
  color?: string;
}

export interface SankeyLink {
  source: string;
  target: string;
  value: number;
}

interface AttributionSankeyProps {
  nodes: SankeyNode[];
  links: SankeyLink[];
  className?: string;
}

const CATEGORY_COLORS: Record<string, string> = {
  "Signal Categories": "#F97316",
  "Agent Actions": "#2563EB",
  "Revenue Outcomes": "#059669",
};

export const AttributionSankey = memo(function AttributionSankey({
  nodes,
  links,
  className = "",
}: AttributionSankeyProps) {
  const data = {
    nodes: nodes.map((n) => ({ ...n, nodeColor: n.color ?? "#F97316" })),
    links,
  };

  return (
    <div className={`${className}`}>
      <div className="h-[400px]">
      <ResponsiveSankey
        data={data}
        margin={{ top: 16, right: 120, bottom: 16, left: 120 }}
        align="justify"
        colors={(node) => (node as { nodeColor?: string }).nodeColor ?? "#F97316"}
        nodeOpacity={1}
        nodeHoverOpacity={1}
        nodeThickness={18}
        nodeSpacing={16}
        nodeBorderWidth={0}
        nodeBorderRadius={4}
        linkOpacity={0.25}
        linkHoverOpacity={0.5}
        linkContract={2}
        linkBlendMode="normal"
        enableLinkGradient
        labelPosition="outside"
        labelOrientation="horizontal"
        labelPadding={12}
        labelTextColor={{ from: "color", modifiers: [["darker", 1.2]] }}
        nodeTooltip={({ node }) => (
          <div className="rounded-md border border-neutral-bg bg-surface-card px-3 py-2 shadow-lg">
            <p className="text-xs font-semibold text-text-primary">{node.label}</p>
            <p className="text-xs text-text-secondary">
              {formatINR(node.value, { compact: true })}
            </p>
          </div>
        )}
        linkTooltip={({ link }) => (
          <div className="rounded-md border border-neutral-bg bg-surface-card px-3 py-2 shadow-lg">
            <p className="text-xs text-text-primary">
              {link.source.label} → {link.target.label}
            </p>
            <p className="text-xs font-semibold text-text-secondary">
              {formatINR(link.value, { compact: true })}
            </p>
          </div>
        )}
      />
      </div>

      <details className="mt-3 text-xs text-text-secondary">
        <summary className="cursor-pointer font-medium">View as text</summary>
        <div className="mt-1 max-h-40 overflow-y-auto">
          <p>Nodes: {nodes.map((n) => n.label ?? n.id).join(", ")}.</p>
          {links.map((l, i) => (
            <p key={i}>
              {l.source} → {l.target}: {l.value.toLocaleString("en-IN")}
            </p>
          ))}
        </div>
      </details>
    </div>
  );
});
