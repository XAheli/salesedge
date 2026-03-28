const DEFAULT_WS_ORIGIN = "ws://localhost:8000";

export function getWebSocketBaseUrl(): string {
  const env = import.meta.env.VITE_WS_URL;
  if (typeof env === "string" && env.length > 0) {
    return env.replace(/\/$/, "");
  }
  return DEFAULT_WS_ORIGIN;
}

export function buildWebSocketUrl(path: string): string {
  const base = getWebSocketBaseUrl();
  const normalizedPath = path.startsWith("/") ? path : `/${path}`;
  return `${base}${normalizedPath}`;
}
