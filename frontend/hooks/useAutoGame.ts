"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import axios from "axios";
import { API_BASE } from "@/lib/api";

// ── Types ─────────────────────────────────────────────────────────────────────

export type AutoGamePhase = "loading" | "playing" | "result";

export interface AutoGameState {
  phase: AutoGamePhase;
  error: string | null;
  playerBoardId: number | null;
  playerMatchedIndices: number[];
  playerMissedIndices: number[];
  opponents: OpponentState[];
  cardsDrawnIds: number[];
  currentCardId: number | null;
  currentCardName: string | null;
  currentCardNumber: number | null;
  tensionLevel: "low" | "medium" | "high" | "critical";
  nearWinPlayers: number[];
  turnsPlayed: number;
  escrowBalance: number;
}

export interface OpponentState {
  axolotitoId: string | number;
  axoName: string;
  markedCount: number;
  boardCardIds: number[];
}

export interface UseAutoGameOptions {
  axolotitoId: number;
  token: string | null;
  pollIntervalMs?: number;
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
  const [playerBoardId, setPlayerBoardId] = useState<number | null>(null);
  const [playerMatchedIndices, setPlayerMatchedIndices] = useState<number[]>([]);
  const [playerMissedIndices, setPlayerMissedIndices] = useState<number[]>([]);
  const [opponents, setOpponents] = useState<OpponentState[]>([]);
  const [cardsDrawnIds, setCardsDrawnIds] = useState<number[]>([]);
  const [currentCardId, setCurrentCardId] = useState<number | null>(null);
  const [currentCardName, setCurrentCardName] = useState<string | null>(null);
  const [currentCardNumber, setCurrentCardNumber] = useState<number | null>(null);
  const [tensionLevel, setTensionLevel] = useState<"low" | "medium" | "high" | "critical">("low");
  const [nearWinPlayers, setNearWinPlayers] = useState<number[]>([]);
  const [turnsPlayed, setTurnsPlayed] = useState(0);
  const [escrowBalance, setEscrowBalance] = useState(0);

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

      // Player boards mapping
      if (data.player_boards && data.player_boards.length > 0) {
        const pb = data.player_boards[0];
        setPlayerBoardId(pb.board_id);
        setPlayerMatchedIndices(pb.marked_indices ?? []);
        setPlayerMissedIndices(pb.missed_indices ?? []);
      }

      // Bots mapping
      if (data.bot_boards) {
        const mapped: OpponentState[] = data.bot_boards.map((b: any) => ({
          axolotitoId: b.board_id,
          axoName: String(b.board_id).replace("bot_", "Bot "),
          markedCount: b.marked_count ?? 0,
          boardCardIds: [],
        }));
        setOpponents(mapped);
      }

      // Cards drawn IDs
      if (data.cards_drawn) {
        setCardsDrawnIds(data.cards_drawn);
      }

      // Current card mapping
      if (data.current_card) {
        setCurrentCardId(data.current_card.card_id ?? null);
        setCurrentCardName(data.current_card.name ?? null);
        setCurrentCardNumber(data.current_card.numero ?? null);
      } else {
        setCurrentCardId(null);
        setCurrentCardName(null);
        setCurrentCardNumber(null);
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
    playerBoardId,
    playerMatchedIndices,
    playerMissedIndices,
    opponents,
    cardsDrawnIds,
    currentCardId,
    currentCardName,
    currentCardNumber,
    tensionLevel,
    nearWinPlayers,
    turnsPlayed,
    escrowBalance,
    refetch: fetchGameState,
  };
}
