"use client";

import React, { useMemo } from "react";
import GameScreen from "./screens/GameScreen";
import { useCpuGame, type UseCpuGameOptions } from "@/hooks/useCpuGame";
import type { OpponentInfo } from "./ui/OpponentStrip";

// ── Win-line definitions ──────────────────────────────────────────────────────
const WINNING_LINES: number[][] = [
  [0, 1, 2, 3], [4, 5, 6, 7], [8, 9, 10, 11], [12, 13, 14, 15],
  [0, 4, 8, 12], [1, 5, 9, 13], [2, 6, 10, 14], [3, 7, 11, 15],
  [0, 5, 10, 15], [3, 6, 9, 12],
];

function cpuThreat(matched: number[]): number {
  const s = new Set(matched);
  return Math.max(...WINNING_LINES.map((line) => line.filter((i) => s.has(i)).length));
}

// ── Props ─────────────────────────────────────────────────────────────────────

interface CpuGameWrapperProps extends UseCpuGameOptions {
  onPlayAgainInPlace: () => void;
  onChangeBoard: () => void;
  onChangeAll: () => void;
}

// ── Component ─────────────────────────────────────────────────────────────────

export default function CpuGameWrapper(props: CpuGameWrapperProps) {
  const {
    onPlayAgainInPlace,
    onChangeBoard,
    onChangeAll,
    ...hookOptions
  } = props;

  const game = useCpuGame(hookOptions);

  // Map game phase to GameScreen phase
  const phase = game.phase === "loading"
    ? "loading"
    : game.phase === "result"
      ? "result"
      : "playing";

  // Current card
  const cards = game.result?.drawn_cards_sample ?? [];
  const currentCard = game.calledIdx >= 0 && cards.length > 0
    ? {
        cardNumber: game.nameToNum.get(cards[game.calledIdx]?.toLowerCase() ?? "") ?? undefined,
        turn: game.calledIdx + 1,
        windowMs: 2000,
        name: cards[game.calledIdx],
      }
    : null;

  // Opponents mapped from CPU boards
  const opponents: OpponentInfo[] = useMemo(() => {
    return game.cpuBoardsNums.map((nums, i) => ({
      axolotito_id: -(i + 1), // negative IDs for bots
      axo_name: game.cpuBoardsNums.length > 1 ? `Bot ${i + 1}` : "CPU",
      boardNums: nums,
      matchedIndices: game.cpuMatchesAll[i] ?? [],
      threat: cpuThreat(game.cpuMatchesAll[i] ?? []),
      kind: "bot" as const,
      isWinner: game.cpuWon && i === game.cpuWinnerBotIdx,
    }));
  }, [game.cpuBoardsNums, game.cpuMatchesAll, game.cpuWon, game.cpuWinnerBotIdx]);

  // Tension derived from CPU threat
  const maxThreat = Math.max(0, ...opponents.map((o) => o.threat ?? 0));
  const tensionLevel = game.phase === "result"
    ? (game.playerWon ? "low" : "medium")
    : maxThreat >= 4
      ? "critical"
      : maxThreat >= 3
        ? "high"
        : maxThreat >= 2
          ? "medium"
          : "low";

  // Result mapping
  const result = game.result
    ? {
        resultado: game.result.resultado,
        prize_gal: game.result.prize_gal,
        axo_xp_gained: game.result.axo_xp_gained,
        board_xp_gained: game.result.board_xp_gained,
        turns: game.result.turns,
        player_missed_cards: game.result.player_missed_cards,
        streak_bonus_pct: game.result.streak_bonus_pct,
        streak_broken: game.result.streak_broken,
        win_streak_after: game.result.win_streak_after,
        lucky_save_occurred: game.result.lucky_save_occurred,
        wisdom_saves: game.result.wisdom_saves,
      }
    : undefined;

  // CPU winner board numbers (used in result screen when player loses)
  const cpuWinnerBoardNums =
    game.cpuWon && game.cpuWinnerBotIdx < game.cpuBoardsNums.length
      ? game.cpuBoardsNums[game.cpuWinnerBotIdx]
      : undefined;

  if (game.error) {
    return (
      <div className="mt-4 bg-red-950/50 border border-red-500/30 text-red-300 text-xs font-bold rounded-2xl p-4 max-w-sm mx-auto text-center">
        <p>{game.error}</p>
      </div>
    );
  }

  return (
    <GameScreen
      mode="cpu"
      phase={phase}
      axoName={hookOptions.selectedAxo?.name ?? "Axolotito"}
      playerBoards={[
        {
          boardNums: game.playerBoardNums,
          matchedIndices: game.playerMatches,
          boardId: hookOptions.selectedBoardId,
        },
      ]}
      allCards={hookOptions.allCards}
      currentCard={currentCard}
      totalCards={cards.length}
      opponents={opponents}
      tensionLevel={tensionLevel}
      winPatterns={game.result?.active_win_patterns ?? ['line', 'cuadrito']}
      result={result}
      calledCardsHistory={game.result?.drawn_cards_sample ?? []}
      nameToNumMap={game.nameToNum}
      playerWinLine={game.playerWinLine}
      cpuWinLine={game.cpuWinLine}
      cpuWinnerBoardNums={cpuWinnerBoardNums}
      playerMatchedResult={game.playerMatches}
      playerMissedResult={game.playerMissedIndices}
      onPlayAgain={onPlayAgainInPlace}
      onChangeBoard={onChangeBoard}
      onChangeAll={onChangeAll}
      onSpeedChange={game.setSpeedMultiplier}
      speedMultiplier={game.speedMultiplier}
    />
  );
}
