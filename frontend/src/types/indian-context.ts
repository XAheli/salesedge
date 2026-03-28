export interface IndianState {
  name: string;
  code: string;
  zone: "north" | "south" | "east" | "west" | "central" | "northeast";
  is_ut: boolean;
}

export interface NICCode {
  code: string;
  section: string;
  division: string;
  description: string;
}

export interface INRAmount {
  raw: number;
  formatted: string;
  compact: string;
  value: number;
  unit: "Cr" | "L" | "K" | "";
}

export interface FYRange {
  label: string;
  start: Date;
  end: Date;
}

export type IndianNumberUnit = "Cr" | "L" | "K" | "";

export interface FormatINROptions {
  compact?: boolean;
  decimals?: number;
  showSymbol?: boolean;
}
