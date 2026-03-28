import { useCallback, useEffect, useRef, useState } from "react";
import { buildWebSocketUrl } from "./wsConfig";

export type DealRiskAlertSeverity = "low" | "medium" | "high" | "critical";

export interface DealRiskAlert {
  id: string;
  deal_id: string;
  deal_name: string;
  message: string;
  severity: DealRiskAlertSeverity;
  created_at: string;
  acknowledged?: boolean;
}

const WS_PATH = "/ws/alerts";
const INITIAL_DELAY_MS = 1_000;
const MAX_DELAY_MS = 60_000;

function parseAlertMessage(raw: unknown): DealRiskAlert | null {
  if (!raw || typeof raw !== "object") {
    return null;
  }
  const o = raw as Record<string, unknown>;
  if (
    typeof o.id === "string" &&
    typeof o.deal_id === "string" &&
    typeof o.message === "string" &&
    typeof o.created_at === "string"
  ) {
    return {
      id: o.id,
      deal_id: o.deal_id,
      deal_name: typeof o.deal_name === "string" ? o.deal_name : "Deal",
      message: o.message,
      severity:
        o.severity === "low" ||
        o.severity === "medium" ||
        o.severity === "high" ||
        o.severity === "critical"
          ? o.severity
          : "medium",
      created_at: o.created_at,
      acknowledged: Boolean(o.acknowledged),
    };
  }
  return null;
}

export interface UseAlertsResult {
  alerts: DealRiskAlert[];
  isConnected: boolean;
  connectionError: Error | null;
  clearAlerts: () => void;
}

export function useAlerts(enabled: boolean = true): UseAlertsResult {
  const [alerts, setAlerts] = useState<DealRiskAlert[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [connectionError, setConnectionError] = useState<Error | null>(null);

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectAttempt = useRef(0);
  const reconnectTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const shouldConnect = useRef(enabled);

  const clearAlerts = useCallback(() => setAlerts([]), []);

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

          if (Array.isArray(payload)) {
            const next = payload
              .map((item) => parseAlertMessage(item))
              .filter((x): x is DealRiskAlert => x !== null);
            if (next.length) {
              setAlerts((prev) => [...next, ...prev].slice(0, 200));
            }
            return;
          }

          if (payload && typeof payload === "object" && "alerts" in payload) {
            const list = (payload as { alerts: unknown }).alerts;
            if (Array.isArray(list)) {
              const next = list
                .map((item) => parseAlertMessage(item))
                .filter((x): x is DealRiskAlert => x !== null);
              if (next.length) {
                setAlerts((prev) => [...next, ...prev].slice(0, 200));
              }
            }
            return;
          }

          const single = parseAlertMessage(payload);
          if (single) {
            setAlerts((prev) => [single, ...prev].slice(0, 200));
          }
        } catch {
          setConnectionError(new Error("Failed to parse alert message"));
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

  return { alerts, isConnected, connectionError, clearAlerts };
}
