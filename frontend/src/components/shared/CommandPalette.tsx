import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import * as Dialog from "@radix-ui/react-dialog";
import { Command } from "cmdk";
import { LayoutDashboard, Target, BarChart3, RefreshCw, Swords, Database, Settings, Search } from "lucide-react";
import { useGlobalSearch } from "@/api/hooks/useSearch";
import { COMMAND_PALETTE_EVENT, GLOBAL_ESCAPE_EVENT } from "@/hooks/useKeyboardShortcuts";
import clsx from "clsx";

const NAV = [
  { label: "Dashboard", path: "/", icon: LayoutDashboard },
  { label: "Prospects", path: "/prospects", icon: Target },
  { label: "Deals", path: "/deals", icon: BarChart3 },
  { label: "Retention", path: "/retention", icon: RefreshCw },
  { label: "Intelligence", path: "/intelligence", icon: Swords },
  { label: "Data & provenance", path: "/data", icon: Database },
  { label: "Settings", path: "/settings", icon: Settings },
] as const;

export function CommandPalette() {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");
  const navigate = useNavigate();
  const search = useGlobalSearch(query);

  useEffect(() => {
    const openPalette = () => {
      setOpen(true);
      setQuery("");
    };
    const onEscapeGlobal = () => setOpen(false);
    window.addEventListener(COMMAND_PALETTE_EVENT, openPalette);
    window.addEventListener(GLOBAL_ESCAPE_EVENT, onEscapeGlobal);
    return () => {
      window.removeEventListener(COMMAND_PALETTE_EVENT, openPalette);
      window.removeEventListener(GLOBAL_ESCAPE_EVENT, onEscapeGlobal);
    };
  }, []);

  const runNavigate = (path: string) => {
    navigate(path);
    setOpen(false);
    setQuery("");
  };

  const hits = search.data?.items ?? [];
  const showResults = query.trim().length >= 2 && !search.isLoading && !search.isError;

  return (
    <Dialog.Root open={open} onOpenChange={setOpen}>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 z-[100] bg-black/40 backdrop-blur-[1px] data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0" />
        <Dialog.Content
          className={clsx(
            "fixed left-1/2 top-[15%] z-[101] w-[min(100vw-2rem,32rem)] -translate-x-1/2",
            "rounded-xl border border-neutral-bg bg-surface-card shadow-xl outline-none",
            "data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0",
          )}
          aria-describedby={undefined}
        >
          <Dialog.Title className="sr-only">Command palette</Dialog.Title>
          <Command
            className="flex max-h-[min(70vh,28rem)] flex-col overflow-hidden rounded-xl"
            shouldFilter={false}
            loop
          >
            <div className="flex items-center gap-2 border-b border-neutral-bg px-3">
              <Search className="h-4 w-4 shrink-0 text-text-tertiary" aria-hidden />
              <Command.Input
                value={query}
                onValueChange={setQuery}
                placeholder="Search pages, actions, or records…"
                className="h-12 w-full bg-transparent text-sm text-text-primary outline-none placeholder:text-text-tertiary"
              />
            </div>
            <Command.List className="max-h-[min(60vh,22rem)] overflow-y-auto p-2 scrollbar-thin">
              <Command.Empty className="py-6 text-center text-sm text-text-tertiary">
                {search.isLoading && query.trim().length >= 2
                  ? "Searching…"
                  : "No matches. Try another query."}
              </Command.Empty>

              <Command.Group
                heading="Navigation"
                className="mb-2 text-xs font-semibold uppercase tracking-wide text-text-tertiary [&_[cmdk-group-heading]]:px-2 [&_[cmdk-group-heading]]:py-1.5"
              >
                {NAV.map(({ label, path, icon: Icon }) => (
                  <Command.Item
                    key={path}
                    value={`nav-${path}`}
                    onSelect={() => runNavigate(path)}
                    className="flex cursor-pointer items-center gap-2 rounded-lg px-2 py-2 text-sm text-text-primary aria-selected:bg-primary-500/10 aria-selected:text-primary-700"
                  >
                    <Icon className="h-4 w-4 shrink-0 opacity-70" aria-hidden />
                    {label}
                  </Command.Item>
                ))}
              </Command.Group>

              <Command.Group
                heading="Actions"
                className="mb-2 text-xs font-semibold uppercase tracking-wide text-text-tertiary [&_[cmdk-group-heading]]:px-2 [&_[cmdk-group-heading]]:py-1.5"
              >
                <Command.Item
                  value="action-new-prospect"
                  onSelect={() => runNavigate("/prospects")}
                  className="flex cursor-pointer items-center gap-2 rounded-lg px-2 py-2 text-sm text-text-primary aria-selected:bg-primary-500/10 aria-selected:text-primary-700"
                >
                  <Target className="h-4 w-4 shrink-0 opacity-70" aria-hidden />
                  Open prospects
                </Command.Item>
                <Command.Item
                  value="action-pipeline"
                  onSelect={() => runNavigate("/deals")}
                  className="flex cursor-pointer items-center gap-2 rounded-lg px-2 py-2 text-sm text-text-primary aria-selected:bg-primary-500/10 aria-selected:text-primary-700"
                >
                  <BarChart3 className="h-4 w-4 shrink-0 opacity-70" aria-hidden />
                  Review pipeline
                </Command.Item>
              </Command.Group>

              {showResults && hits.length > 0 && (
                <Command.Group
                  heading="Search results"
                  className="text-xs font-semibold uppercase tracking-wide text-text-tertiary [&_[cmdk-group-heading]]:px-2 [&_[cmdk-group-heading]]:py-1.5"
                >
                  {hits.map((hit) => (
                    <Command.Item
                      key={`${hit.type}-${hit.id}`}
                      value={`hit-${hit.type}-${hit.id}`}
                      onSelect={() => runNavigate(hit.href)}
                      className="flex cursor-pointer flex-col gap-0.5 rounded-lg px-2 py-2 text-sm text-text-primary aria-selected:bg-primary-500/10 aria-selected:text-primary-700"
                    >
                      <span className="font-medium">{hit.title}</span>
                      {hit.subtitle && (
                        <span className="text-xs text-text-tertiary">{hit.subtitle}</span>
                      )}
                      <span className="text-[10px] uppercase text-text-tertiary">{hit.type}</span>
                    </Command.Item>
                  ))}
                </Command.Group>
              )}

              {search.isError && query.trim().length >= 2 && (
                <p className="px-2 py-2 text-xs text-red-600">
                  Search failed. Check your connection and try again.
                </p>
              )}
            </Command.List>
          </Command>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
}
