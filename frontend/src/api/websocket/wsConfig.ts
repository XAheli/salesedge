const DEFAULT_WS_ORIGIN = "ws://localhost:8000";

function getDefaultWsFromWindow(): string | null {
  if (typeof window === "undefined") {
    return null;
  }
  const { protocol, hostname, port } = window.location;
  const wsProtocol = protocol === "https:" ? "wss" : "ws";
  const targetPort = port === "5173" ? "8000" : port;
  const hostPort = targetPort ? `${hostname}:${targetPort}` : hostname;
  return `${wsProtocol}://${hostPort}`;
}

export function getWebSocketBaseUrl(): string {
  const env = import.meta.env.VITE_WS_URL;
  if (typeof env === "string" && env.length > 0) {
    return env.replace(/\/$/, "");
  }
  const dynamicDefault = getDefaultWsFromWindow();
  if (dynamicDefault) {
    return dynamicDefault;
  }
  return DEFAULT_WS_ORIGIN;
}

export function buildWebSocketUrl(path: string): string {
  const base = getWebSocketBaseUrl();
  const normalizedPath = path.startsWith("/") ? path : `/${path}`;
  return `${base}${normalizedPath}`;
}
