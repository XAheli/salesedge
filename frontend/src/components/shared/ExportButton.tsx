import { useCallback, useState, type RefObject } from "react";
import * as DropdownMenu from "@radix-ui/react-dropdown-menu";
import { Download } from "lucide-react";
import clsx from "clsx";
import { exportToCSV, exportToPNG } from "@/utils/export";
import { toast } from "sonner";

export interface ExportColumn<T extends Record<string, unknown>> {
  key: keyof T;
  header: string;
}

export interface ExportButtonProps<T extends Record<string, unknown>> {
  data: T[];
  columns: ExportColumn<T>[];
  /** Used for PNG capture (chart or card root). */
  captureRef: RefObject<HTMLElement | null>;
  filenameBase?: string;
  className?: string;
  /** XLSX export requires a backend or sheet library — disabled by default. */
  xlsxAvailable?: boolean;
  onExportXlsx?: () => void | Promise<void>;
}

export function ExportButton<T extends Record<string, unknown>>({
  data,
  columns,
  captureRef,
  filenameBase = "export",
  className,
  xlsxAvailable = false,
  onExportXlsx,
}: ExportButtonProps<T>) {
  const [pngBusy, setPngBusy] = useState(false);

  const onCsv = useCallback(() => {
    try {
      if (!data.length) {
        toast.message("Nothing to export", { description: "Add data before exporting CSV." });
        return;
      }
      exportToCSV(data, columns, filenameBase);
      toast.success("CSV downloaded");
    } catch (e) {
      toast.error("CSV export failed", {
        description: e instanceof Error ? e.message : "Unknown error",
      });
    }
  }, [columns, data, filenameBase]);

  const onPng = useCallback(async () => {
    setPngBusy(true);
    try {
      await exportToPNG(captureRef.current, filenameBase, {
        backgroundColor: null,
      });
      toast.success("PNG downloaded");
    } catch (e) {
      toast.error("PNG export failed", {
        description: e instanceof Error ? e.message : "Unknown error",
      });
    } finally {
      setPngBusy(false);
    }
  }, [captureRef, filenameBase]);

  const onXlsx = useCallback(async () => {
    if (!xlsxAvailable || !onExportXlsx) {
      return;
    }
    try {
      await onExportXlsx();
      toast.success("Spreadsheet export started");
    } catch (e) {
      toast.error("XLSX export failed", {
        description: e instanceof Error ? e.message : "Unknown error",
      });
    }
  }, [onExportXlsx, xlsxAvailable]);

  return (
    <DropdownMenu.Root>
      <DropdownMenu.Trigger asChild>
        <button
          type="button"
          className={clsx(
            "inline-flex h-9 items-center gap-2 rounded-lg border border-neutral-bg bg-surface-card px-3 text-sm font-medium text-text-primary hover:bg-neutral-bg/60",
            className,
          )}
          aria-label="Export"
        >
          <Download className="h-4 w-4" aria-hidden />
          Export
        </button>
      </DropdownMenu.Trigger>
      <DropdownMenu.Portal>
        <DropdownMenu.Content
          className="z-50 min-w-[10rem] rounded-lg border border-neutral-bg bg-surface-card p-1 shadow-lg"
          sideOffset={4}
          align="end"
        >
          <DropdownMenu.Item
            className="cursor-pointer rounded-md px-2 py-2 text-sm outline-none hover:bg-neutral-bg"
            onSelect={(e) => {
              e.preventDefault();
              onCsv();
            }}
          >
            Download CSV
          </DropdownMenu.Item>
          <DropdownMenu.Item
            className="cursor-pointer rounded-md px-2 py-2 text-sm outline-none hover:bg-neutral-bg disabled:opacity-40"
            disabled={pngBusy}
            onSelect={async (e) => {
              e.preventDefault();
              await onPng();
            }}
          >
            {pngBusy ? "Preparing PNG…" : "Download PNG"}
          </DropdownMenu.Item>
          <DropdownMenu.Item
            className="cursor-pointer rounded-md px-2 py-2 text-sm outline-none hover:bg-neutral-bg disabled:opacity-40"
            disabled={!xlsxAvailable}
            onSelect={(e) => {
              e.preventDefault();
              void onXlsx();
            }}
          >
            Download XLSX {!xlsxAvailable ? "(unavailable)" : ""}
          </DropdownMenu.Item>
        </DropdownMenu.Content>
      </DropdownMenu.Portal>
    </DropdownMenu.Root>
  );
}
