import { useCallback, useEffect, useRef, useState } from "react";

const STORAGE_KEY = "salesedge-layout-preferences";

export interface LayoutPreferences {
  sidebarWidth: number;
  panelOrder: string[];
  columnPreferences: Record<string, boolean>;
}

const DEFAULT_LAYOUT: LayoutPreferences = {
  sidebarWidth: 224,
  panelOrder: [],
  columnPreferences: {},
};

function safeParse(raw: string | null): LayoutPreferences {
  if (!raw) {
    return { ...DEFAULT_LAYOUT };
  }
  try {
    const parsed = JSON.parse(raw) as Partial<LayoutPreferences>;
    return {
      sidebarWidth:
        typeof parsed.sidebarWidth === "number" && parsed.sidebarWidth >= 160 && parsed.sidebarWidth <= 400
          ? parsed.sidebarWidth
          : DEFAULT_LAYOUT.sidebarWidth,
      panelOrder: Array.isArray(parsed.panelOrder)
        ? parsed.panelOrder.filter((x): x is string => typeof x === "string")
        : [],
      columnPreferences:
        parsed.columnPreferences && typeof parsed.columnPreferences === "object"
          ? Object.fromEntries(
              Object.entries(parsed.columnPreferences).filter(
                ([k, v]) => typeof k === "string" && typeof v === "boolean",
              ),
            )
          : {},
    };
  } catch {
    return { ...DEFAULT_LAYOUT };
  }
}

export interface UsePersistedLayoutResult {
  sidebarWidth: number;
  setSidebarWidth: (width: number) => void;
  panelOrder: string[];
  setPanelOrder: (order: string[]) => void;
  columnPreferences: Record<string, boolean>;
  setColumnPreferences: (prefs: Record<string, boolean>) => void;
  setColumnVisible: (columnId: string, visible: boolean) => void;
  resetLayout: () => void;
}

export function usePersistedLayout(): UsePersistedLayoutResult {
  const [state, setState] = useState<LayoutPreferences>(() => {
    if (typeof window === "undefined") {
      return { ...DEFAULT_LAYOUT };
    }
    return safeParse(localStorage.getItem(STORAGE_KEY));
  });

  const saveTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  const persist = useCallback((next: LayoutPreferences) => {
    if (typeof window === "undefined") {
      return;
    }
    if (saveTimer.current) {
      clearTimeout(saveTimer.current);
    }
    saveTimer.current = setTimeout(() => {
      try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
      } catch {
        /* quota or private mode */
      }
      saveTimer.current = null;
    }, 200);
  }, []);

  useEffect(() => {
    persist(state);
    return () => {
      if (saveTimer.current) {
        clearTimeout(saveTimer.current);
      }
    };
  }, [state, persist]);

  const setSidebarWidth = useCallback((width: number) => {
    setState((s) => ({ ...s, sidebarWidth: width }));
  }, []);

  const setPanelOrder = useCallback((order: string[]) => {
    setState((s) => ({ ...s, panelOrder: order }));
  }, []);

  const setColumnPreferences = useCallback((prefs: Record<string, boolean>) => {
    setState((s) => ({ ...s, columnPreferences: prefs }));
  }, []);

  const setColumnVisible = useCallback((columnId: string, visible: boolean) => {
    setState((s) => ({
      ...s,
      columnPreferences: { ...s.columnPreferences, [columnId]: visible },
    }));
  }, []);

  const resetLayout = useCallback(() => {
    setState({ ...DEFAULT_LAYOUT });
    try {
      localStorage.removeItem(STORAGE_KEY);
    } catch {
      /* ignore */
    }
  }, []);

  return {
    sidebarWidth: state.sidebarWidth,
    setSidebarWidth,
    panelOrder: state.panelOrder,
    setPanelOrder,
    columnPreferences: state.columnPreferences,
    setColumnPreferences,
    setColumnVisible,
    resetLayout,
  };
}
