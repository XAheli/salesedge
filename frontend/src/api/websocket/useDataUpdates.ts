import { useEffect, useRef, useState } from "react";
import { buildWebSocketUrl } from "./wsConfig";

export interface DataFreshnessUpdate {
  source_id: string;
  source_name: string;
  updated_at: string;
  record_count: number | null;
  event_type: "refresh" | "incremental" | "snapshot";
}

const WS_PATH = "/ws/data-updates";
const INITIAL_DELAY_MS = 1_000;
const MAX_DELAY_MS = 60_000;

function parseUpdate(raw: unknown): DataFreshnessUpdate | null {
  if (!raw || typeof raw !== "object") {
    return null;
  }
  const o = raw as Record<string, unknown>;
  if (typeof o.source_id === "string" && typeof o.updated_at === "string") {
    return {
      source_id: o.source_id,
      source_name: typeof o.source_name === "string" ? o.source_name : o.source_id,
      updated_at: o.updated_at,
      record_count: typeof o.record_count === "number" ? o.record_count : null,
      event_type:
        o.event_type === "refresh" || o.event_type === "incremental" || o.event_type === "snapshot"
          ? o.event_type
          : "refresh",
    };
  }
  return null;
}

export interface UseDataUpdatesResult {
  latestUpdate: DataFreshnessUpdate | null;
  staleSources: string[];
  isConnected: boolean;
  connectionError: Error | null;
}

export function useDataUpdates(enabled: boolean = true): UseDataUpdatesResult {
  const [latestUpdate, setLatestUpdate] = useState<DataFreshnessUpdate | null>(null);
  const [staleSources, setStaleSources] = useState<string[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [connectionError, setConnectionError] = useState<Error | null>(null);

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectAttempt = useRef(0);
  const reconnectTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const shouldConnect = useRef(enabled);

  useEffect(() => {
    shouldConnect.current = enabled;
    if (!enabled) {
      if (reconnectTimer.current) {
        clearTimeout(reconnectTimer.current);
        reconnectTimer.current = null;
      }
      wsRef.current?.close();
      wsRef.current = null;
      setIsConnected(false);
      return;
    }

    const connect = () => {
      if (!shouldConnect.current) {
        return;
      }

      const url = buildWebSocketUrl(WS_PATH);
      let socket: WebSocket;
      try {
        socket = new WebSocket(url);
      } catch (e) {
        setConnectionError(e instanceof Error ? e : new Error("WebSocket construction failed"));
        scheduleReconnect();
        return;
      }

      wsRef.current = socket;

      socket.onopen = () => {
        reconnectAttempt.current = 0;
        setConnectionError(null);
        setIsConnected(true);
      };

      socket.onclose = () => {
        setIsConnected(false);
        wsRef.current = null;
        if (shouldConnect.current) {
          scheduleReconnect();
        }
      };

      socket.onerror = () => {
        setConnectionError(new Error("WebSocket connection error"));
      };

      socket.onmessage = (event) => {
        try {
          const payload = JSON.parse(event.data as string) as unknown;

          if (payload && typeof payload === "object" && "stale_sources" in payload) {
            const stale = (payload as { stale_sources: unknown }).stale_sources;
            if (Array.isArray(stale) && stale.every((s) => typeof s === "string")) {
              setStaleSources(stale as string[]);
            }
          }

          if (payload && typeof payload === "object" && "update" in payload) {
            const u = parseUpdate((payload as { update: unknown }).update);
            if (u) {
              setLatestUpdate(u);
            }
            return;
          }

          const single = parseUpdate(payload);
          if (single) {
            setLatestUpdate(single);
          }
        } catch {
          setConnectionError(new Error("Failed to parse data update message"));
        }
      };
    };

    const scheduleReconnect = () => {
      if (!shouldConnect.current || reconnectTimer.current) {
        return;
      }
      const exp = Math.min(
        MAX_DELAY_MS,
        INITIAL_DELAY_MS * Math.pow(2, reconnectAttempt.current),
      );
      reconnectAttempt.current += 1;
      reconnectTimer.current = setTimeout(() => {
        reconnectTimer.current = null;
        connect();
      }, exp);
    };

    connect();

    return () => {
      shouldConnect.current = false;
      if (reconnectTimer.current) {
        clearTimeout(reconnectTimer.current);
        reconnectTimer.current = null;
      }
      wsRef.current?.close();
      wsRef.current = null;
      setIsConnected(false);
    };
  }, [enabled]);

  return { latestUpdate, staleSources, isConnected, connectionError };
}
