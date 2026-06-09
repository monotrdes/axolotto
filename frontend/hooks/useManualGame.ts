"use client";

import { useState, useCallback, useRef } from "react";
import { useWebSocket } from "./useWebSocket";
import { API_BASE } from "@/lib/api";

// ── Types ─────────────────────────────────────────────────────────────────────

export type ManualGamePhase = "connecting" | "countdown" | "playing" | "result";

export interface ManualPlayer {
  axolotito_id: number;
  axo_name: string;
  marked_count?: number;
}

export interface ManualGameState {
  phase: ManualGamePhase;
  error: string | null;
  /** Player's board numbers (4×4 = 16) */
  playerBoardNums: number[];
  /** Active board ID */
  boardId: number | null;
  /** All players in the room */
  players: ManualPlayer[];
  /** Cards called so far (history) */
  cardsCalled: ManualCardEntry[];
  /** Current card being called */
  currentCard: ManualCardEntry | null;
  /** Countdown seconds (0 when YA!) */
  countdownSeconds: number;
  /** Tension data */
  tensionLevel: "low" | "medium" | "high" | "critical";
  nearWinPlayers: number[];
  /** Marked cell indices (player's own board) */
  markedCells: number[];
  /** Hint cells (highlighted cells for current card) */
  hintCells: number[];
  hintsRemaining: number;
  turnsPlayed: number;
  /** Result data */
  winnerAxoId: number | null;
  winnerName: string;
  winType: string;
  payoutFrj: number;
  /** Timing */
  highlightWindowMs: number;
}

export interface ManualCardEntry {
  card_id: number;
  card_number?: number;
  turn: number;
  window_ms: number;
  timestamp_ms: number;
}

export interface UseManualGameOptions {
  roomId: number;
  axolotitoId: number;
  token: string | null;
  /** Callback when game ends */
  onGameEnd?: (winnerAxoId: number | null, payout: number) => void;
}

// ── Build WS URL ──────────────────────────────────────────────────────────────

function buildWsUrl(roomId: number, token: string | null): string | null {
  if (!token) return null;
  const wsBase = API_BASE
    .replace(/^http/, "ws")
    .replace(/\/api\/v1$/, "");
  return `${wsBase}/api/v1/ws/game/${roomId}?token=${encodeURIComponent(token)}`;
}

// ── Hook ──────────────────────────────────────────────────────────────────────

export function useManualGame(options: UseManualGameOptions): ManualGameState & {
  sendMarkCell: (cellIndex: number) => void;
  sendShoutLoteria: () => void;
  sendUseHint: () => void;
  connect: () => void;
  disconnect: () => void;
} {
  const { roomId, axolotitoId, token, onGameEnd } = options;

  // ── State ────────────────────────────────────────────────────────────────
  const [phase, setPhase] = useState<ManualGamePhase>("connecting");
  const [error, setError] = useState<string | null>(null);
  const [playerBoardNums, setPlayerBoardNums] = useState<number[]>(Array(16).fill(0));
  const [boardId, setBoardId] = useState<number | null>(null);
  const [players, setPlayers] = useState<ManualPlayer[]>([]);
  const [cardsCalled, setCardsCalled] = useState<ManualCardEntry[]>([]);
  const [currentCard, setCurrentCard] = useState<ManualCardEntry | null>(null);
  const [countdownSeconds, setCountdownSeconds] = useState(0);
  const [tensionLevel, setTensionLevel] = useState<"low" | "medium" | "high" | "critical">("low");
  const [nearWinPlayers, setNearWinPlayers] = useState<number[]>([]);
  const [markedCells, setMarkedCells] = useState<number[]>([]);
  const [hintCells, setHintCells] = useState<number[]>([]);
  const [hintsRemaining, setHintsRemaining] = useState(3);
  const [turnsPlayed, setTurnsPlayed] = useState(0);
  const [highlightWindowMs, setHighlightWindowMs] = useState(2000);
  const [winnerAxoId, setWinnerAxoId] = useState<number | null>(null);
  const [winnerName, setWinnerName] = useState("");
  const [winType, setWinType] = useState("");
  const [payoutFrj, setPayoutFrj] = useState(0);

  // Track if game ended for cleanup
  const endedRef = useRef(false);

  // ── WS message handlers ──────────────────────────────────────────────────
  const handlers: Record<string, (data: any) => void> = {
    error: (data) => {
      setError(data.message ?? "Error del servidor.");
    },

    player_joined: (data) => {
      setPlayers((prev) => [
        ...prev,
        { axolotito_id: data.axolotito_id, axo_name: data.axo_name },
      ]);
    },

    player_left: (data) => {
      setPlayers((prev) =>
        prev.filter((p) => p.axo_name !== data.axo_name)
      );
    },

    countdown: (data) => {
      setPhase("countdown");
      setCountdownSeconds(data.seconds ?? 0);
    },

    game_start: (data) => {
      setPhase("playing");
      setPlayers(data.players ?? []);
      setHighlightWindowMs(data.highlight_window_ms ?? 2000);
    },

    card_called: (data) => {
      const entry: ManualCardEntry = {
        card_id: data.card_id,
        card_number: data.card_number,
        turn: data.turn,
        window_ms: data.window_ms,
        timestamp_ms: data.timestamp_ms,
      };
      setCurrentCard(entry);
      setCardsCalled((prev) => [...prev, entry]);
      setHintCells([]); // Clear previous hints
    },

    tension_update: (data) => {
      setTensionLevel(data.level ?? "low");
      setNearWinPlayers(data.near_win ?? []);
    },

    cell_marked: (data) => {
      setMarkedCells((prev) =>
        prev.includes(data.cell_index) ? prev : [...prev, data.cell_index]
      );
    },

    hint_activated: (data) => {
      setHintCells(data.cell_indices ?? []);
      setHintsRemaining(data.hints_remaining ?? 0);
    },

    loteria_validated: (data) => {
      setWinnerAxoId(data.player_axo_id);
      setWinnerName(data.player_name ?? "");
      setWinType(data.win_type ?? "");
    },

    game_end: (data) => {
      if (endedRef.current) return;
      endedRef.current = true;
      setPhase("result");
      setWinnerAxoId(data.winner_axo_id ?? null);
      setPayoutFrj(data.payout_frj ?? data.player_payout ?? 0);
      onGameEnd?.(data.winner_axo_id ?? null, data.payout_frj ?? 0);
    },

    game_state_sync: (data) => {
      // Reconnect sync — restore state
      setPhase(data.phase ?? "playing");
      if (data.player_marked) {
        const boardMarks = Object.values(data.player_marked) as number[][];
        setMarkedCells(boardMarks.flat());
      }
      setCardsCalled(data.cards_history ?? []);
      if (data.current_card_id) {
        setCurrentCard({
          card_id: data.current_card_id,
          turn: data.turns_played,
          window_ms: data.highlight_window_ms ?? 2000,
          timestamp_ms: Date.now(),
        });
      }
      setTurnsPlayed(data.turns_played ?? 0);
    },
  };

  // ── WebSocket ────────────────────────────────────────────────────────────
  const wsUrl = buildWsUrl(roomId, token);
  const { send, readyState, connect, disconnect } = useWebSocket(
    () => wsUrl,
    handlers,
    {
      reconnect: true,
      maxReconnects: 5,
      reconnectBaseMs: 1000,
      heartbeatMs: 15000,
      onOpen: () => setPhase("connecting"),
    }
  );

  // ── Actions ──────────────────────────────────────────────────────────────
  const sendMarkCell = useCallback(
    (cellIndex: number) => {
      if (readyState !== "open") return;
      send({ type: "mark_cell", cell_index: cellIndex });
    },
    [send, readyState]
  );

  const sendShoutLoteria = useCallback(() => {
    if (readyState !== "open") return;
    send({ type: "shout_loteria" });
  }, [send, readyState]);

  const sendUseHint = useCallback(() => {
    if (readyState !== "open") return;
    send({ type: "use_hint" });
  }, [send, readyState]);

  return {
    phase,
    error,
    playerBoardNums,
    boardId,
    players,
    cardsCalled,
    currentCard,
    countdownSeconds,
    tensionLevel,
    nearWinPlayers,
    markedCells,
    hintCells,
    hintsRemaining,
    turnsPlayed,
    highlightWindowMs,
    winnerAxoId,
    winnerName,
    winType,
    payoutFrj,
    sendMarkCell,
    sendShoutLoteria,
    sendUseHint,
    connect,
    disconnect,
  };
}
