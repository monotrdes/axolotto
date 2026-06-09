"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import axios from "axios";
import { API_BASE } from "@/lib/api";

// ── Win-line definitions (4×4 grid, indices 0-15) ─────────────────────────────
const WINNING_LINES: number[][] = [
  [0, 1, 2, 3], [4, 5, 6, 7], [8, 9, 10, 11], [12, 13, 14, 15],
  [0, 4, 8, 12], [1, 5, 9, 13], [2, 6, 10, 14], [3, 7, 11, 15],
  [0, 5, 10, 15], [3, 6, 9, 12],
];

// ── Animation timing ──────────────────────────────────────────────────────────
export const CPU_TICK_MS = 1200;
const INITIAL_DELAY = 200;

// ── Types ─────────────────────────────────────────────────────────────────────

export type CpuGamePhase = "loading" | "animating" | "result";

export interface CpuGameResult {
  resultado: "victoria" | "derrota";
  winner: string;
  turns: number;
  prize_gal: number;
  drawn_cards_sample: string[];
  player_missed_cards: string[];
  axo_xp_gained: number;
  board_xp_gained: number;
  axo_level_current: number;
  board_level_current: number;
  room_title: string;
  bot_count: number;
  bot_focus: number;
  player_miss_chance_pct: number;
  lucky_save_occurred: boolean;
  lucky_save_turn: number | null;
  win_streak_after: number;
  streak_bonus_pct: number;
  streak_broken: boolean;
  wisdom_saves: number;
  bot_board_nums?: number[][];
  bot_board_ids?: (number | null)[];
  bot_marked_indices?: number[][];
  player_board_nums?: number[];
  name_to_num?: Record<string, number>;
  winning_line?: number[] | null;
  winner_bot_index?: number | null;
  active_win_patterns?: string[];
}

export interface UseCpuGameOptions {
  userId: string;
  token: string | null;
  selectedAxo: any;
  selectedBoardId: number;
  playerBoards: any[];
  allCards: any[];
  selectedRoom: "rookie" | "champion";
  multiplier?: number;
  onDone: () => void;
  onResultReady?: (won: boolean) => void;
}

export interface UseCpuGameState {
  phase: CpuGamePhase;
  error: string | null;
  result: CpuGameResult | null;
  /** Current card index in drawn_cards_sample (0-based) */
  calledIdx: number;
  /** Matched cell indices on player board */
  playerMatches: number[];
  /** Missed (distraction) cell indices */
  playerMissedIndices: number[];
  /** For each bot i: matched cell indices */
  cpuMatchesAll: number[][];
  /** Missed indices for main bot (index 0) */
  cpuMissedMain: number[];
  /** Winning line on player board (empty until won) */
  playerWinLine: number[];
  /** Winning line on winner bot board */
  cpuWinLine: number[];
  showPlayAgain: boolean;
  cpuWon: boolean;
  playerWon: boolean;
  showLuckySave: boolean;
  priorityLine: number[];
  cpuWinnerBotIdx: number;
  cpuBoardsNums: number[][];
  playerBoardNums: number[];
  /** card name → lotería number */
  nameToNum: Map<string, number>;
  /** Already resolved (true after loading phase) */
  ready: boolean;
  /** Animation speed multiplier (1 = normal, 2 = fast) */
  speedMultiplier: number;
  setSpeedMultiplier: (multiplier: number) => void;
}

// ── Helpers ───────────────────────────────────────────────────────────────────

function checkLine(matched: number[]): number[] | null {
  const s = new Set(matched);
  for (const line of WINNING_LINES) {
    if (line.every((i) => s.has(i))) return line;
  }
  return null;
}

function calcPriorityLine(matched: number[]): number[] {
  const matchedSet = new Set(matched);
  let bestLine: number[] = [];
  let bestCount = -1;
  for (const line of WINNING_LINES) {
    const count = line.filter((i) => matchedSet.has(i)).length;
    if (count > bestCount) {
      bestCount = count;
      bestLine = line;
    }
  }
  return bestLine;
}

function cpuThreat(matched: number[]): number {
  const s = new Set(matched);
  return Math.max(...WINNING_LINES.map((line) => line.filter((i) => s.has(i)).length));
}

function fakeCpuBoard(): number[] {
  const nums = Array.from({ length: 54 }, (_, i) => i + 1);
  for (let i = nums.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [nums[i], nums[j]] = [nums[j], nums[i]];
  }
  return nums.slice(0, 16);
}

function buildNameToNum(allCards: any[]): Map<string, number> {
  const m = new Map<string, number>();
  allCards.forEach((c) => {
    const num = Number(c.item_metadata?.numero_loteria);
    if (num && c.name) m.set(c.name.toLowerCase(), num);
  });
  return m;
}

function resolveBoardNums(board: any, allCards: any[]): number[] {
  return (board.card_ids || []).slice(0, 16).map((id: number | null) => {
    if (!id) return 0;
    const c = allCards.find((card: any) => Number(card.id) === Number(id));
    return c ? Number(c.item_metadata?.numero_loteria) || 0 : 0;
  });
}

// ── Hook ──────────────────────────────────────────────────────────────────────

export function useCpuGame(options: UseCpuGameOptions): UseCpuGameState {
  const {
    userId,
    token,
    selectedAxo,
    selectedBoardId,
    playerBoards,
    allCards,
    selectedRoom,
    multiplier = 1,
    onDone,
    onResultReady,
  } = options;

  const BOT_COUNT = selectedRoom === "champion" ? 5 : 1;
  const isTutorial = selectedAxo.id === 0;

  // ── State ────────────────────────────────────────────────────────────────
  const [phase, setPhase] = useState<CpuGamePhase>("loading");
  const [result, setResult] = useState<CpuGameResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Animation state
  const [calledIdx, setCalledIdx] = useState(-1);
  const [playerMatches, setPlayerMatches] = useState<number[]>([]);
  const [playerMissedIndices, setPlayerMissedIndices] = useState<number[]>([]);
  const [cpuMatchesAll, setCpuMatchesAll] = useState<number[][]>(() =>
    Array.from({ length: BOT_COUNT }, () => [])
  );
  const [cpuMissedMain, setCpuMissedMain] = useState<number[]>([]);
  const [playerWinLine, setPlayerWinLine] = useState<number[]>([]);
  const [cpuWinLine, setCpuWinLine] = useState<number[]>([]);
  const [showPlayAgain, setShowPlayAgain] = useState(false);
  const [cpuWon, setCpuWon] = useState(false);
  const [playerWon, setPlayerWon] = useState(false);
  const [showLuckySave, setShowLuckySave] = useState(false);
  const [priorityLine, setPriorityLine] = useState<number[]>([]);
  const [cpuWinnerBotIdx, setCpuWinnerBotIdx] = useState(0);

  // Stable boards
  const [cpuBoardsNums, setCpuBoardsNums] = useState<number[][]>(() =>
    Array.from({ length: BOT_COUNT }, () => fakeCpuBoard())
  );
  const [tutorialNameToNum, setTutorialNameToNum] = useState<Map<string, number>>(
    new Map()
  );

  // Speed control
  const [speedMultiplier, setSpeedMultiplier] = useState(1);

  // Refs
  const playerMatchesRef = useRef<number[]>([]);
  const playerMissedRef = useRef<number[]>([]);
  const cpuMatchesAllRef = useRef<number[][]>(Array.from({ length: BOT_COUNT }, () => []));
  const cpuMissedMainRef = useRef<number[]>([]);
  const animTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Derived board data
  const board = playerBoards.find((b: any) => b.id === selectedBoardId);
  const playerBoardNums =
    isTutorial && result?.player_board_nums
      ? (result.player_board_nums as number[])
      : board
        ? resolveBoardNums(board, allCards)
        : Array(16).fill(0);
  const nameToNum = isTutorial ? tutorialNameToNum : buildNameToNum(allCards);

  // ── Fetch ────────────────────────────────────────────────────────────────
  const fetchResult = useCallback(async () => {
    try {
      const headers = token ? { Authorization: `Bearer ${token}` } : {};

      let res;
      if (isTutorial) {
        res = await axios.post(`${API_BASE}/tutorial/play-game`, {}, { headers });
      } else {
        await axios.post(
          `${API_BASE}/auth/axolotitos/${selectedAxo.id}/bot-config`,
          {
            user_id: userId,
            bot_enabled: true,
            bot_budget_axf: 100,
            bot_loss_limit_axf: 100,
            bot_profit_limit_axf: 10000,
            assigned_board_id: selectedBoardId,
          },
          { headers }
        );
        res = await axios.post(
          `${API_BASE}/game/play`,
          {
            axolotito_id: selectedAxo.id,
            room_name: selectedRoom,
            multiplier,
            bot_enabled: true,
            bot_budget_gal: 100,
            bot_loss_limit_pct: 100,
            bot_profit_limit_pct: 10000,
          },
          { headers }
        );
      }

      setResult(res.data);
      if (res.data.bot_board_nums && res.data.bot_board_nums.length > 0) {
        setCpuBoardsNums(res.data.bot_board_nums);
      }
      if (isTutorial && res.data.name_to_num) {
        setTutorialNameToNum(
          new Map(Object.entries(res.data.name_to_num).map(([k, v]) => [k, v as number]))
        );
      }
      onDone();
      setPhase("animating");
    } catch (err: any) {
      setError(err.response?.data?.detail ?? "Error al obtener resultado. Intenta de nuevo.");
    }
  }, [token, selectedAxo.id, selectedBoardId, selectedRoom, multiplier, onDone, isTutorial]);

  useEffect(() => {
    fetchResult();
    return () => {
      if (animTimerRef.current) clearTimeout(animTimerRef.current);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // ── Animation tick-by-tick ───────────────────────────────────────────────
  useEffect(() => {
    if (phase !== "animating" || !result) return;

    const {
      drawn_cards_sample: cards,
      resultado,
      player_missed_cards,
      bot_focus,
      lucky_save_occurred,
      lucky_save_turn,
      winning_line: backendWinningLine,
      winner_bot_index: backendWinnerBotIdx,
    } = result;

    const backendWon = resultado === "victoria";
    const botMissChance = Math.max(0, Math.min(0.3, (100 - (bot_focus ?? 50)) * 0.003));
    const botCount = cpuBoardsNums.length;
    let idx = 0;

    playerMatchesRef.current = [];
    playerMissedRef.current = [];
    cpuMatchesAllRef.current = Array.from({ length: botCount }, () => []);
    cpuMissedMainRef.current = [];

    const finishWithPlayerWin = (line: number[]) => {
      setPlayerWinLine(line);
      setPlayerWon(true);
      setPhase("result");
      onResultReady?.(true);
      setTimeout(() => setShowPlayAgain(true), 2000);
    };

    const finishWithCpuWin = (allMatches: number[][], winnerBotIdx: number, winLine: number[]) => {
      setCpuWinLine(winLine);
      setCpuWinnerBotIdx(winnerBotIdx);
      const newAll = allMatches.map((arr) => [...arr]);
      setCpuMatchesAll(newAll);
      cpuMatchesAllRef.current = newAll;
      setCpuWon(true);
      setPhase("result");
      onResultReady?.(false);
      setTimeout(() => setShowPlayAgain(true), 2000);
    };

    const tick = () => {
      if (idx >= cards.length) {
        if (backendWon) {
          finishWithPlayerWin([0, 1, 2, 3]);
        } else {
          let winLine: number[];
          let winBot: number;
          if (
            backendWinningLine && backendWinningLine.length > 0 &&
            backendWinnerBotIdx != null && backendWinnerBotIdx < botCount
          ) {
            winLine = backendWinningLine;
            winBot = backendWinnerBotIdx;
          } else {
            const found = (() => {
              for (let b = 0; b < botCount; b++) {
                const l = checkLine(cpuMatchesAllRef.current[b] ?? []);
                if (l) return { line: l, bot: b };
              }
              return null;
            })();
            if (found) {
              winLine = found.line;
              winBot = found.bot;
            } else {
              winBot = cpuBoardsNums
                .map((_, i) => i)
                .sort(
                  (a, bIdx) =>
                    cpuThreat(cpuMatchesAllRef.current[bIdx] ?? []) -
                    cpuThreat(cpuMatchesAllRef.current[a] ?? [])
                )[0];
              const priorityFull = calcPriorityLine(cpuMatchesAllRef.current[winBot] ?? []);
              const matchedSet = new Set(cpuMatchesAllRef.current[winBot] ?? []);
              winLine = priorityFull.filter((i) => matchedSet.has(i));
            }
          }
          finishWithCpuWin(cpuMatchesAllRef.current, winBot, winLine!);
        }
        return;
      }

      const cardName = cards[idx];
      const cardNum = nameToNum.get(cardName.toLowerCase()) ?? 0;
      setCalledIdx(idx);

      if (lucky_save_turn !== null && idx === lucky_save_turn) {
        setShowLuckySave(true);
        setTimeout(() => setShowLuckySave(false), 1600);
      }

      if (cardNum) {
        const playerIdx = playerBoardNums.findIndex((n) => n === cardNum);
        if (
          playerIdx !== -1 &&
          !playerMatchesRef.current.includes(playerIdx) &&
          !playerMissedRef.current.includes(playerIdx)
        ) {
          const wasMissed = player_missed_cards.some(
            (m) => m.toLowerCase() === cardName.toLowerCase()
          );
          if (wasMissed) {
            const newMissed = [...playerMissedRef.current, playerIdx];
            playerMissedRef.current = newMissed;
            setPlayerMissedIndices([...newMissed]);
          } else {
            playerMatchesRef.current = [...playerMatchesRef.current, playerIdx];
            setPlayerMatches([...playerMatchesRef.current]);

            const line = checkLine(playerMatchesRef.current);
            if (line && backendWon) {
              idx++;
              setCalledIdx(idx - 1);
              finishWithPlayerWin(line);
              return;
            }
          }
          setPriorityLine(calcPriorityLine(playerMatchesRef.current));
        }

        // Update all bot boards
        const newMatchesAll = cpuMatchesAllRef.current.map((arr) => [...arr]);
        const newMissedMain = [...cpuMissedMainRef.current];
        let matchesChanged = false;
        let missedMainChanged = false;

        for (let b = 0; b < botCount; b++) {
          const botIdx = cpuBoardsNums[b].findIndex((n) => n === cardNum);
          if (botIdx !== -1 && !newMatchesAll[b].includes(botIdx)) {
            if (Math.random() >= botMissChance) {
              newMatchesAll[b] = [...newMatchesAll[b], botIdx];
              matchesChanged = true;
            } else if (b === 0 && !newMissedMain.includes(botIdx)) {
              newMissedMain.push(botIdx);
              missedMainChanged = true;
            }
          }
        }

        if (matchesChanged) {
          cpuMatchesAllRef.current = newMatchesAll;
          setCpuMatchesAll([...newMatchesAll]);

          if (!backendWon) {
            for (let b = 0; b < botCount; b++) {
              const botLine = checkLine(newMatchesAll[b]);
              if (botLine) {
                if (missedMainChanged) {
                  cpuMissedMainRef.current = newMissedMain;
                  setCpuMissedMain([...newMissedMain]);
                }
                finishWithCpuWin(newMatchesAll, b, botLine);
                return;
              }
            }
          }
        }
        if (missedMainChanged) {
          cpuMissedMainRef.current = newMissedMain;
          setCpuMissedMain([...newMissedMain]);
        }
      }

      idx++;
      animTimerRef.current = setTimeout(tick, CPU_TICK_MS);
    };

    animTimerRef.current = setTimeout(tick, INITIAL_DELAY);
    return () => {
      if (animTimerRef.current) clearTimeout(animTimerRef.current);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [phase, result]);

  return {
    phase,
    error,
    result,
    calledIdx,
    playerMatches,
    playerMissedIndices,
    cpuMatchesAll,
    cpuMissedMain,
    playerWinLine,
    cpuWinLine,
    showPlayAgain,
    cpuWon,
    playerWon,
    showLuckySave,
    priorityLine,
    cpuWinnerBotIdx,
    cpuBoardsNums,
    playerBoardNums,
    nameToNum,
    ready: phase !== "loading",
    speedMultiplier,
    setSpeedMultiplier,
  };
}
