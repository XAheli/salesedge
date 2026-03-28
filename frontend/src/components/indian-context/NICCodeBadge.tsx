import { memo, useState } from "react";

interface NICCodeBadgeProps {
  code: string;
  description: string;
  section?: string;
  className?: string;
}

export const NICCodeBadge = memo(function NICCodeBadge({
  code,
  description,
  section,
  className = "",
}: NICCodeBadgeProps) {
  const [showTooltip, setShowTooltip] = useState(false);

  return (
    <span
      className={`relative inline-flex items-center gap-1 rounded-full bg-data-quality-bg px-2 py-0.5 text-[10px] font-medium text-data-quality ${className}`}
      onMouseEnter={() => setShowTooltip(true)}
      onMouseLeave={() => setShowTooltip(false)}
    >
      <span className="font-mono">NIC {code}</span>

      {showTooltip && (
        <div className="absolute bottom-full left-1/2 z-50 mb-2 -translate-x-1/2 whitespace-nowrap rounded-md border border-neutral-bg bg-surface-card px-3 py-2 shadow-lg">
          <p className="text-xs font-semibold text-text-primary">{description}</p>
          {section && (
            <p className="mt-0.5 text-[10px] text-text-secondary">Section: {section}</p>
          )}
          <div className="absolute left-1/2 top-full -translate-x-1/2 border-4 border-transparent border-t-surface-card" />
        </div>
      )}
    </span>
  );
});
