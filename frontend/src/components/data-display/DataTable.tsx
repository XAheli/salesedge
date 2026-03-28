import { useState, useMemo, useCallback, memo } from "react";
import {
  useReactTable,
  getCoreRowModel,
  getSortedRowModel,
  getPaginationRowModel,
  getFilteredRowModel,
  flexRender,
  type ColumnDef,
  type SortingState,
  type ColumnFiltersState,
} from "@tanstack/react-table";
import {
  ArrowUpDown,
  ArrowUp,
  ArrowDown,
  ChevronLeft,
  ChevronRight,
  ChevronsLeft,
  ChevronsRight,
  Download,
} from "lucide-react";
import { formatINR } from "@/utils/indian-formatting";
import { formatIST } from "@/utils/indian-formatting";
import { LoadingSkeleton } from "./LoadingSkeleton";
import { EmptyState } from "./EmptyState";

export interface DataTableProps<T> {
  data: T[];
  columns: ColumnDef<T, unknown>[];
  pagination?: boolean;
  pageSize?: number;
  sorting?: boolean;
  filters?: boolean;
  onRowClick?: (row: T) => void;
  exportOptions?: ("csv" | "json")[];
  emptyState?: { title: string; description?: string };
  loading?: boolean;
  currencyColumns?: string[];
  dateColumns?: string[];
  className?: string;
}

function exportCSV<T>(data: T[], columns: ColumnDef<T, unknown>[]) {
  const headers = columns
    .map((c) => (typeof c.header === "string" ? c.header : String((c as { accessorKey?: string }).accessorKey ?? "")))
    .join(",");
  const rows = data.map((row) =>
    columns
      .map((c) => {
        const key = (c as { accessorKey?: string }).accessorKey;
        if (!key) return "";
        const val = (row as Record<string, unknown>)[key];
        const str = String(val ?? "");
        return str.includes(",") ? `"${str}"` : str;
      })
      .join(","),
  );
  const csv = [headers, ...rows].join("\n");
  const blob = new Blob([csv], { type: "text/csv" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "export.csv";
  a.click();
  URL.revokeObjectURL(url);
}

function exportJSON<T>(data: T[]) {
  const blob = new Blob([JSON.stringify(data, null, 2)], {
    type: "application/json",
  });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "export.json";
  a.click();
  URL.revokeObjectURL(url);
}

function DataTableInner<T>({
  data,
  columns,
  pagination = true,
  pageSize = 10,
  sorting = true,
  onRowClick,
  exportOptions,
  emptyState,
  loading = false,
  currencyColumns = [],
  dateColumns = [],
  className = "",
}: DataTableProps<T>) {
  const [sortingState, setSortingState] = useState<SortingState>([]);
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);
  const [globalFilter, setGlobalFilter] = useState("");

  const processedColumns = useMemo(() => {
    return columns.map((col) => {
      const key = (col as { accessorKey?: string }).accessorKey;
      if (!key) return col;

      if (currencyColumns.includes(key) && !col.cell) {
        return {
          ...col,
          cell: ({ getValue }: { getValue: () => unknown }) => {
            const val = getValue();
            return typeof val === "number" ? formatINR(val, { compact: true }) : String(val ?? "");
          },
        };
      }

      if (dateColumns.includes(key) && !col.cell) {
        return {
          ...col,
          cell: ({ getValue }: { getValue: () => unknown }) => {
            const val = getValue();
            return typeof val === "string" ? formatIST(val, "date") : String(val ?? "");
          },
        };
      }

      return col;
    });
  }, [columns, currencyColumns, dateColumns]);

  const table = useReactTable({
    data,
    columns: processedColumns,
    state: { sorting: sortingState, columnFilters, globalFilter },
    onSortingChange: setSortingState,
    onColumnFiltersChange: setColumnFilters,
    onGlobalFilterChange: setGlobalFilter,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: sorting ? getSortedRowModel() : undefined,
    getPaginationRowModel: pagination ? getPaginationRowModel() : undefined,
    getFilteredRowModel: getFilteredRowModel(),
    initialState: { pagination: { pageSize } },
  });

  const handleExport = useCallback(
    (format: "csv" | "json") => {
      if (format === "csv") exportCSV(data, columns);
      else exportJSON(data);
    },
    [data, columns],
  );

  if (loading) {
    return <LoadingSkeleton variant="table" rows={pageSize} />;
  }

  if (!data.length) {
    return (
      <EmptyState
        title={emptyState?.title ?? "No data available"}
        description={emptyState?.description}
      />
    );
  }

  return (
    <div className={`rounded-md bg-surface-card shadow-card ${className}`}>
      <div className="flex items-center justify-between gap-3 border-b border-neutral-bg px-4 py-3">
        <input
          type="text"
          placeholder="Search..."
          value={globalFilter}
          onChange={(e) => setGlobalFilter(e.target.value)}
          className="h-8 w-64 rounded-md border border-neutral-bg bg-transparent px-3 text-sm text-text-primary placeholder:text-text-tertiary focus:border-primary-300 focus:outline-none"
        />
        {exportOptions && exportOptions.length > 0 && (
          <div className="flex gap-1">
            {exportOptions.map((fmt) => (
              <button
                key={fmt}
                onClick={() => handleExport(fmt)}
                className="inline-flex items-center gap-1.5 rounded-md border border-neutral-bg px-2.5 py-1.5 text-xs font-medium text-text-secondary transition-colors hover:bg-neutral-bg"
              >
                <Download size={12} />
                {fmt.toUpperCase()}
              </button>
            ))}
          </div>
        )}
      </div>

      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            {table.getHeaderGroups().map((headerGroup) => (
              <tr key={headerGroup.id} className="border-b border-neutral-bg">
                {headerGroup.headers.map((header) => (
                  <th
                    key={header.id}
                    className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-text-secondary"
                  >
                    {header.isPlaceholder ? null : (
                      <div
                        className={`flex items-center gap-1 ${
                          header.column.getCanSort() ? "cursor-pointer select-none" : ""
                        }`}
                        onClick={header.column.getToggleSortingHandler()}
                      >
                        {flexRender(header.column.columnDef.header, header.getContext())}
                        {header.column.getCanSort() && (
                          <span className="text-text-tertiary">
                            {header.column.getIsSorted() === "asc" ? (
                              <ArrowUp size={14} />
                            ) : header.column.getIsSorted() === "desc" ? (
                              <ArrowDown size={14} />
                            ) : (
                              <ArrowUpDown size={14} />
                            )}
                          </span>
                        )}
                      </div>
                    )}
                  </th>
                ))}
              </tr>
            ))}
          </thead>
          <tbody>
            {table.getRowModel().rows.map((row) => (
              <tr
                key={row.id}
                onClick={() => onRowClick?.(row.original)}
                className={`border-b border-neutral-bg/50 transition-colors last:border-b-0 ${
                  onRowClick ? "cursor-pointer hover:bg-surface-card-hover" : ""
                }`}
              >
                {row.getVisibleCells().map((cell) => (
                  <td
                    key={cell.id}
                    className="px-4 py-3 text-sm text-text-primary"
                  >
                    {flexRender(cell.column.columnDef.cell, cell.getContext())}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {pagination && (
        <div className="flex items-center justify-between border-t border-neutral-bg px-4 py-3">
          <p className="text-xs text-text-tertiary">
            {table.getFilteredRowModel().rows.length} result(s)
          </p>
          <div className="flex items-center gap-1">
            <button
              onClick={() => table.setPageIndex(0)}
              disabled={!table.getCanPreviousPage()}
              className="rounded p-1 text-text-secondary hover:bg-neutral-bg disabled:opacity-30"
            >
              <ChevronsLeft size={16} />
            </button>
            <button
              onClick={() => table.previousPage()}
              disabled={!table.getCanPreviousPage()}
              className="rounded p-1 text-text-secondary hover:bg-neutral-bg disabled:opacity-30"
            >
              <ChevronLeft size={16} />
            </button>
            <span className="px-2 text-xs text-text-secondary">
              {table.getState().pagination.pageIndex + 1} / {table.getPageCount()}
            </span>
            <button
              onClick={() => table.nextPage()}
              disabled={!table.getCanNextPage()}
              className="rounded p-1 text-text-secondary hover:bg-neutral-bg disabled:opacity-30"
            >
              <ChevronRight size={16} />
            </button>
            <button
              onClick={() => table.setPageIndex(table.getPageCount() - 1)}
              disabled={!table.getCanNextPage()}
              className="rounded p-1 text-text-secondary hover:bg-neutral-bg disabled:opacity-30"
            >
              <ChevronsRight size={16} />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export const DataTable = memo(DataTableInner) as typeof DataTableInner;
