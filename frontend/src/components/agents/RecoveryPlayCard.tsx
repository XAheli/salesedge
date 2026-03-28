import { memo, useState, useCallback } from "react";
import { Sparkles, ChevronDown, ChevronUp, Check, Circle } from "lucide-react";
import { ConfidenceBadge } from "@/components/data-display/ConfidenceBadge";

export interface RecoveryAction {
  action: string;
  owner: string;
  deadline: string;
  status: "pending" | "in_progress" | "completed" | "skipped";
}

interface RecoveryPlayCardProps {
  title: string;
  description: string;
  confidence: number;
  priority: "high" | "medium" | "low";
  actions: RecoveryAction[];
  reasoning?: string;
  onActionToggle?: (index: number) => void;
  className?: string;
}

const PRIORITY_STYLES = {
  high: "border-l-risk bg-risk-bg/30 text-risk",
  medium: "border-l-caution bg-caution-bg/30 text-caution",
  low: "border-l-info bg-info-bg/30 text-info",
};

const ACTION_STATUS_ICON = {
  completed: <Check size={14} className="text-revenue-positive" />,
  in_progress: <Circle size={14} className="fill-primary-500/20 text-primary-500" />,
  pending: <Circle size={14} className="text-text-tertiary" />,
  skipped: <Check size={14} className="text-text-tertiary line-through" />,
};

export const RecoveryPlayCard = memo(function RecoveryPlayCard({
  title,
  description,
  confidence,
  priority,
  actions,
  reasoning,
  onActionToggle,
  className = "",
}: RecoveryPlayCardProps) {
  const [expanded, setExpanded] = useState(false);
  const completedCount = actions.filter((a) => a.status === "completed").length;

  return (
    <div className={`rounded-md border-l-4 bg-surface-card shadow-card ${PRIORITY_STYLES[priority].split(" ")[0]} ${className}`}>
      <div className="p-4">
        <div className="flex items-start justify-between gap-3">
          <div className="flex items-start gap-2.5">
            <div className="mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center rounded-md bg-primary-50">
              <Sparkles size={14} className="text-primary-500" />
            </div>
            <div>
              <h4 className="text-sm font-semibold text-text-primary">{title}</h4>
              <p className="mt-0.5 text-xs text-text-secondary">{description}</p>
            </div>
          </div>
          <ConfidenceBadge confidence={confidence} size="sm" />
        </div>

        <div className="mt-3 flex items-center gap-3">
          <span
            className={`rounded-full px-2 py-0.5 text-[10px] font-semibold uppercase ${
              PRIORITY_STYLES[priority]
            }`}
          >
            {priority}
          </span>
          <span className="text-[10px] text-text-tertiary">
            {completedCount}/{actions.length} actions done
          </span>
          <div className="ml-auto h-1 flex-1 max-w-[80px] overflow-hidden rounded-full bg-neutral-bg">
            <div
              className="h-full rounded-full bg-revenue-positive transition-all"
              style={{
                width: `${actions.length ? (completedCount / actions.length) * 100 : 0}%`,
              }}
            />
          </div>
        </div>
      </div>

      <div className="border-t border-neutral-bg">
        <button
          onClick={() => setExpanded(!expanded)}
          className="flex w-full items-center justify-between px-4 py-2 text-xs font-medium text-text-secondary hover:bg-neutral-bg/50"
        >
          <span>Actions & Details</span>
          {expanded ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
        </button>

        {expanded && (
          <div className="px-4 pb-4">
            <ul className="space-y-2">
              {actions.map((action, idx) => (
                <li
                  key={idx}
                  className="flex items-start gap-2 rounded-md bg-neutral-bg/30 px-3 py-2"
                >
                  <button
                    onClick={() => onActionToggle?.(idx)}
                    className="mt-0.5 shrink-0"
                    disabled={!onActionToggle}
                  >
                    {ACTION_STATUS_ICON[action.status]}
                  </button>
                  <div className="min-w-0 flex-1">
                    <p
                      className={`text-xs ${
                        action.status === "completed"
                          ? "text-text-tertiary line-through"
                          : "text-text-primary"
                      }`}
                    >
                      {action.action}
                    </p>
                    <div className="mt-0.5 flex items-center gap-2 text-[10px] text-text-tertiary">
                      <span>{action.owner}</span>
                      <span>&middot;</span>
                      <span>{action.deadline}</span>
                    </div>
                  </div>
                </li>
              ))}
            </ul>

            {reasoning && (
              <div className="mt-3 rounded-md bg-primary-50 px-3 py-2">
                <p className="text-[10px] font-medium text-primary-700">AI Reasoning</p>
                <p className="mt-0.5 text-xs text-primary-800">{reasoning}</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
});
