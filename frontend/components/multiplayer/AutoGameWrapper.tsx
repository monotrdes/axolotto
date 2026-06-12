"use client";

import React, { useMemo, useState } from "react";
import GameScreen from "../screens/GameScreen";
import { useAutoGame, type AutoGameEndResult } from "@/hooks/useAutoGame";
import type { OpponentInfo } from "../ui/OpponentStrip";

interface AutoGameWrapperProps {
  axolotitoId: number;
  token: string | null;
  allCards: any[];
  playerBoards: any[];
  budget: number;
  recallRequested: boolean;
  recalling: boolean;
  onRecall: () => void;
  escrowNotifs: { id: number; amount: number }[];
  onDone: () => void;
}

export default function AutoGameWrapper({
  axolotitoId,
  token,
  allCards,
  playerBoards,
  budget,
  recallRequested,
  recalling,
  onRecall,
  escrowNotifs,
  onDone,
}: AutoGameWrapperProps) {
  const [endResult, setEndResult] = useState<AutoGameEndResult | null>(null);

  const game = useAutoGame({
    axolotitoId,
    token,
    onGameEnd: (res) => {
      setEndResult(res);
    },
  });

  // Find player's active board
  const activeBoard = useMemo(() => {
    return playerBoards.find((b) => b.id === game.playerBoardId);
  }, [playerBoards, game.playerBoardId]);

  // Map board IDs to lottery numbers (1-54)
  const playerBoardNums = useMemo(() => {
    if (!activeBoard?.card_ids) return Array(16).fill(0);
    return activeBoard.card_ids.map((cid: any) => {
      const c = allCards.find((ac: any) => Number(ac.id) === Number(cid));
      return c ? Number(c.item_metadata?.numero_loteria ?? c.numero_loteria) : 0;
    });
  }, [activeBoard, allCards]);

  // Map opponents
  const opponents: OpponentInfo[] = useMemo(() => {
    return game.opponents.map((opp, idx) => ({
      axolotito_id: -(idx + 1), // Negative IDs for bots
      axo_name: opp.axoName,
      boardNums: [],
      matchedIndices: Array(opp.markedCount).fill(0),
      threat: opp.markedCount,
      kind: "bot" as const,
      isWinner: game.phase === "result" && endResult?.winnerAxoId === opp.axolotitoId,
    }));
  }, [game.opponents, game.phase, endResult]);

  // Map called card history names
  const calledCardsHistory = useMemo(() => {
    return game.cardsDrawnIds
      .map((cid) => {
        const card = allCards.find((c: any) => Number(c.id) === Number(cid));
        return card?.name ?? "";
      })
      .filter(Boolean);
  }, [game.cardsDrawnIds, allCards]);

  // Map name to number map
  const nameToNumMap = useMemo(() => {
    const map = new Map<string, number>();
    allCards.forEach((c: any) => {
      if (c.name && (c.item_metadata?.numero_loteria || c.numero_loteria)) {
        map.set(
          c.name.toLowerCase(),
          Number(c.item_metadata?.numero_loteria ?? c.numero_loteria)
        );
      }
    });
    return map;
  }, [allCards]);

  // Map current card
  const currentCard = useMemo(() => {
    if (!game.currentCardId) return null;
    return {
      cardId: game.currentCardId,
      cardNumber: game.currentCardNumber ?? undefined,
      turn: game.turnsPlayed,
      name: game.currentCardName ?? undefined,
    };
  }, [game.currentCardId, game.currentCardNumber, game.currentCardName, game.turnsPlayed]);

  if (game.error) {
    return (
      <div className="mt-4 bg-red-950/50 border border-red-500/30 text-red-300 text-xs font-bold rounded-2xl p-6 max-w-sm mx-auto text-center">
        <p className="text-red-400 font-extrabold uppercase mb-2">Error de Partida</p>
        <p className="text-slate-300">{game.error}</p>
        <button
          onClick={onDone}
          className="mt-4 px-6 py-2 bg-red-800 hover:bg-red-700 text-white rounded-xl text-xs font-bold transition-all"
        >
          Volver al Lobby
        </button>
      </div>
    );
  }

  // Result mapping
  const result =
    game.phase === "result" && endResult
      ? {
          resultado: (endResult.winnerAxoId === axolotitoId ? "victoria" : "derrota") as
            | "victoria"
            | "derrota",
          prize_gal: endResult.payoutFrj,
          axo_xp_gained: endResult.winnerAxoId === axolotitoId ? 15 : 2,
          board_xp_gained: endResult.winnerAxoId === axolotitoId ? 10 : 1,
          turns: endResult.turnsPlayed,
          player_missed_cards: [] as string[],
          streak_bonus_pct: 0,
          streak_broken: false,
          win_streak_after: 0,
        }
      : undefined;

  return (
    <div className="relative">
      {recallRequested && (
        <div className="absolute top-2 left-1/2 -translate-x-1/2 z-50 px-4 py-1.5 bg-amber-500/95 text-slate-950 font-black text-[10px] rounded-full uppercase tracking-wider shadow-lg animate-pulse">
          ⏳ Regresando al terminar la partida...
        </div>
      )}
      <GameScreen
        mode="auto"
        phase={game.phase === "loading" ? "loading" : game.phase}
        axoName={
          playerBoards.length > 0
            ? "Tu Axolotito"
            : "Axolotito"
        }
        playerBoards={[
          {
            boardNums: playerBoardNums,
            matchedIndices: game.playerMatchedIndices,
            boardId: game.playerBoardId ?? undefined,
          },
        ]}
        allCards={allCards}
        currentCard={currentCard}
        totalCards={game.cardsDrawnIds.length}
        opponents={opponents}
        tensionLevel={game.tensionLevel}
        nearWinPlayers={game.nearWinPlayers}
        result={result}
        calledCardsHistory={calledCardsHistory}
        nameToNumMap={nameToNumMap}
        playerMatchedResult={game.playerMatchedIndices}
        playerMissedResult={game.playerMissedIndices}
        onRecall={onRecall}
        escrowBalance={game.escrowBalance}
        initialBudget={budget}
        onChangeAll={onDone}
      />
    </div>
  );
}
