import { memo, useMemo } from "react";
import { formatIST } from "@/utils/indian-formatting";

interface ISTTimestampProps {
  date: string | Date;
  format?: "full" | "date" | "time" | "datetime";
  className?: string;
}

export const ISTTimestamp = memo(function ISTTimestamp({
  date,
  format = "datetime",
  className = "",
}: ISTTimestampProps) {
  const formatted = useMemo(() => formatIST(date, format), [date, format]);

  const isoString = useMemo(() => {
    const d = typeof date === "string" ? new Date(date) : date;
    return d.toISOString();
  }, [date]);

  return (
    <time dateTime={isoString} className={`tabular-nums text-sm text-text-secondary ${className}`}>
      {formatted}
    </time>
  );
});
