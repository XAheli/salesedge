import { memo, useMemo } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import { ChartContainer } from "./ChartContainer";

export interface OutreachChannel {
  name: string;
  openRate: number;
  replyRate: number;
  meetingBookedRate: number;
}

interface OutreachPerformanceProps {
  data: OutreachChannel[];
  loading?: boolean;
  error?: string | null;
  className?: string;
}

const COLORS = {
  openRate: "#F97316",
  replyRate: "#059669",
  meetingBookedRate: "#2563EB",
} as const;

function pctFmt(v: number): string {
  return `${v.toFixed(1)}%`;
}

export const OutreachPerformance = memo(function OutreachPerformance({
  data,
  loading,
  error,
  className = "",
}: OutreachPerformanceProps) {
  const isEmpty = !loading && !error && data.length === 0;

  const textSummary = useMemo(() => {
    if (!data.length) return "No outreach data available.";
    return data
      .map(
        (d) =>
          `${d.name}: Open ${pctFmt(d.openRate)}, Reply ${pctFmt(d.replyRate)}, Meetings ${pctFmt(d.meetingBookedRate)}`,
      )
      .join(". ");
  }, [data]);

  return (
    <ChartContainer
      title="Outreach Performance"
      subtitle="Open, reply, and meeting-booked rates by channel"
      loading={loading}
      error={error}
      empty={isEmpty}
      emptyMessage="No outreach sequence data"
      className={className}
    >
      <ResponsiveContainer width="100%" height={320}>
        <BarChart data={data} margin={{ top: 8, right: 12, bottom: 4, left: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#F3F4F6" />
          <XAxis
            dataKey="name"
            tick={{ fontSize: 11, fill: "#57534E" }}
            axisLine={{ stroke: "#F3F4F6" }}
            tickLine={false}
          />
          <YAxis
            tick={{ fontSize: 11, fill: "#57534E" }}
            axisLine={false}
            tickLine={false}
            tickFormatter={pctFmt}
            domain={[0, 100]}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: "#FFFFFF",
              border: "1px solid #F3F4F6",
              borderRadius: 8,
              fontSize: 12,
            }}
            formatter={(value: number, name: string) => {
              const labels: Record<string, string> = {
                openRate: "Open Rate",
                replyRate: "Reply Rate",
                meetingBookedRate: "Meetings Booked",
              };
              return [pctFmt(value), labels[name] ?? name];
            }}
          />
          <Legend
            wrapperStyle={{ fontSize: 10, paddingTop: 8 }}
            formatter={(value: string) => {
              const labels: Record<string, string> = {
                openRate: "Open Rate",
                replyRate: "Reply Rate",
                meetingBookedRate: "Meetings Booked",
              };
              return labels[value] ?? value;
            }}
          />
          <Bar dataKey="openRate" fill={COLORS.openRate} radius={[4, 4, 0, 0]} barSize={20} />
          <Bar dataKey="replyRate" fill={COLORS.replyRate} radius={[4, 4, 0, 0]} barSize={20} />
          <Bar dataKey="meetingBookedRate" fill={COLORS.meetingBookedRate} radius={[4, 4, 0, 0]} barSize={20} />
        </BarChart>
      </ResponsiveContainer>

      <details className="mt-3 text-xs text-text-secondary">
        <summary className="cursor-pointer font-medium">View as text</summary>
        <p className="mt-1">{textSummary}</p>
      </details>
    </ChartContainer>
  );
});

export default OutreachPerformance;
