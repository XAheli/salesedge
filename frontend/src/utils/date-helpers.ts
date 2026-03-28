import { formatDistanceToNow } from "date-fns";

const IST_TIMEZONE = "Asia/Kolkata";

interface IndiaParts {
  weekday: string;
  hour: number;
  minute: number;
  month: number;
  day: number;
  year: number;
}

function getPartsInIndia(date: Date): IndiaParts {
  const formatter = new Intl.DateTimeFormat("en-GB", {
    timeZone: IST_TIMEZONE,
    weekday: "short",
    hour: "2-digit",
    minute: "2-digit",
    month: "numeric",
    day: "numeric",
    year: "numeric",
    hour12: false,
  });
  const parts = formatter.formatToParts(date);
  const map: Record<string, string> = {};
  for (const p of parts) {
    if (p.type !== "literal") {
      map[p.type] = p.value;
    }
  }
  return {
    weekday: map.weekday ?? "",
    hour: parseInt(map.hour ?? "0", 10),
    minute: parseInt(map.minute ?? "0", 10),
    month: parseInt(map.month ?? "1", 10) - 1,
    day: parseInt(map.day ?? "1", 10),
    year: parseInt(map.year ?? "1970", 10),
  };
}

export function getIndianMarketHours(): { open: string; close: string } {
  return { open: "09:15", close: "15:30" };
}

export function isIndianMarketOpen(date: Date = new Date()): boolean {
  const { weekday, hour, minute } = getPartsInIndia(date);
  const wd = weekday.slice(0, 3).toLowerCase();
  if (wd === "sat" || wd === "sun") {
    return false;
  }
  const openM = 9 * 60 + 15;
  const closeM = 15 * 60 + 30;
  const nowM = hour * 60 + minute;
  return nowM >= openM && nowM <= closeM;
}

export function isWeekendIndia(date: Date = new Date()): boolean {
  const { weekday } = getPartsInIndia(date);
  const wd = weekday.slice(0, 3).toLowerCase();
  return wd === "sat" || wd === "sun";
}

export function formatRelativeTime(date: Date | string): string {
  const d = typeof date === "string" ? new Date(date) : date;
  if (Number.isNaN(d.getTime())) {
    return "";
  }
  return formatDistanceToNow(d, { addSuffix: true });
}

/**
 * Indian FY: April–March. Labels like "Q1 FY 2025-26".
 */
export function getQuarterLabel(date: Date = new Date()): string {
  const { month, year } = getPartsInIndia(date);
  let fyStartYear: number;
  let quarter: number;

  if (month >= 3 && month <= 5) {
    fyStartYear = year;
    quarter = 1;
  } else if (month >= 6 && month <= 8) {
    fyStartYear = year;
    quarter = 2;
  } else if (month >= 9 && month <= 11) {
    fyStartYear = year;
    quarter = 3;
  } else {
    quarter = 4;
    fyStartYear = year - 1;
  }

  const fyEndShort = String((fyStartYear + 1) % 100).padStart(2, "0");
  const fyStartShort = String(fyStartYear % 100).padStart(2, "0");
  return `Q${quarter} FY ${fyStartYear}-${fyEndShort}`;
}
