"use client";

import { useRef, useEffect, useCallback, useState } from "react";

export type WSReadyState = "connecting" | "open" | "closing" | "closed";

export interface UseWebSocketOptions {
  /** Auto-reconnect with exponential backoff (default true) */
  reconnect?: boolean;
  /** Max reconnect attempts (default 10) */
  maxReconnects?: number;
  /** Base delay in ms for exponential backoff (default 1000) */
  reconnectBaseMs?: number;
  /** Heartbeat interval in ms (default 15000) */
  heartbeatMs?: number;
  /** Called when connection opens */
  onOpen?: (ws: WebSocket) => void;
  /** Called on each message (before handlers) */
  onMessage?: (data: any) => void;
}

export interface UseWebSocketReturn {
  send: (data: any) => void;
  readyState: WSReadyState;
  lastMessage: any;
  connect: () => void;
  disconnect: () => void;
}

function readyStateName(state: number): WSReadyState {
  switch (state) {
    case WebSocket.CONNECTING:
      return "connecting";
    case WebSocket.OPEN:
      return "open";
    case WebSocket.CLOSING:
      return "closing";
    default:
      return "closed";
  }
}

export function useWebSocket<T = any>(
  url: string | (() => string | null),
  handlers: Record<string, (data: T) => void> = {},
  options: UseWebSocketOptions = {}
): UseWebSocketReturn {
  const {
    reconnect = true,
    maxReconnects = 10,
    reconnectBaseMs = 1000,
    heartbeatMs = 15000,
    onOpen,
  } = options;

  const [readyState, setReadyState] = useState<WSReadyState>("closed");
  const [lastMessage, setLastMessage] = useState<any>(null);

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectCountRef = useRef(0);
  const reconnectTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const heartbeatTimerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const intentionalCloseRef = useRef(false);

  const clearTimers = useCallback(() => {
    if (reconnectTimerRef.current) clearTimeout(reconnectTimerRef.current);
    if (heartbeatTimerRef.current) clearInterval(heartbeatTimerRef.current);
  }, []);

  const disconnect = useCallback(() => {
    intentionalCloseRef.current = true;
    clearTimers();
    if (wsRef.current) {
      wsRef.current.close(1000, "Client disconnect");
      wsRef.current = null;
    }
    setReadyState("closed");
    reconnectCountRef.current = 0;
  }, [clearTimers]);

  const connect = useCallback(() => {
    const resolvedUrl = typeof url === "function" ? url() : url;
    if (!resolvedUrl) return;

    intentionalCloseRef.current = false;
    clearTimers();

    // Close existing connection
    if (wsRef.current) {
      wsRef.current.close(1000, "Reconnect");
      wsRef.current = null;
    }

    setReadyState("connecting");
    const ws = new WebSocket(resolvedUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      setReadyState("open");
      reconnectCountRef.current = 0;
      onOpen?.(ws);

      // Heartbeat
      if (heartbeatMs > 0) {
        heartbeatTimerRef.current = setInterval(() => {
          if (ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({ type: "ping" }));
          }
        }, heartbeatMs);
      }
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        setLastMessage(data);

        // Pong — ignore, keep alive
        if (data.type === "pong") return;

        // Route to handler
        const handler = handlers[data.type];
        if (handler) {
          handler(data);
        }

        options.onMessage?.(data);
      } catch {
        // Non-JSON message — ignore
      }
    };

    ws.onclose = (event) => {
      setReadyState("closed");
      clearTimers();

      if (intentionalCloseRef.current) return;

      // Auto-reconnect with exponential backoff
      if (reconnect && reconnectCountRef.current < maxReconnects) {
        const delay = Math.min(
          reconnectBaseMs * Math.pow(2, reconnectCountRef.current),
          30000
        );
        reconnectCountRef.current++;
        reconnectTimerRef.current = setTimeout(() => {
          connect();
        }, delay);
      }
    };

    ws.onerror = () => {
      // onclose will fire after this
    };
  }, [url, handlers, reconnect, maxReconnects, reconnectBaseMs, heartbeatMs, onOpen, clearTimers, options.onMessage]);

  const send = useCallback(
    (data: any) => {
      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        wsRef.current.send(typeof data === "string" ? data : JSON.stringify(data));
      }
    },
    []
  );

  // Connect on mount, disconnect on unmount
  useEffect(() => {
    connect();
    return () => {
      disconnect();
    };
  }, [connect, disconnect]);

  return { send, readyState, lastMessage, connect, disconnect };
}
