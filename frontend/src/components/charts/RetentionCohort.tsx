import { memo, useMemo } from "react";

export interface CohortRow {
  cohort: string;
  values: number[];
}

interface RetentionCohortProps {
  data: CohortRow[];
  className?: string;
}

function retentionColor(pct: number): string {
  if (pct >= 90) return "bg-revenue-positive text-white";
  if (pct >= 70) return "bg-revenue-positive/70 text-white";
  if (pct >= 50) return "bg-caution/60 text-white";
  if (pct >= 30) return "bg-caution/40 text-text-primary";
  if (pct >= 10) return "bg-risk/30 text-text-primary";
  return "bg-risk/60 text-white";
}

export const RetentionCohort = memo(function RetentionCohort({
  data,
  className = "",
}: RetentionCohortProps) {
  const maxMonths = useMemo(
    () => Math.max(...data.map((r) => r.values.length)),
    [data],
  );

  return (
    <div className={`overflow-x-auto ${className}`}>
      <details className="mb-3 text-xs text-text-secondary">
        <summary className="cursor-pointer font-medium">View as text</summary>
        <div className="mt-1 max-h-40 overflow-y-auto">
          {data.map((row) => (
            <p key={row.cohort}>
              {row.cohort}: {row.values.map((v, i) => `M${i}=${v.toFixed(0)}%`).join(", ")}
            </p>
          ))}
        </div>
      </details>
      <table className="w-full border-collapse text-xs">
        <thead>
          <tr>
            <th className="sticky left-0 z-10 bg-surface-card px-3 py-2 text-left font-semibold text-text-secondary">
              Cohort
            </th>
            {Array.from({ length: maxMonths }).map((_, i) => (
              <th
                key={i}
                className="px-3 py-2 text-center font-semibold text-text-secondary"
              >
                M{i}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((row) => (
            <tr key={row.cohort}>
              <td className="sticky left-0 z-10 bg-surface-card px-3 py-1.5 font-medium text-text-primary">
                {row.cohort}
              </td>
              {Array.from({ length: maxMonths }).map((_, i) => {
                const val = row.values[i];
                if (val === undefined) {
                  return <td key={i} className="px-3 py-1.5" />;
                }
                return (
                  <td key={i} className="px-1 py-1">
                    <div
                      className={`rounded px-2 py-1 text-center font-medium ${retentionColor(val)}`}
                    >
                      {val.toFixed(0)}%
                    </div>
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
});
