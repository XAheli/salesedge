import { memo, useMemo } from "react";
import { getCurrentFY } from "@/utils/indian-formatting";

interface FYSelectorProps {
  value?: string;
  onChange: (fy: string) => void;
  startYear?: number;
  className?: string;
}

function generateFYOptions(startYear: number): string[] {
  const now = new Date();
  const currentEndYear = now.getMonth() >= 3 ? now.getFullYear() + 1 : now.getFullYear();
  const options: string[] = [];

  for (let endYr = currentEndYear; endYr > startYear; endYr--) {
    const startYr = endYr - 1;
    const s = startYr.toString().slice(-2);
    const e = endYr.toString().slice(-2);
    options.push(`FY ${s}-${e}`);
  }

  return options;
}

export const FYSelector = memo(function FYSelector({
  value,
  onChange,
  startYear = 2020,
  className = "",
}: FYSelectorProps) {
  const options = useMemo(() => generateFYOptions(startYear), [startYear]);
  const currentFY = useMemo(() => getCurrentFY(), []);

  return (
    <select
      value={value ?? currentFY}
      onChange={(e) => onChange(e.target.value)}
      className={`h-9 rounded-md border border-neutral-bg bg-surface-card px-3 pr-8 text-sm text-text-primary transition-colors hover:border-primary-300 focus:border-primary-400 focus:outline-none ${className}`}
    >
      {options.map((fy) => (
        <option key={fy} value={fy}>
          {fy}
          {fy === currentFY ? " (Current)" : ""}
        </option>
      ))}
    </select>
  );
});
