import { useState, useMemo, useCallback } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  Search,
  Download,
  ChevronLeft,
  ChevronRight,
  ChevronsLeft,
  ChevronsRight,
  ArrowUp,
  ArrowDown,
  MapPin,
  RefreshCw,
  AlertTriangle,
} from "lucide-react";
import {
  useProspectList,
  type ProspectListItem,
} from "@/api/hooks/useProspects";
import { formatRelativeTime } from "@/utils/date-helpers";
import { SkeletonTable } from "@/components/data-display/LoadingSkeleton";
import { ErrorBoundary } from "@/components/shared/ErrorBoundary";
import { FilterBar } from "@/components/shared/FilterBar";
import { exportToCSV } from "@/utils/export";

type SortField =
  | "company_name"
  | "industry"
  | "state"
  | "fit_score"
  | "employee_count";
type SortDir = "asc" | "desc";

function fitScoreColor(score: number): string {
  if (score >= 85) return "bg-revenue-positive text-white";
  if (score >= 70) return "bg-caution text-white";
  if (score >= 50) return "bg-amber-400 text-white";
  return "bg-risk text-white";
}

function SortHeader({
  label,
  field,
  current,
  direction,
  onSort,
  className = "",
}: {
  label: string;
  field: SortField;
  current: SortField;
  direction: SortDir;
  onSort: (f: SortField) => void;
  className?: string;
}) {
  const active = current === field;
  return (
    <th
      className={`cursor-pointer select-none px-4 py-3 font-medium text-text-secondary hover:text-text-primary ${className}`}
      onClick={() => onSort(field)}
    >
      <span className="inline-flex items-center gap-1">
        {label}
        {active &&
          (direction === "asc" ? (
            <ArrowUp size={12} />
          ) : (
            <ArrowDown size={12} />
          ))}
      </span>
    </th>
  );
}

export default function Prospects() {
  const [localSearch, setLocalSearch] = useState("");
  const [sortBy, setSortBy] = useState<SortField>("company_name");
  const [sortDir, setSortDir] = useState<SortDir>("asc");
  const [page, setPage] = useState(1);
  const pageSize = 25;

  const { data, isLoading, error, refetch } = useProspectList({
    page,
    page_size: pageSize,
    sort_by: sortBy,
    sort_order: sortDir,
  });

  const prospects = data?.items ?? [];
  const totalItems = data?.total ?? 0;
  const totalPages = data?.pages ?? 1;

  const filtered = useMemo(() => {
    if (!localSearch.trim()) return prospects;
    const q = localSearch.toLowerCase();
    return prospects.filter(
      (p) =>
        p.company_name.toLowerCase().includes(q) ||
        p.industry.toLowerCase().includes(q) ||
        p.state.toLowerCase().includes(q),
    );
  }, [prospects, localSearch]);

  const handleSort = useCallback(
    (field: SortField) => {
      if (sortBy === field) {
        setSortDir((d) => (d === "asc" ? "desc" : "asc"));
      } else {
        setSortBy(field);
        setSortDir(
          field === "fit_score" || field === "employee_count" ? "desc" : "asc",
        );
      }
      setPage(1);
    },
    [sortBy],
  );

  if (error) {
    return (
      <div className="flex min-h-[400px] flex-col items-center justify-center rounded-lg bg-surface-card p-8 text-center shadow-card">
        <AlertTriangle className="h-8 w-8 text-risk" />
        <h2 className="mt-4 font-display text-lg font-semibold text-text-primary">
          Failed to load prospects
        </h2>
        <p className="mt-2 text-sm text-text-secondary">
          {(error as Error).message}
        </p>
        <button
          onClick={() => refetch()}
          className="mt-4 inline-flex items-center gap-2 rounded-lg bg-primary-500 px-4 py-2 text-sm font-semibold text-white hover:bg-primary-600"
        >
          <RefreshCw size={16} /> Retry
        </button>
      </div>
    );
  }

  return (
    <ErrorBoundary>
      <div className="space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h2 className="text-lg font-semibold text-text-primary">
              Prospect Intelligence
            </h2>
            <p className="text-sm text-text-tertiary">
              {totalItems} companies tracked · Fit scores powered by government
              + market data
            </p>
          </div>
          <button
            className="flex items-center gap-1.5 rounded-lg border border-neutral-bg px-3 py-2 text-xs font-medium text-text-secondary hover:bg-neutral-bg"
            onClick={() =>
              exportToCSV(
                filtered as unknown as Record<string, unknown>[],
                [
                  { key: "company_name", header: "Company Name" },
                  { key: "industry", header: "Industry" },
                  { key: "state", header: "State" },
                  { key: "employee_count", header: "Employees" },
                ],
                "prospects",
              )
            }
          >
            <Download size={14} /> Export
          </button>
        </div>

        <FilterBar />

        <div className="relative">
          <Search
            size={16}
            className="absolute left-3 top-1/2 -translate-y-1/2 text-text-tertiary"
          />
          <input
            type="text"
            placeholder="Search by company, industry, or state..."
            value={localSearch}
            onChange={(e) => setLocalSearch(e.target.value)}
            className="h-10 w-full rounded-lg border border-neutral-bg bg-surface-card pl-10 pr-4 text-sm text-text-primary placeholder:text-text-tertiary focus:border-primary-300 focus:outline-none"
          />
        </div>

        {isLoading ? (
          <SkeletonTable rows={10} cols={7} />
        ) : (
          <div className="card overflow-hidden">
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="border-b border-neutral-bg bg-neutral-bg/50">
                  <SortHeader
                    label="Company"
                    field="company_name"
                    current={sortBy}
                    direction={sortDir}
                    onSort={handleSort}
                  />
                  <SortHeader
                    label="Industry"
                    field="industry"
                    current={sortBy}
                    direction={sortDir}
                    onSort={handleSort}
                  />
                  <SortHeader
                    label="State"
                    field="state"
                    current={sortBy}
                    direction={sortDir}
                    onSort={handleSort}
                  />
                  <SortHeader
                    label="Employees"
                    field="employee_count"
                    current={sortBy}
                    direction={sortDir}
                    onSort={handleSort}
                    className="text-right"
                  />
                  <th className="px-4 py-3 font-medium text-text-secondary">
                    Revenue Band
                  </th>
                  <SortHeader
                    label="Fit Score"
                    field="fit_score"
                    current={sortBy}
                    direction={sortDir}
                    onSort={handleSort}
                    className="text-center"
                  />
                  <th className="px-4 py-3 font-medium text-text-secondary">
                    Last Enriched
                  </th>
                </tr>
              </thead>
              <tbody>
                {filtered.length === 0 ? (
                  <tr>
                    <td
                      colSpan={7}
                      className="px-4 py-12 text-center text-sm text-text-tertiary"
                    >
                      No prospects found
                    </td>
                  </tr>
                ) : (
                  filtered.map((p) => <ProspectRow key={p.id} prospect={p} />)
                )}
              </tbody>
            </table>
          </div>
        )}

        {totalPages > 1 && (
          <div className="flex items-center justify-between px-1">
            <p className="text-xs text-text-tertiary">
              Page {page} of {totalPages} · {totalItems} total
            </p>
            <div className="flex items-center gap-1">
              <PaginationBtn
                disabled={page <= 1}
                onClick={() => setPage(1)}
                label="First"
              >
                <ChevronsLeft size={14} />
              </PaginationBtn>
              <PaginationBtn
                disabled={page <= 1}
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                label="Previous"
              >
                <ChevronLeft size={14} />
              </PaginationBtn>
              <PaginationBtn
                disabled={page >= totalPages}
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                label="Next"
              >
                <ChevronRight size={14} />
              </PaginationBtn>
              <PaginationBtn
                disabled={page >= totalPages}
                onClick={() => setPage(totalPages)}
                label="Last"
              >
                <ChevronsRight size={14} />
              </PaginationBtn>
            </div>
          </div>
        )}
      </div>
    </ErrorBoundary>
  );
}

function ProspectRow({ prospect: p }: { prospect: ProspectListItem }) {
  const navigate = useNavigate();

  return (
    <tr
      className="cursor-pointer border-b border-neutral-bg/50 transition-colors hover:bg-primary-50/50"
      onClick={() => navigate(`/prospects/${p.id}`)}
    >
      <td className="px-4 py-3">
        <Link
          to={`/prospects/${p.id}`}
          className="font-medium text-text-primary hover:text-primary-600"
          onClick={(e) => e.stopPropagation()}
        >
          {p.company_name}
        </Link>
        {p.nic_code && (
          <span className="ml-2 text-xs text-text-tertiary">
            NIC:{p.nic_code}
          </span>
        )}
      </td>
      <td className="px-4 py-3 text-text-secondary">{p.industry}</td>
      <td className="px-4 py-3">
        <span className="flex items-center gap-1 text-text-secondary">
          <MapPin size={12} /> {p.state}
        </span>
      </td>
      <td className="px-4 py-3 text-right font-medium text-text-primary">
        {p.employee_count != null
          ? p.employee_count.toLocaleString("en-IN")
          : "—"}
      </td>
      <td className="px-4 py-3 text-text-secondary">
        {p.revenue_band_inr ?? "—"}
      </td>
      <td className="px-4 py-3 text-center">
        {p.fit_score != null ? (
          <span
            className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold ${fitScoreColor(p.fit_score)}`}
          >
            {p.fit_score}
          </span>
        ) : (
          <span className="text-xs text-text-tertiary">N/A</span>
        )}
      </td>
      <td className="px-4 py-3 text-xs text-text-tertiary">
        {p.last_enriched ? formatRelativeTime(p.last_enriched) : "—"}
      </td>
    </tr>
  );
}

function PaginationBtn({
  disabled,
  onClick,
  label,
  children,
}: {
  disabled: boolean;
  onClick: () => void;
  label: string;
  children: React.ReactNode;
}) {
  return (
    <button
      disabled={disabled}
      onClick={onClick}
      aria-label={label}
      className="flex h-8 w-8 items-center justify-center rounded-md border border-neutral-bg text-text-secondary transition-colors hover:bg-neutral-bg disabled:cursor-not-allowed disabled:opacity-40"
    >
      {children}
    </button>
  );
}
