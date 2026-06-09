"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import axios from "axios";
import { API_BASE } from "@/lib/api";

// ── Types ─────────────────────────────────────────────────────────────────────

export type AutoGamePhase = "loading" | "playing" | "result";

export interface AutoGameState {
  phase: AutoGamePhase;
  error: string | null;
  /** Main player board numbers (4×4 = 16) */
  playerBoardNums: number[];
  /** Opponent states: mini boards */
  opponents: OpponentState[];
  /** Cards called so far (history) */
  cardsDrawn: CardDrawnEntry[];
  /** Current card being called */
  currentCard: CardDrawnEntry | null;
  /** Tension metadata */
  tensionLevel: "low" | "medium" | "high" | "critical";
  nearWinPlayers: number[];
  turnsPlayed: number;
  /** Escrow balance snapshot */
  escrowBalance: number;
  /** Interpolated match indices for player board */
  playerMatchedIndices: number[];
}

export interface OpponentState {
  axolotitoId: number;
  axoName: string;
  markedCount: number;
  boardCardIds: number[]; // card IDs, need to be resolved to numbers by caller
}

export interface CardDrawnEntry {
  cardId: number;
  numeroLoteria: number;
  turn: number;
  timestampMs: number;
}

export interface UseAutoGameOptions {
  axolotitoId: number;
  token: string | null;
  /** Interval in ms for polling (default 2000) */
  pollIntervalMs?: number;
  /** Callback when game ends */
  onGameEnd?: (result: AutoGameEndResult) => void;
}

export interface AutoGameEndResult {
  winnerAxoId: number | null;
  payoutFrj: number;
  turnsPlayed: number;
}

// ── Hook ──────────────────────────────────────────────────────────────────────

export function useAutoGame(options: UseAutoGameOptions): AutoGameState & {
  refetch: () => Promise<void>;
} {
  const { axolotitoId, token, pollIntervalMs = 2000, onGameEnd } = options;

  const [phase, setPhase] = useState<AutoGamePhase>("loading");
  const [error, setError] = useState<string | null>(null);
  const [playerBoardNums, setPlayerBoardNums] = useState<number[]>(Array(16).fill(0));
  const [opponents, setOpponents] = useState<OpponentState[]>([]);
  const [cardsDrawn, setCardsDrawn] = useState<CardDrawnEntry[]>([]);
  const [currentCard, setCurrentCard] = useState<CardDrawnEntry | null>(null);
  const [tensionLevel, setTensionLevel] = useState<"low" | "medium" | "high" | "critical">("low");
  const [nearWinPlayers, setNearWinPlayers] = useState<number[]>([]);
  const [turnsPlayed, setTurnsPlayed] = useState(0);
  const [escrowBalance, setEscrowBalance] = useState(0);
  const [playerMatchedIndices, setPlayerMatchedIndices] = useState<number[]>([]);

  const prevCardsRef = useRef<number>(0);
  const pollTimerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const fetchGameState = useCallback(async () => {
    if (!axolotitoId) return;
    try {
      const headers: Record<string, string> = {};
      if (token) headers["Authorization"] = `Bearer ${token}`;

      const res = await axios.get(`${API_BASE}/multiplayer/game-state/${axolotitoId}`, {
        headers,
      });

      const data = res.data;

      // Phase
      if (data.phase === "finished") {
        setPhase("result");
        onGameEnd?.({
          winnerAxoId: data.winner_axo_id ?? null,
          payoutFrj: data.player_payout ?? 0,
          turnsPlayed: data.turns_played ?? 0,
        });
        if (pollTimerRef.current) clearInterval(pollTimerRef.current);
        return;
      }

      setPhase("playing");

      // Board
      if (data.player_board_nums && data.player_board_nums.length > 0) {
        setPlayerBoardNums(data.player_board_nums);
      }

      // Opponents
      if (data.opponents) {
        setOpponents(data.opponents);
      }

      // Cards drawn
      if (data.cards_drawn) {
        const cards = data.cards_drawn as CardDrawnEntry[];
        setCardsDrawn(cards);

        // New card since last poll
        if (cards.length > prevCardsRef.current) {
          const newCard = cards[cards.length - 1];
          setCurrentCard(newCard);
          prevCardsRef.current = cards.length;
        }
      }

      // Tension
      if (data.tension_level) {
        setTensionLevel(data.tension_level);
      }
      if (data.near_win_players) {
        setNearWinPlayers(data.near_win_players);
      }

      // Meta
      if (data.turns_played != null) setTurnsPlayed(data.turns_played);
      if (data.escrow_balance != null) setEscrowBalance(data.escrow_balance);
      if (data.player_matched_indices) {
        setPlayerMatchedIndices(data.player_matched_indices);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail ?? "Error obteniendo estado de partida.");
    }
  }, [axolotitoId, token, onGameEnd]);

  // Polling loop
  useEffect(() => {
    if (!axolotitoId) return;
    fetchGameState(); // Initial fetch
    pollTimerRef.current = setInterval(fetchGameState, pollIntervalMs);
    return () => {
      if (pollTimerRef.current) clearInterval(pollTimerRef.current);
    };
  }, [axolotitoId, pollIntervalMs, fetchGameState]);

  return {
    phase,
    error,
    playerBoardNums,
    opponents,
    cardsDrawn,
    currentCard,
    tensionLevel,
    nearWinPlayers,
    turnsPlayed,
    escrowBalance,
    playerMatchedIndices,
    refetch: fetchGameState,
  };
}
