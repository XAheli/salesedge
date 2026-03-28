import {
  createContext,
  createElement,
  useCallback,
  useContext,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import type { TimeWindow } from "@/stores/useFilterStore";

export interface DateRange {
  start: string;
  end: string;
}

export interface TimeSyncContextValue {
  timeWindow: TimeWindow;
  setTimeWindow: (w: TimeWindow) => void;
  customDateRange: DateRange | null;
  setCustomDateRange: (range: DateRange | null) => void;
}

const TimeSyncContext = createContext<TimeSyncContextValue | null>(null);

export interface TimeWindowSyncProviderProps {
  children: ReactNode;
  initialTimeWindow?: TimeWindow;
  initialCustomRange?: DateRange | null;
}

export function TimeWindowSyncProvider({
  children,
  initialTimeWindow = "30d",
  initialCustomRange = null,
}: TimeWindowSyncProviderProps) {
  const [timeWindow, setTimeWindowState] = useState<TimeWindow>(initialTimeWindow);
  const [customDateRange, setCustomDateRangeState] = useState<DateRange | null>(
    initialCustomRange,
  );

  const setTimeWindow = useCallback((w: TimeWindow) => {
    setTimeWindowState(w);
    if (w !== "custom") {
      setCustomDateRangeState(null);
    }
  }, []);

  const setCustomDateRange = useCallback((range: DateRange | null) => {
    setCustomDateRangeState(range);
    if (range) {
      setTimeWindowState("custom");
    }
  }, []);

  const value = useMemo(
    () => ({
      timeWindow,
      setTimeWindow,
      customDateRange,
      setCustomDateRange,
    }),
    [timeWindow, setTimeWindow, customDateRange, setCustomDateRange],
  );

  return createElement(TimeSyncContext.Provider, { value }, children);
}

export function useTimeSync(): TimeSyncContextValue {
  const ctx = useContext(TimeSyncContext);
  if (!ctx) {
    throw new Error("useTimeSync must be used within a TimeWindowSyncProvider");
  }
  return ctx;
}
