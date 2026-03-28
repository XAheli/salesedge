import { memo, type ReactNode } from "react";
import {
  Mail,
  Phone,
  Users,
  Monitor,
  FileText,
  AlertCircle,
  Zap,
  Calendar,
  type LucideIcon,
} from "lucide-react";

export interface TimelineEvent {
  date: string;
  title: string;
  description?: string;
  type: "email" | "call" | "meeting" | "demo" | "proposal" | "signal" | "milestone" | "note";
  icon?: ReactNode;
}

interface TimelineProps {
  events: TimelineEvent[];
  className?: string;
}

const TYPE_CONFIG: Record<
  TimelineEvent["type"],
  { icon: LucideIcon; color: string; bg: string }
> = {
  email: { icon: Mail, color: "text-info", bg: "bg-info-bg" },
  call: { icon: Phone, color: "text-revenue-positive", bg: "bg-revenue-positive-bg" },
  meeting: { icon: Users, color: "text-primary-500", bg: "bg-primary-100" },
  demo: { icon: Monitor, color: "text-data-quality", bg: "bg-data-quality-bg" },
  proposal: { icon: FileText, color: "text-caution", bg: "bg-caution-bg" },
  signal: { icon: AlertCircle, color: "text-risk", bg: "bg-risk-bg" },
  milestone: { icon: Zap, color: "text-primary-600", bg: "bg-primary-100" },
  note: { icon: Calendar, color: "text-neutral", bg: "bg-neutral-bg" },
};

export const Timeline = memo(function Timeline({ events, className = "" }: TimelineProps) {
  if (!events.length) return null;

  return (
    <div className={`relative ${className}`}>
      <div className="absolute left-4 top-0 h-full w-px bg-neutral-bg" />

      <ul className="space-y-4">
        {events.map((event, idx) => {
          const cfg = TYPE_CONFIG[event.type];
          const Icon = cfg.icon;

          return (
            <li key={`${event.date}-${idx}`} className="relative pl-10">
              <div
                className={`absolute left-2 top-1 flex h-5 w-5 items-center justify-center rounded-full ${cfg.bg}`}
              >
                <Icon size={12} className={cfg.color} />
              </div>

              <div className="rounded-md bg-surface-card p-3 shadow-sm">
                <div className="flex items-start justify-between gap-2">
                  <p className="text-sm font-medium text-text-primary">{event.title}</p>
                  <time className="shrink-0 text-[10px] text-text-tertiary">{event.date}</time>
                </div>
                {event.description && (
                  <p className="mt-1 text-xs text-text-secondary">{event.description}</p>
                )}
              </div>
            </li>
          );
        })}
      </ul>
    </div>
  );
});
