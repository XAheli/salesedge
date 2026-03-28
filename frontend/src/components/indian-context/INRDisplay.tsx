import { memo, useMemo } from "react";
import { formatINR, toIndianUnits } from "@/utils/indian-formatting";

interface INRDisplayProps {
  value: number;
  compact?: boolean;
  decimals?: number;
  showSymbol?: boolean;
  size?: "sm" | "md" | "lg";
  className?: string;
}

const SIZE_MAP = {
  sm: "text-sm",
  md: "text-base",
  lg: "text-xl font-display font-bold",
};

export const INRDisplay = memo(function INRDisplay({
  value,
  compact = false,
  decimals = 2,
  showSymbol = true,
  size = "md",
  className = "",
}: INRDisplayProps) {
  const formatted = useMemo(
    () => formatINR(value, { compact, decimals, showSymbol }),
    [value, compact, decimals, showSymbol],
  );

  const { unit } = useMemo(() => toIndianUnits(value), [value]);

  return (
    <span className={`tabular-nums ${SIZE_MAP[size]} ${className}`} title={formatINR(value)}>
      {formatted}
    </span>
  );
});
