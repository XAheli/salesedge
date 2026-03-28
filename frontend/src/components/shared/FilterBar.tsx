import { useMemo, useState } from "react";
import * as DropdownMenu from "@radix-ui/react-dropdown-menu";
import { ChevronDown, Filter } from "lucide-react";
import clsx from "clsx";
import { useFilterStore } from "@/stores/useFilterStore";
import { INDIAN_STATES } from "@/utils/indian-formatting";
import { TimeWindowPicker } from "./TimeWindowPicker";

const SEGMENTS = [
  { value: "enterprise", label: "Enterprise" },
  { value: "mid_market", label: "Mid-market" },
  { value: "smb", label: "SMB" },
  { value: "startup", label: "Startup" },
] as const;

const INDUSTRY_OPTIONS = [
  "IT Services",
  "BFSI",
  "Manufacturing",
  "Retail",
  "Healthcare",
  "Energy",
  "Telecom",
  "Logistics",
] as const;

export interface FilterBarProps {
  className?: string;
}

export function FilterBar({ className }: FilterBarProps) {
  const territory = useFilterStore((s) => s.territory);
  const segment = useFilterStore((s) => s.segment);
  const industry = useFilterStore((s) => s.industry);
  const setTerritory = useFilterStore((s) => s.setTerritory);
  const setSegment = useFilterStore((s) => s.setSegment);
  const setIndustry = useFilterStore((s) => s.setIndustry);
  const resetFilters = useFilterStore((s) => s.resetFilters);

  const [territoryOpen, setTerritoryOpen] = useState(false);
  const [segmentOpen, setSegmentOpen] = useState(false);
  const [industryOpen, setIndustryOpen] = useState(false);

  const territoryOptions = useMemo(
    () =>
      Object.entries(INDIAN_STATES).map(([code, { name }]) => ({
        value: code,
        label: `${name} (${code})`,
      })),
    [],
  );

  const territoryLabel =
    territory.length === 0
      ? "All territories"
      : territory.length === 1
        ? territoryOptions.find((o) => o.value === territory[0])?.label ?? territory[0]
        : `${territory.length} territories`;

  const segmentLabel =
    segment.length === 0
      ? "All segments"
      : segment.length === 1
        ? SEGMENTS.find((s) => s.value === segment[0])?.label ?? segment[0]!
        : `${segment.length} segments`;

  const industryLabel =
    industry.length === 0
      ? "All industries"
      : industry.length === 1
        ? industry[0]!
        : `${industry.length} industries`;

  return (
    <div
      className={clsx(
        "flex flex-col gap-3 rounded-xl border border-neutral-bg bg-surface-card p-4 lg:flex-row lg:flex-wrap lg:items-end",
        className,
      )}
    >
      <div className="flex items-center gap-2 text-sm font-medium text-text-secondary">
        <Filter className="h-4 w-4" aria-hidden />
        Filters
      </div>

      <div className="flex min-w-[200px] flex-1 flex-col gap-1">
        <span className="text-xs font-medium text-text-tertiary">Time window</span>
        <TimeWindowPicker />
      </div>

      <div className="flex flex-wrap gap-2">
        <DropdownMenu.Root open={territoryOpen} onOpenChange={setTerritoryOpen}>
          <DropdownMenu.Trigger asChild>
            <button
              type="button"
              className="inline-flex h-9 min-w-[10rem] items-center justify-between gap-2 rounded-lg border border-neutral-bg bg-neutral-bg/40 px-3 text-left text-sm text-text-primary hover:bg-neutral-bg/70"
            >
              {territoryLabel}
              <ChevronDown className="h-4 w-4 opacity-50" aria-hidden />
            </button>
          </DropdownMenu.Trigger>
          <DropdownMenu.Portal>
            <DropdownMenu.Content
              className="z-50 max-h-64 min-w-[14rem] overflow-y-auto rounded-lg border border-neutral-bg bg-surface-card p-1 shadow-lg"
              sideOffset={4}
              align="start"
            >
              <DropdownMenu.Item
                className="cursor-pointer rounded-md px-2 py-1.5 text-sm outline-none hover:bg-neutral-bg"
                onSelect={() => setTerritory([])}
              >
                Clear all
              </DropdownMenu.Item>
              {territoryOptions.map((opt) => (
                <DropdownMenu.CheckboxItem
                  key={opt.value}
                  className="flex cursor-pointer items-center gap-2 rounded-md px-2 py-1.5 text-sm outline-none hover:bg-neutral-bg"
                  checked={territory.includes(opt.value)}
                  onCheckedChange={(checked) =>
                    setTerritory(
                      checked
                        ? [...new Set([...territory, opt.value])]
                        : territory.filter((t) => t !== opt.value),
                    )
                  }
                >
                  {opt.label}
                </DropdownMenu.CheckboxItem>
              ))}
            </DropdownMenu.Content>
          </DropdownMenu.Portal>
        </DropdownMenu.Root>

        <DropdownMenu.Root open={segmentOpen} onOpenChange={setSegmentOpen}>
          <DropdownMenu.Trigger asChild>
            <button
              type="button"
              className="inline-flex h-9 min-w-[10rem] items-center justify-between gap-2 rounded-lg border border-neutral-bg bg-neutral-bg/40 px-3 text-left text-sm text-text-primary hover:bg-neutral-bg/70"
            >
              {segmentLabel}
              <ChevronDown className="h-4 w-4 opacity-50" aria-hidden />
            </button>
          </DropdownMenu.Trigger>
          <DropdownMenu.Portal>
            <DropdownMenu.Content
              className="z-50 min-w-[12rem] rounded-lg border border-neutral-bg bg-surface-card p-1 shadow-lg"
              sideOffset={4}
            >
              <DropdownMenu.Item
                className="cursor-pointer rounded-md px-2 py-1.5 text-sm outline-none hover:bg-neutral-bg"
                onSelect={() => setSegment([])}
              >
                Clear all
              </DropdownMenu.Item>
              {SEGMENTS.map((s) => (
                <DropdownMenu.CheckboxItem
                  key={s.value}
                  className="flex cursor-pointer items-center gap-2 rounded-md px-2 py-1.5 text-sm outline-none hover:bg-neutral-bg"
                  checked={segment.includes(s.value)}
                  onCheckedChange={(checked) =>
                    setSegment(
                      checked
                        ? [...new Set([...segment, s.value])]
                        : segment.filter((x) => x !== s.value),
                    )
                  }
                >
                  {s.label}
                </DropdownMenu.CheckboxItem>
              ))}
            </DropdownMenu.Content>
          </DropdownMenu.Portal>
        </DropdownMenu.Root>

        <DropdownMenu.Root open={industryOpen} onOpenChange={setIndustryOpen}>
          <DropdownMenu.Trigger asChild>
            <button
              type="button"
              className="inline-flex h-9 min-w-[10rem] items-center justify-between gap-2 rounded-lg border border-neutral-bg bg-neutral-bg/40 px-3 text-left text-sm text-text-primary hover:bg-neutral-bg/70"
            >
              {industryLabel}
              <ChevronDown className="h-4 w-4 opacity-50" aria-hidden />
            </button>
          </DropdownMenu.Trigger>
          <DropdownMenu.Portal>
            <DropdownMenu.Content
              className="z-50 max-h-64 min-w-[12rem] overflow-y-auto rounded-lg border border-neutral-bg bg-surface-card p-1 shadow-lg"
              sideOffset={4}
            >
              <DropdownMenu.Item
                className="cursor-pointer rounded-md px-2 py-1.5 text-sm outline-none hover:bg-neutral-bg"
                onSelect={() => setIndustry([])}
              >
                Clear all
              </DropdownMenu.Item>
              {INDUSTRY_OPTIONS.map((name) => (
                <DropdownMenu.CheckboxItem
                  key={name}
                  className="flex cursor-pointer items-center gap-2 rounded-md px-2 py-1.5 text-sm outline-none hover:bg-neutral-bg"
                  checked={industry.includes(name)}
                  onCheckedChange={(checked) =>
                    setIndustry(
                      checked
                        ? [...new Set([...industry, name])]
                        : industry.filter((x) => x !== name),
                    )
                  }
                >
                  {name}
                </DropdownMenu.CheckboxItem>
              ))}
            </DropdownMenu.Content>
          </DropdownMenu.Portal>
        </DropdownMenu.Root>

        <button
          type="button"
          onClick={() => resetFilters()}
          className="h-9 rounded-lg border border-transparent px-3 text-sm text-primary-600 hover:bg-primary-500/10"
        >
          Reset
        </button>
      </div>
    </div>
  );
}
