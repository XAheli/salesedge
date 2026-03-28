import * as Tabs from "@radix-ui/react-tabs";
import clsx from "clsx";
import { useFilterStore, type TimeWindow } from "@/stores/useFilterStore";

const OPTIONS: { value: TimeWindow; label: string }[] = [
  { value: "7d", label: "7d" },
  { value: "30d", label: "30d" },
  { value: "90d", label: "90d" },
  { value: "1y", label: "1y" },
  { value: "custom", label: "Custom" },
];

export interface TimeWindowPickerProps {
  className?: string;
  /** When true, reads/writes global filter store (default). */
  useGlobalStore?: boolean;
  value?: TimeWindow;
  onChange?: (window: TimeWindow) => void;
  customRange?: { start: string; end: string } | null;
  onCustomRangeChange?: (range: { start: string; end: string } | null) => void;
}

export function TimeWindowPicker({
  className,
  useGlobalStore = true,
  value: controlledValue,
  onChange,
  customRange: controlledRange,
  onCustomRangeChange,
}: TimeWindowPickerProps) {
  const storeWindow = useFilterStore((s) => s.timeWindow);
  const storeCustom = useFilterStore((s) => s.customDateRange);
  const setTimeWindow = useFilterStore((s) => s.setTimeWindow);
  const setCustomDateRange = useFilterStore((s) => s.setCustomDateRange);

  const value: TimeWindow = useGlobalStore ? storeWindow : controlledValue ?? "30d";
  const customRange = useGlobalStore ? storeCustom : controlledRange ?? null;

  const handleValue = (next: TimeWindow) => {
    if (useGlobalStore) {
      setTimeWindow(next);
    } else {
      onChange?.(next);
    }
  };

  const handleStart = (start: string) => {
    const end = customRange?.end ?? start;
    const range = { start, end };
    if (useGlobalStore) {
      setCustomDateRange(range);
    } else {
      onCustomRangeChange?.(range);
    }
  };

  const handleEnd = (end: string) => {
    const start = customRange?.start ?? end;
    const range = { start, end };
    if (useGlobalStore) {
      setCustomDateRange(range);
    } else {
      onCustomRangeChange?.(range);
    }
  };

  return (
    <div className={clsx("flex flex-col gap-2", className)}>
      <Tabs.Root value={value} onValueChange={(v) => handleValue(v as TimeWindow)}>
        <Tabs.List
          className="inline-flex h-9 flex-wrap items-center gap-0.5 rounded-lg border border-neutral-bg bg-neutral-bg/40 p-0.5"
          aria-label="Time window"
        >
          {OPTIONS.map((opt) => (
            <Tabs.Trigger
              key={opt.value}
              value={opt.value}
              className={clsx(
                "rounded-md px-3 py-1.5 text-xs font-medium transition-colors",
                "text-text-secondary hover:text-text-primary",
                "data-[state=active]:bg-surface-card data-[state=active]:text-text-primary data-[state=active]:shadow-sm",
              )}
            >
              {opt.label}
            </Tabs.Trigger>
          ))}
        </Tabs.List>
      </Tabs.Root>

      {value === "custom" && (
        <div className="flex flex-wrap items-center gap-2">
          <label className="sr-only" htmlFor="tw-custom-start">
            Start date
          </label>
          <input
            id="tw-custom-start"
            type="date"
            value={customRange?.start ?? ""}
            onChange={(e) => handleStart(e.target.value)}
            className="h-9 rounded-md border border-neutral-bg bg-surface-card px-2 text-sm text-text-primary"
          />
          <span className="text-text-tertiary">–</span>
          <label className="sr-only" htmlFor="tw-custom-end">
            End date
          </label>
          <input
            id="tw-custom-end"
            type="date"
            value={customRange?.end ?? ""}
            onChange={(e) => handleEnd(e.target.value)}
            className="h-9 rounded-md border border-neutral-bg bg-surface-card px-2 text-sm text-text-primary"
          />
        </div>
      )}
    </div>
  );
}
