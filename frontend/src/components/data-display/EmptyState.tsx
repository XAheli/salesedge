import { memo, type ReactNode } from "react";
import { Inbox } from "lucide-react";

interface EmptyStateProps {
  title: string;
  description?: string;
  icon?: ReactNode;
  action?: {
    label: string;
    onClick: () => void;
  };
  className?: string;
}

export const EmptyState = memo(function EmptyState({
  title,
  description,
  icon,
  action,
  className = "",
}: EmptyStateProps) {
  return (
    <div
      className={`flex flex-col items-center justify-center px-6 py-16 text-center ${className}`}
    >
      <div className="flex h-16 w-16 items-center justify-center rounded-full bg-neutral-bg">
        {icon ?? <Inbox className="h-7 w-7 text-text-tertiary" />}
      </div>

      <h3 className="mt-4 font-display text-base font-semibold text-text-primary">{title}</h3>

      {description && (
        <p className="mt-1.5 max-w-sm text-sm text-text-secondary">{description}</p>
      )}

      {action && (
        <button
          onClick={action.onClick}
          className="mt-5 rounded-lg bg-primary-500 px-4 py-2 text-sm font-semibold text-white transition-colors hover:bg-primary-600 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary-500"
        >
          {action.label}
        </button>
      )}
    </div>
  );
});
