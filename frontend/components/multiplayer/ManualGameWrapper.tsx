"use client";

import React, { useMemo } from "react";
import GameScreen from "../screens/GameScreen";
import { useManualGame, type UseManualGameOptions } from "@/hooks/useManualGame";
import type { OpponentInfo } from "../ui/OpponentStrip";

interface ManualGameWrapperProps extends UseManualGameOptions {
  onDone: () => void;
  playMode: "manual" | "auto";
}

export default function ManualGameWrapper(props: ManualGameWrapperProps) {
  const { onDone, playMode: initialPlayMode, ...hookOptions } = props;
  const game = useManualGame({ ...hookOptions, initialPlayMode });

  // Map opponent structures
  const opponents: OpponentInfo[] = useMemo(() => {
    return game.players
      .filter((p) => p.axolotito_id !== hookOptions.axolotitoId)
      .map((p) => ({
        axolotito_id: p.axolotito_id,
        axo_name: p.axo_name,
        // Manual mode opponents don't share their full boards, only marked count
        boardNums: [],
        matchedIndices: Array(p.marked_count ?? 0).fill(0),
        threat: p.marked_count ?? 0,
        kind: "human" as const,
        isWinner: game.phase === "result" && game.winnerAxoId === p.axolotito_id,
      }));
  }, [game.players, game.phase, game.winnerAxoId, hookOptions.axolotitoId]);

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

  // Result mapping for manual Lotería
  const result = game.phase === "result"
    ? {
        resultado: (game.winnerAxoId === hookOptions.axolotitoId ? "victoria" : "derrota") as "victoria" | "derrota",
        prize_gal: game.payoutFrj,
        axo_xp_gained: game.winnerAxoId === hookOptions.axolotitoId ? 15 : 2, // estimated
        board_xp_gained: game.winnerAxoId === hookOptions.axolotitoId ? 10 : 1,
        turns: game.turnsPlayed,
        player_missed_cards: [] as string[],
        streak_bonus_pct: 0,
        streak_broken: false,
        win_streak_after: 0,
      }
    : undefined;

  return (
    <div className="relative">
      {game.playMode === "auto" && (
        <div className="absolute top-2 left-1/2 -translate-x-1/2 z-50 px-4 py-1.5 bg-yellow-500/90 text-slate-950 font-black text-[10px] rounded-full uppercase tracking-wider shadow-lg animate-pulse">
          🤖 Modo Bot Activado (Inactividad)
        </div>
      )}
      <GameScreen
        mode={game.playMode === "auto" ? "auto" : "manual"}
        phase={game.phase === "connecting" ? "loading" : game.phase}
        axoName={game.players.find(p => p.axolotito_id === hookOptions.axolotitoId)?.axo_name ?? "Tu Axolotito"}
        playerBoards={[
          {
            boardNums: game.playerBoardNums,
            matchedIndices: game.markedCells,
            boardId: game.boardId ?? undefined,
          }
        ]}
        allCards={[]} // loaded inside GameScreen
        currentCard={
          game.currentCard
            ? {
                cardId: game.currentCard.card_id,
                cardNumber: game.currentCard.card_number,
                turn: game.currentCard.turn,
                windowMs: game.currentCard.window_ms,
              }
            : null
        }
        totalCards={game.cardsCalled.length}
        opponents={opponents}
        tensionLevel={game.tensionLevel}
        nearWinPlayers={game.nearWinPlayers}
        countdownSeconds={game.countdownSeconds}
        onCellTap={(boardIdx, cellIdx) => game.sendMarkCell(cellIdx)}
        onShoutLoteria={game.sendShoutLoteria}
        onUseHint={game.sendUseHint}
        hintsRemaining={game.hintsRemaining}
        showActionBar={game.phase === "playing" && game.playMode === "manual"}
        result={result}
        // Chat wiring
        chatMessages={game.chatMessages ?? []}
        onSendChat={game.sendChatMessage}
        chatCollapsed={game.chatCollapsed}
        onToggleChat={game.toggleChat}
      />
    </div>
  );
}
