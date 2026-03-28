import type { FormatINROptions, IndianNumberUnit } from "@/types/indian-context";

const CRORE = 1_00_00_000;
const LAKH = 1_00_000;
const THOUSAND = 1_000;

export function formatINR(
  amount: number,
  options: FormatINROptions = {},
): string {
  const { compact = false, decimals = 2, showSymbol = true } = options;
  const symbol = showSymbol ? "₹" : "";

  if (compact) {
    const { value, unit } = toIndianUnits(amount);
    const formatted = value.toFixed(decimals).replace(/\.?0+$/, "");
    return `${symbol}${formatted}${unit}`;
  }

  const sign = amount < 0 ? "-" : "";
  const formatted = formatIndianNumber(Math.abs(amount), decimals);
  return `${sign}${symbol}${formatted}`;
}

export function formatIndianNumber(num: number, decimals?: number): string {
  const abs = Math.abs(num);
  const sign = num < 0 ? "-" : "";

  let intPart: string;
  let decPart: string | undefined;

  if (decimals !== undefined && decimals > 0) {
    const fixed = abs.toFixed(decimals);
    const [i, d] = fixed.split(".");
    intPart = i!;
    decPart = d;
  } else {
    intPart = Math.floor(abs).toString();
  }

  if (intPart.length <= 3) {
    return `${sign}${intPart}${decPart ? "." + decPart : ""}`;
  }

  const last3 = intPart.slice(-3);
  let remaining = intPart.slice(0, -3);
  const groups: string[] = [];

  while (remaining.length > 2) {
    groups.unshift(remaining.slice(-2));
    remaining = remaining.slice(0, -2);
  }
  if (remaining.length > 0) {
    groups.unshift(remaining);
  }

  const formatted = groups.join(",") + "," + last3;
  return `${sign}${formatted}${decPart ? "." + decPart : ""}`;
}

export function toIndianUnits(amount: number): { value: number; unit: IndianNumberUnit } {
  const abs = Math.abs(amount);
  const sign = amount < 0 ? -1 : 1;

  if (abs >= CRORE) {
    return { value: sign * (abs / CRORE), unit: "Cr" };
  }
  if (abs >= LAKH) {
    return { value: sign * (abs / LAKH), unit: "L" };
  }
  if (abs >= THOUSAND) {
    return { value: sign * (abs / THOUSAND), unit: "K" };
  }
  return { value: amount, unit: "" };
}

export function fromIndianUnits(value: number, unit: "Cr" | "L" | "K"): number {
  switch (unit) {
    case "Cr":
      return value * CRORE;
    case "L":
      return value * LAKH;
    case "K":
      return value * THOUSAND;
  }
}

const IST_OFFSET_MS = 5.5 * 60 * 60 * 1000;

export function formatIST(
  date: Date | string,
  format: "full" | "date" | "time" | "datetime" = "datetime",
): string {
  const d = typeof date === "string" ? new Date(date) : date;

  const istDate = new Date(d.getTime() + (IST_OFFSET_MS + d.getTimezoneOffset() * 60 * 1000));

  const day = istDate.getDate().toString().padStart(2, "0");
  const monthNames = [
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
  ];
  const month = monthNames[istDate.getMonth()]!;
  const year = istDate.getFullYear();
  const hours = istDate.getHours().toString().padStart(2, "0");
  const minutes = istDate.getMinutes().toString().padStart(2, "0");

  switch (format) {
    case "date":
      return `${day} ${month} ${year}`;
    case "time":
      return `${hours}:${minutes} IST`;
    case "full":
      return `${day} ${month} ${year}, ${hours}:${minutes} IST`;
    case "datetime":
    default:
      return `${day} ${month} ${year} ${hours}:${minutes} IST`;
  }
}

export function getCurrentFY(): string {
  const now = new Date();
  const year = now.getFullYear();
  const month = now.getMonth();

  if (month >= 3) {
    const startYear = year.toString().slice(-2);
    const endYear = (year + 1).toString().slice(-2);
    return `FY ${startYear}-${endYear}`;
  }

  const startYear = (year - 1).toString().slice(-2);
  const endYear = year.toString().slice(-2);
  return `FY ${startYear}-${endYear}`;
}

export function getFYRange(fy: string): { start: Date; end: Date } {
  const match = fy.match(/FY\s*(\d{2,4})-(\d{2,4})/);
  if (!match) {
    throw new Error(`Invalid FY format: "${fy}". Expected "FY YY-YY" or "FY YYYY-YYYY".`);
  }

  let startYear = parseInt(match[1]!, 10);
  if (startYear < 100) {
    startYear += startYear < 50 ? 2000 : 1900;
  }

  return {
    start: new Date(startYear, 3, 1),
    end: new Date(startYear + 1, 2, 31, 23, 59, 59, 999),
  };
}

export const INDIAN_STATES: Record<string, { name: string; code: string; zone: string }> = {
  AN: { name: "Andaman and Nicobar Islands", code: "AN", zone: "south" },
  AP: { name: "Andhra Pradesh", code: "AP", zone: "south" },
  AR: { name: "Arunachal Pradesh", code: "AR", zone: "northeast" },
  AS: { name: "Assam", code: "AS", zone: "northeast" },
  BR: { name: "Bihar", code: "BR", zone: "east" },
  CH: { name: "Chandigarh", code: "CH", zone: "north" },
  CT: { name: "Chhattisgarh", code: "CT", zone: "central" },
  DL: { name: "Delhi", code: "DL", zone: "north" },
  DN: { name: "Dadra and Nagar Haveli and Daman and Diu", code: "DN", zone: "west" },
  GA: { name: "Goa", code: "GA", zone: "west" },
  GJ: { name: "Gujarat", code: "GJ", zone: "west" },
  HP: { name: "Himachal Pradesh", code: "HP", zone: "north" },
  HR: { name: "Haryana", code: "HR", zone: "north" },
  JH: { name: "Jharkhand", code: "JH", zone: "east" },
  JK: { name: "Jammu and Kashmir", code: "JK", zone: "north" },
  KA: { name: "Karnataka", code: "KA", zone: "south" },
  KL: { name: "Kerala", code: "KL", zone: "south" },
  LA: { name: "Ladakh", code: "LA", zone: "north" },
  LD: { name: "Lakshadweep", code: "LD", zone: "south" },
  MH: { name: "Maharashtra", code: "MH", zone: "west" },
  ML: { name: "Meghalaya", code: "ML", zone: "northeast" },
  MN: { name: "Manipur", code: "MN", zone: "northeast" },
  MP: { name: "Madhya Pradesh", code: "MP", zone: "central" },
  MZ: { name: "Mizoram", code: "MZ", zone: "northeast" },
  NL: { name: "Nagaland", code: "NL", zone: "northeast" },
  OD: { name: "Odisha", code: "OD", zone: "east" },
  PB: { name: "Punjab", code: "PB", zone: "north" },
  PY: { name: "Puducherry", code: "PY", zone: "south" },
  RJ: { name: "Rajasthan", code: "RJ", zone: "north" },
  SK: { name: "Sikkim", code: "SK", zone: "northeast" },
  TG: { name: "Telangana", code: "TG", zone: "south" },
  TN: { name: "Tamil Nadu", code: "TN", zone: "south" },
  TR: { name: "Tripura", code: "TR", zone: "northeast" },
  UK: { name: "Uttarakhand", code: "UK", zone: "north" },
  UP: { name: "Uttar Pradesh", code: "UP", zone: "north" },
  WB: { name: "West Bengal", code: "WB", zone: "east" },
};
