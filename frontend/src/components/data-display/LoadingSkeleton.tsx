import { memo } from "react";

interface SkeletonBaseProps {
  className?: string;
}

const shimmer =
  "relative overflow-hidden before:absolute before:inset-0 before:-translate-x-full before:animate-[shimmer_1.5s_infinite] before:bg-gradient-to-r before:from-transparent before:via-white/40 before:to-transparent";

function Bone({ className = "" }: SkeletonBaseProps) {
  return <div className={`rounded bg-neutral-bg ${shimmer} ${className}`} />;
}

export function SkeletonCard({ className = "" }: SkeletonBaseProps) {
  return (
    <div className={`rounded-md bg-surface-card p-4 shadow-card ${className}`}>
      <Bone className="h-3 w-24" />
      <Bone className="mt-3 h-7 w-36" />
      <Bone className="mt-2 h-3 w-20" />
      <div className="mt-4 flex items-center justify-between border-t border-neutral-bg pt-3">
        <Bone className="h-2 w-16" />
        <Bone className="h-2 w-12" />
      </div>
    </div>
  );
}

export function SkeletonTable({ rows = 5, cols = 4 }: { rows?: number; cols?: number }) {
  return (
    <div className="rounded-md bg-surface-card shadow-card">
      <div className="border-b border-neutral-bg px-4 py-3">
        <Bone className="h-8 w-64" />
      </div>
      <table className="w-full">
        <thead>
          <tr className="border-b border-neutral-bg">
            {Array.from({ length: cols }).map((_, c) => (
              <th key={c} className="px-4 py-3">
                <Bone className="h-3 w-20" />
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {Array.from({ length: rows }).map((_, r) => (
            <tr key={r} className="border-b border-neutral-bg/50 last:border-b-0">
              {Array.from({ length: cols }).map((_, c) => (
                <td key={c} className="px-4 py-3">
                  <Bone className={`h-4 ${c === 0 ? "w-32" : "w-20"}`} />
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export function SkeletonChart({ className = "" }: SkeletonBaseProps) {
  return (
    <div className={`rounded-md bg-surface-card p-4 shadow-card ${className}`}>
      <div className="flex items-center justify-between">
        <div>
          <Bone className="h-4 w-36" />
          <Bone className="mt-1.5 h-3 w-48" />
        </div>
        <div className="flex gap-2">
          <Bone className="h-7 w-16 rounded-md" />
          <Bone className="h-7 w-16 rounded-md" />
        </div>
      </div>
      <div className="mt-4 flex items-end gap-1">
        {Array.from({ length: 12 }).map((_, i) => (
          <Bone
            key={i}
            className="flex-1"
            style={{ height: `${30 + Math.random() * 70}%`, minHeight: 24 } as React.CSSProperties}
          />
        ))}
      </div>
      <Bone className="mt-2 h-px w-full" />
    </div>
  );
}

interface LoadingSkeletonProps {
  variant: "card" | "table" | "chart";
  count?: number;
  rows?: number;
  className?: string;
}

export const LoadingSkeleton = memo(function LoadingSkeleton({
  variant,
  count = 1,
  rows,
  className = "",
}: LoadingSkeletonProps) {
  if (variant === "table") return <SkeletonTable rows={rows} />;
  if (variant === "chart") return <SkeletonChart className={className} />;

  return (
    <div className={`grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4 ${className}`}>
      {Array.from({ length: count }).map((_, i) => (
        <SkeletonCard key={i} />
      ))}
    </div>
  );
});
