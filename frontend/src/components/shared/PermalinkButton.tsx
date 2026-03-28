import { useCallback } from "react";
import { Link2 } from "lucide-react";
import clsx from "clsx";
import { useFilterStore } from "@/stores/useFilterStore";
import { serializeFilters } from "@/utils/filter-serialization";
import { announce } from "@/utils/accessibility";
import { toast } from "sonner";

export interface PermalinkButtonProps {
  className?: string;
  /** Path to prepend (defaults to current pathname). */
  basePath?: string;
}

export function PermalinkButton({ className, basePath }: PermalinkButtonProps) {
  const timeWindow = useFilterStore((s) => s.timeWindow);
  const customDateRange = useFilterStore((s) => s.customDateRange);
  const territory = useFilterStore((s) => s.territory);
  const segment = useFilterStore((s) => s.segment);
  const industry = useFilterStore((s) => s.industry);

  const copyPermalink = useCallback(async () => {
    const filters = {
      timeWindow,
      customDateRange,
      territory,
      segment,
      industry,
    };
    const params = serializeFilters(filters);
    const path = basePath ?? window.location.pathname;
    const relative = `${path}?${params.toString()}`;
    const absolute = `${window.location.origin}${relative}`;

    try {
      await navigator.clipboard.writeText(absolute);
      toast.success("Link copied", { description: "Shareable URL with filters is on the clipboard." });
      announce("Filter link copied to clipboard", "polite");
    } catch (e) {
      toast.error("Could not copy link", {
        description: e instanceof Error ? e.message : "Clipboard permission denied.",
      });
    }
  }, [basePath, customDateRange, industry, segment, territory, timeWindow]);

  return (
    <button
      type="button"
      onClick={() => void copyPermalink()}
      className={clsx(
        "inline-flex h-9 items-center gap-2 rounded-lg border border-neutral-bg bg-surface-card px-3 text-sm font-medium text-text-primary hover:bg-neutral-bg/60",
        className,
      )}
    >
      <Link2 className="h-4 w-4" aria-hidden />
      Copy link
    </button>
  );
}
