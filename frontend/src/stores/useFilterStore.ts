import { create } from "zustand";

export type TimeWindow = "7d" | "30d" | "90d" | "1y" | "custom";

interface DateRange {
  start: string;
  end: string;
}

interface FilterState {
  timeWindow: TimeWindow;
  customDateRange: DateRange | null;
  territory: string[];
  segment: string[];
  industry: string[];

  setTimeWindow: (window: TimeWindow) => void;
  setCustomDateRange: (range: DateRange | null) => void;
  setTerritory: (territories: string[]) => void;
  setSegment: (segments: string[]) => void;
  setIndustry: (industries: string[]) => void;
  resetFilters: () => void;
}

const DEFAULT_FILTERS = {
  timeWindow: "30d" as const,
  customDateRange: null,
  territory: [] as string[],
  segment: [] as string[],
  industry: [] as string[],
};

export const useFilterStore = create<FilterState>()((set) => ({
  ...DEFAULT_FILTERS,

  setTimeWindow: (timeWindow) =>
    set({
      timeWindow,
      customDateRange: timeWindow !== "custom" ? null : undefined,
    }),

  setCustomDateRange: (customDateRange) =>
    set({ customDateRange, timeWindow: "custom" }),

  setTerritory: (territory) => set({ territory }),
  setSegment: (segment) => set({ segment }),
  setIndustry: (industry) => set({ industry }),

  resetFilters: () => set(DEFAULT_FILTERS),
}));
