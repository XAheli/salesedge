import { memo, useMemo, useState, useRef, useEffect, useCallback } from "react";
import { ChevronDown, Search, X } from "lucide-react";
import { INDIAN_STATES } from "@/utils/indian-formatting";

interface StatePickerProps {
  value?: string;
  onChange: (code: string) => void;
  placeholder?: string;
  className?: string;
}

const ALL_STATES = Object.values(INDIAN_STATES).sort((a, b) =>
  a.name.localeCompare(b.name),
);

export const StatePicker = memo(function StatePicker({
  value,
  onChange,
  placeholder = "Select State/UT",
  className = "",
}: StatePickerProps) {
  const [open, setOpen] = useState(false);
  const [search, setSearch] = useState("");
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function onClickOutside(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setOpen(false);
      }
    }
    document.addEventListener("mousedown", onClickOutside);
    return () => document.removeEventListener("mousedown", onClickOutside);
  }, []);

  const filtered = useMemo(
    () =>
      search
        ? ALL_STATES.filter(
            (s) =>
              s.name.toLowerCase().includes(search.toLowerCase()) ||
              s.code.toLowerCase().includes(search.toLowerCase()),
          )
        : ALL_STATES,
    [search],
  );

  const selected = value ? INDIAN_STATES[value] : undefined;

  const handleSelect = useCallback(
    (code: string) => {
      onChange(code);
      setOpen(false);
      setSearch("");
    },
    [onChange],
  );

  return (
    <div ref={ref} className={`relative ${className}`}>
      <button
        type="button"
        onClick={() => setOpen(!open)}
        className="flex h-9 w-full items-center justify-between rounded-md border border-neutral-bg bg-surface-card px-3 text-sm transition-colors hover:border-primary-300 focus:border-primary-400 focus:outline-none"
      >
        <span className={selected ? "text-text-primary" : "text-text-tertiary"}>
          {selected ? `${selected.name} (${selected.code})` : placeholder}
        </span>
        <div className="flex items-center gap-1">
          {value && (
            <span
              onClick={(e) => {
                e.stopPropagation();
                onChange("");
                setSearch("");
              }}
              className="rounded p-0.5 text-text-tertiary hover:text-text-secondary"
            >
              <X size={14} />
            </span>
          )}
          <ChevronDown size={16} className="text-text-tertiary" />
        </div>
      </button>

      {open && (
        <div className="absolute z-50 mt-1 w-full rounded-md border border-neutral-bg bg-surface-card shadow-lg">
          <div className="border-b border-neutral-bg p-2">
            <div className="relative">
              <Search
                size={14}
                className="absolute left-2.5 top-1/2 -translate-y-1/2 text-text-tertiary"
              />
              <input
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search states..."
                className="h-8 w-full rounded border border-neutral-bg bg-transparent pl-8 pr-3 text-xs text-text-primary placeholder:text-text-tertiary focus:border-primary-300 focus:outline-none"
                autoFocus
              />
            </div>
          </div>

          <ul className="max-h-56 overflow-y-auto py-1">
            {filtered.length === 0 ? (
              <li className="px-3 py-2 text-xs text-text-tertiary">No states found</li>
            ) : (
              filtered.map((state) => (
                <li key={state.code}>
                  <button
                    type="button"
                    onClick={() => handleSelect(state.code)}
                    className={`flex w-full items-center gap-2 px-3 py-1.5 text-left text-xs transition-colors hover:bg-primary-50 ${
                      value === state.code ? "bg-primary-50 font-medium text-primary-600" : "text-text-primary"
                    }`}
                  >
                    <span className="w-6 shrink-0 font-mono text-text-tertiary">{state.code}</span>
                    <span>{state.name}</span>
                    <span className="ml-auto rounded-full bg-neutral-bg px-1.5 py-0.5 text-[10px] text-text-tertiary">
                      {state.zone}
                    </span>
                  </button>
                </li>
              ))
            )}
          </ul>
        </div>
      )}
    </div>
  );
});
