import { useCallback } from "react";
import { useFilterStore, type TimeWindow } from "@/stores/useFilterStore";

export type CrossFilterPayload =
  | { dimension: "territory"; values: string[] }
  | { dimension: "segment"; values: string[] }
  | { dimension: "industry"; values: string[] }
  | {
      dimension: "timeWindow";
      window: TimeWindow;
      customRange?: { start: string; end: string } | null;
    };

export interface UseCrossFilterResult {
  applyCrossFilter: (payload: CrossFilterPayload) => void;
  clearCrossFilters: () => void;
}

export function useCrossFilter(): UseCrossFilterResult {
  const setTerritory = useFilterStore((s) => s.setTerritory);
  const setSegment = useFilterStore((s) => s.setSegment);
  const setIndustry = useFilterStore((s) => s.setIndustry);
  const setTimeWindow = useFilterStore((s) => s.setTimeWindow);
  const setCustomDateRange = useFilterStore((s) => s.setCustomDateRange);
  const resetFilters = useFilterStore((s) => s.resetFilters);

  const applyCrossFilter = useCallback(
    (payload: CrossFilterPayload) => {
      switch (payload.dimension) {
        case "territory":
          setTerritory(payload.values);
          break;
        case "segment":
          setSegment(payload.values);
          break;
        case "industry":
          setIndustry(payload.values);
          break;
        case "timeWindow":
          setTimeWindow(payload.window);
          if (payload.customRange !== undefined) {
            setCustomDateRange(payload.customRange);
          }
          break;
        default:
          break;
      }
    },
    [setTerritory, setSegment, setIndustry, setTimeWindow, setCustomDateRange],
  );

  const clearCrossFilters = useCallback(() => {
    resetFilters();
  }, [resetFilters]);

  return { applyCrossFilter, clearCrossFilters };
}
