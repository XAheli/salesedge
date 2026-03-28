import { memo } from "react";
import { Bot, CheckCircle, Clock, AlertTriangle } from "lucide-react";

type AgentStatus = "active" | "idle" | "error";

interface AgentStatusCardProps {
  name: string;
  status: AgentStatus;
  lastAction?: string;
  lastActionTime?: string;
  successRate?: number;
  tasksCompleted?: number;
  className?: string;
}

const STATUS_CONFIG: Record<
  AgentStatus,
  { label: string; dot: string; bg: string; icon: typeof CheckCircle }
> = {
  active: {
    label: "Active",
    dot: "bg-revenue-positive",
    bg: "bg-revenue-positive-bg",
    icon: CheckCircle,
  },
  idle: {
    label: "Idle",
    dot: "bg-caution",
    bg: "bg-caution-bg",
    icon: Clock,
  },
  error: {
    label: "Error",
    dot: "bg-risk",
    bg: "bg-risk-bg",
    icon: AlertTriangle,
  },
};

export const AgentStatusCard = memo(function AgentStatusCard({
  name,
  status,
  lastAction,
  lastActionTime,
  successRate,
  tasksCompleted,
  className = "",
}: AgentStatusCardProps) {
  const cfg = STATUS_CONFIG[status];
  const StatusIcon = cfg.icon;

  return (
    <div className={`rounded-md bg-surface-card p-4 shadow-card ${className}`}>
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-center gap-2.5">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary-50">
            <Bot size={18} className="text-primary-500" />
          </div>
          <div>
            <h4 className="text-sm font-semibold text-text-primary">{name}</h4>
            <div className="mt-0.5 flex items-center gap-1.5">
              <span className="relative flex h-2 w-2">
                {status === "active" && (
                  <span className={`absolute inline-flex h-full w-full animate-ping rounded-full ${cfg.dot} opacity-40`} />
                )}
                <span className={`relative inline-flex h-2 w-2 rounded-full ${cfg.dot}`} />
              </span>
              <span className="text-[10px] font-medium text-text-secondary">{cfg.label}</span>
            </div>
          </div>
        </div>

        <div className={`rounded-full p-1.5 ${cfg.bg}`}>
          <StatusIcon size={14} className={status === "active" ? "text-revenue-positive" : status === "idle" ? "text-caution" : "text-risk"} />
        </div>
      </div>

      {lastAction && (
        <div className="mt-3 rounded bg-neutral-bg/50 px-2.5 py-1.5">
          <p className="text-xs text-text-secondary">
            <span className="font-medium text-text-primary">Last:</span> {lastAction}
          </p>
          {lastActionTime && (
            <p className="mt-0.5 text-[10px] text-text-tertiary">{lastActionTime}</p>
          )}
        </div>
      )}

      <div className="mt-3 flex items-center gap-4 border-t border-neutral-bg pt-3">
        {successRate !== undefined && (
          <div>
            <p className="text-[10px] text-text-tertiary">Success Rate</p>
            <p className={`text-sm font-semibold ${successRate >= 90 ? "text-revenue-positive" : successRate >= 70 ? "text-caution" : "text-risk"}`}>
              {successRate.toFixed(1)}%
            </p>
          </div>
        )}
        {tasksCompleted !== undefined && (
          <div>
            <p className="text-[10px] text-text-tertiary">Completed</p>
            <p className="text-sm font-semibold text-text-primary">{tasksCompleted}</p>
          </div>
        )}
      </div>
    </div>
  );
});
