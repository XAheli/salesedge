const LIVE_REGION_ID = "salesedge-aria-live-announcer";

function ensureLiveRegion(politeness: "polite" | "assertive"): HTMLElement {
  let el = document.getElementById(LIVE_REGION_ID);
  if (!el) {
    el = document.createElement("div");
    el.id = LIVE_REGION_ID;
    el.setAttribute("role", "status");
    el.setAttribute("aria-live", politeness);
    el.setAttribute("aria-atomic", "true");
    Object.assign(el.style, {
      position: "absolute",
      width: "1px",
      height: "1px",
      padding: "0",
      margin: "-1px",
      overflow: "hidden",
      clip: "rect(0,0,0,0)",
      whiteSpace: "nowrap",
      border: "0",
    });
    document.body.appendChild(el);
  }
  return el;
}

export function announce(message: string, politeness: "polite" | "assertive" = "polite"): void {
  if (typeof document === "undefined" || !message.trim()) {
    return;
  }
  const el = ensureLiveRegion(politeness);
  el.textContent = "";
  window.requestAnimationFrame(() => {
    el.textContent = message;
  });
}

export interface FocusTrapHandle {
  deactivate: () => void;
}

export function trapFocus(container: HTMLElement | null): FocusTrapHandle | null {
  if (!container || typeof document === "undefined") {
    return null;
  }

  const selector =
    'a[href], button:not([disabled]), textarea, input, select, [tabindex]:not([tabindex="-1"])';

  const getFocusable = () =>
    Array.from(container.querySelectorAll<HTMLElement>(selector)).filter(
      (el) => el.offsetParent !== null || el === document.activeElement,
    );

  const previous = document.activeElement as HTMLElement | null;

  const onKeyDown = (e: KeyboardEvent) => {
    if (e.key !== "Tab") {
      return;
    }
    const nodes = getFocusable();
    if (!nodes.length) {
      return;
    }
    const first = nodes[0]!;
    const last = nodes[nodes.length - 1]!;
    if (e.shiftKey) {
      if (document.activeElement === first) {
        e.preventDefault();
        last.focus();
      }
    } else if (document.activeElement === last) {
      e.preventDefault();
      first.focus();
    }
  };

  container.addEventListener("keydown", onKeyDown);
  const nodes = getFocusable();
  nodes[0]?.focus();

  return {
    deactivate: () => {
      container.removeEventListener("keydown", onKeyDown);
      previous?.focus?.();
    },
  };
}

export type ChartKind =
  | "line"
  | "bar"
  | "area"
  | "pie"
  | "scatter"
  | "heatmap"
  | "sankey"
  | "treemap"
  | "funnel"
  | "unknown";

export function getAriaLabel(
  chartType: ChartKind,
  data: { title?: string; description?: string; pointCount?: number },
): string {
  const title = data.title?.trim() || "Chart";
  const count =
    typeof data.pointCount === "number" ? `${data.pointCount} data points` : "data series";
  const extra = data.description?.trim();

  const kindLabel: Record<ChartKind, string> = {
    line: "line chart showing trend over time",
    bar: "bar chart comparing categories",
    area: "area chart showing volume over time",
    pie: "pie chart showing proportions",
    scatter: "scatter plot showing correlation",
    heatmap: "heatmap showing intensity by two dimensions",
    sankey: "sankey diagram showing flows between stages",
    treemap: "treemap showing hierarchical values",
    funnel: "funnel chart showing stage conversion",
    unknown: "data visualization",
  };

  const base = `${title}: ${kindLabel[chartType]}, ${count}.`;
  return extra ? `${base} ${extra}` : base;
}
