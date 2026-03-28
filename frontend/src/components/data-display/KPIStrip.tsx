import { memo } from "react";
import { KPICard, type KPICardProps } from "./KPICard";

interface KPIStripProps {
  kpis: KPICardProps[];
  className?: string;
}

export const KPIStrip = memo(function KPIStrip({ kpis, className = "" }: KPIStripProps) {
  return (
    <div
      className={`grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4 ${className}`}
    >
      {kpis.map((kpi, idx) => (
        <KPICard key={kpi.title + idx} {...kpi} />
      ))}
    </div>
  );
});
