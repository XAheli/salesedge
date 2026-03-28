function escapeCsvCell(value: unknown): string {
  if (value === null || value === undefined) {
    return "";
  }
  const s = String(value);
  if (/[",\n\r]/.test(s)) {
    return `"${s.replace(/"/g, '""')}"`;
  }
  return s;
}

export function exportToCSV<T extends Record<string, unknown>>(
  data: T[],
  columns: { key: keyof T; header: string }[],
  filename: string,
): void {
  if (!columns.length) {
    throw new Error("exportToCSV: at least one column is required");
  }
  const headerLine = columns.map((c) => escapeCsvCell(c.header)).join(",");
  const lines = data.map((row) =>
    columns.map((c) => escapeCsvCell(row[c.key])).join(","),
  );
  const csv = [headerLine, ...lines].join("\r\n");
  const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename.endsWith(".csv") ? filename : `${filename}.csv`;
  a.rel = "noopener";
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

export interface ExportPngOptions {
  backgroundColor?: string | null;
  scale?: number;
}

export async function exportToPNG(
  element: HTMLElement | null,
  filename: string,
  options: ExportPngOptions = {},
): Promise<void> {
  if (!element) {
    throw new Error("exportToPNG: element ref is required");
  }

  const { default: html2canvas } = await import("html2canvas");

  const canvas = await html2canvas(element, {
    useCORS: true,
    allowTaint: true,
    scale: options.scale ?? (window.devicePixelRatio > 1 ? 2 : 1),
    backgroundColor: options.backgroundColor ?? "#ffffff",
    logging: false,
  });

  await new Promise<void>((resolve, reject) => {
    canvas.toBlob(
      (blob) => {
        if (!blob) {
          reject(new Error("exportToPNG: could not create image blob"));
          return;
        }
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = filename.endsWith(".png") ? filename : `${filename}.png`;
        a.rel = "noopener";
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        resolve();
      },
      "image/png",
      0.95,
    );
  });
}
