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

export type TutorialGamePhase = "loading" | "animating" | "result";

export interface TutorialGameResult {
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

export interface UseTutorialManualGameOptions {
  userId: string;
  token: string | null;
  selectedAxo: any;
  selectedBoardId: number;
  playerBoards: any[];
  allCards: any[];
  tutorialPhase: 1 | 2 | 3; // 1: SAL, 2: OJO, 3: SUERTE_PILA
  onDone: () => void;
  onResultReady?: (won: boolean) => void;
}

export interface UseTutorialManualGameState {
  phase: TutorialGamePhase;
  error: string | null;
  result: TutorialGameResult | null;
  /** Current card index in drawn_cards_sample (0-based) */
  calledIdx: number;
  /** Matched cell indices on player board (user clicked) */
  playerMatches: number[];
  /** Missed (distraction) cell indices */
  playerMissedIndices: number[];
  /** For each bot i: matched cell indices */
  cpuMatchesAll: number[][] ;
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

  // ── Manual actions & helpers ──────────────────────────────────────────────
  onCellTap: (boardIdx: number, cellIdx: number) => void;
  onShoutLoteria: () => void;
  onUseHint: () => void;
  hintsRemaining: number;
  showActionBar: boolean;
  canShoutLoteria: boolean;
  highlightedCell: number | null;
  
  // ── Distraction phase 2 states ─────────────────────────────────────────────
  showDistraction: boolean;
  onDismissDistraction: () => void;

  // ── Speed control ──────────────────────────────────────────────────────────
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

export function useTutorialManualGame(options: UseTutorialManualGameOptions): UseTutorialManualGameState {
  const {
    userId,
    token,
    selectedAxo,
    selectedBoardId,
    playerBoards,
    allCards,
    tutorialPhase,
    onDone,
    onResultReady,
  } = options;

  // ── State ────────────────────────────────────────────────────────────────
  const [phase, setPhase] = useState<TutorialGamePhase>("loading");
  const [result, setResult] = useState<TutorialGameResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Animation & game progress states
  const [calledIdx, setCalledIdx] = useState(-1);
  const [playerMatches, setPlayerMatches] = useState<number[]>([]);
  const [playerMissedIndices, setPlayerMissedIndices] = useState<number[]>([]);
  const [cpuMatchesAll, setCpuMatchesAll] = useState<number[][]>(() => [[]]);
  const [cpuMissedMain, setCpuMissedMain] = useState<number[]>([]);
  const [playerWinLine, setPlayerWinLine] = useState<number[]>([]);
  const [cpuWinLine, setCpuWinLine] = useState<number[]>([]);
  const [showPlayAgain, setShowPlayAgain] = useState(false);
  const [cpuWon, setCpuWon] = useState(false);
  const [playerWon, setPlayerWon] = useState(false);
  const [showLuckySave, setShowLuckySave] = useState(false);
  const [priorityLine, setPriorityLine] = useState<number[]>([]);
  const [cpuWinnerBotIdx, setCpuWinnerBotIdx] = useState(0);

  // Manual gameplay states
  const [canShoutLoteria, setCanShoutLoteria] = useState(false);
  const [hintsRemaining, setHintsRemaining] = useState(3);
  const [highlightedCell, setHighlightedCell] = useState<number | null>(null);

  // Distraction overlay for phase 2
  const [showDistraction, setShowDistraction] = useState(false);
  const [hasTriggeredDistraction, setHasTriggeredDistraction] = useState(false);

  // Stable boards
  const [cpuBoardsNums, setCpuBoardsNums] = useState<number[][]>(() => [fakeCpuBoard()]);
  const [tutorialNameToNum, setTutorialNameToNum] = useState<Map<string, number>>(new Map());

  // Speed control
  const [speedMultiplier, setSpeedMultiplier] = useState(1);

  // Refs for loop synchronization
  const playerMatchesRef = useRef<number[]>([]);
  const playerMissedRef = useRef<number[]>([]);
  const cpuMatchesAllRef = useRef<number[][]>([[]]);
  const cpuMissedMainRef = useRef<number[]>([]);
  const animTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const calledIdxRef = useRef(-1);
  const isPausedRef = useRef(false);

  // Derived board data
  const board = playerBoards.find((b: any) => b.id === selectedBoardId);
  const playerBoardNums =
    result?.player_board_nums
      ? (result.player_board_nums as number[])
      : board
        ? resolveBoardNums(board, allCards)
        : Array(16).fill(0);
  const nameToNum = tutorialNameToNum.size > 0 ? tutorialNameToNum : buildNameToNum(allCards);

  // Calibración de dificultad por fases del tutorial
  const TICK_MS =
    tutorialPhase === 1 ? 2200 :
    tutorialPhase === 2 ? 1700 :
    1300;

  const botMissChance =
    tutorialPhase === 1 ? 0.35 :
    tutorialPhase === 2 ? 0.22 :
    0.12;

  // ── Fetch results from backend ─────────────────────────────────────────────
  const fetchResult = useCallback(async () => {
    try {
      const headers = token ? { Authorization: `Bearer ${token}` } : {};
      const res = await axios.post(`${API_BASE}/tutorial/play-game`, {}, { headers });

      setResult(res.data);
      if (res.data.bot_board_nums && res.data.bot_board_nums.length > 0) {
        setCpuBoardsNums(res.data.bot_board_nums);
      }
      if (res.data.name_to_num) {
        setTutorialNameToNum(
          new Map(Object.entries(res.data.name_to_num).map(([k, v]) => [k, v as number]))
        );
      }
      onDone();
      setPhase("animating");
    } catch (err: any) {
      setError(err.response?.data?.detail ?? "Error al obtener resultado. Intenta de nuevo.");
    }
  }, [token, onDone]);

  useEffect(() => {
    fetchResult();
    return () => {
      if (animTimerRef.current) clearTimeout(animTimerRef.current);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // ── End Game Trigger ───────────────────────────────────────────────────────
  const finishWithPlayerWin = (line: number[]) => {
    if (animTimerRef.current) clearTimeout(animTimerRef.current);
    setPlayerWinLine(line);
    setPlayerWon(true);
    setPhase("result");
    onResultReady?.(true);
  };

  const finishWithCpuWin = (winnerBotIdx: number, winLine: number[]) => {
    if (animTimerRef.current) clearTimeout(animTimerRef.current);
    setCpuWinLine(winLine);
    setCpuWinnerBotIdx(winnerBotIdx);
    setCpuWon(true);
    setPhase("result");
    onResultReady?.(false);
  };

  // ── Manual Marking Callback (onCellTap) ────────────────────────────────────
  const onCellTap = useCallback((boardIdx: number, cellIdx: number) => {
    if (phase !== "animating" || isPausedRef.current || !result) return;

    // Obtener número de la celda pulsada
    const cardNum = playerBoardNums[cellIdx];
    if (!cardNum) return;

    // Buscar el nombre de la carta en el catálogo
    const cardEntry = Array.from(nameToNum.entries()).find((entry) => entry[1] === cardNum);
    if (!cardEntry) return;
    const cardName = cardEntry[0].toLowerCase();

    // Comprobar si la carta ya ha sido cantada en la baraja local hasta el índice actual
    const cardsCalledSoFar = result.drawn_cards_sample.slice(0, calledIdxRef.current + 1);
    const hasBeenCalled = cardsCalledSoFar.some((name: string) => name.toLowerCase() === cardName);

    if (!hasBeenCalled) {
      // Ignorar o feedback de error si no ha salido la carta
      return;
    }

    // Si ya está marcada, no hacer nada
    if (playerMatchesRef.current.includes(cellIdx)) return;

    // Agregar acierto
    const newMatches = [...playerMatchesRef.current, cellIdx];
    playerMatchesRef.current = newMatches;
    setPlayerMatches(newMatches);
    setPriorityLine(calcPriorityLine(newMatches));

    // Si coincide con celda de pista, limpiarla
    if (highlightedCell === cellIdx) {
      setHighlightedCell(null);
    }

    // Verificar si el jugador completó una línea y puede cantar lotería
    const line = checkLine(newMatches);
    if (line) {
      setCanShoutLoteria(true);
    }
  }, [phase, playerBoardNums, result, nameToNum, highlightedCell]);

  // ── Shout Loteria ──────────────────────────────────────────────────────────
  const onShoutLoteria = useCallback(() => {
    if (!canShoutLoteria || phase !== "animating") return;
    const line = checkLine(playerMatchesRef.current);
    if (line) {
      finishWithPlayerWin(line);
    }
  }, [canShoutLoteria, phase]);

  // ── Hints System ───────────────────────────────────────────────────────────
  const onUseHint = useCallback(() => {
    if (hintsRemaining <= 0 || phase !== "animating" || !result) return;

    const cardsCalled = result.drawn_cards_sample.slice(0, calledIdxRef.current + 1).map((n: string) => n.toLowerCase());
    
    let cellToHighlight: number | null = null;
    for (let i = 0; i < playerBoardNums.length; i++) {
      const num = playerBoardNums[i];
      if (num && !playerMatchesRef.current.includes(i)) {
        const cardEntry = Array.from(nameToNum.entries()).find((entry) => entry[1] === num);
        if (cardEntry && cardsCalled.includes(cardEntry[0].toLowerCase())) {
          cellToHighlight = i;
          break;
        }
      }
    }

    if (cellToHighlight !== null) {
      const finalCell = cellToHighlight;
      setHighlightedCell(finalCell);
      setHintsRemaining((prev: number) => prev - 1);
      setTimeout(() => {
        setHighlightedCell((prev: number | null) => prev === finalCell ? null : prev);
      }, 4000);
    }
  }, [hintsRemaining, phase, playerBoardNums, result, nameToNum]);

  // ── Phase 2 Distraction Dismissal ──────────────────────────────────────────
  const onDismissDistraction = useCallback(() => {
    setShowDistraction(false);
    isPausedRef.current = false;
  }, []);

  // ── Bucle de cartas y lógica de la CPU (Bot) ────────────────────────────────
  useEffect(() => {
    if (phase !== "animating" || !result) return;

    const cards = result.drawn_cards_sample;
    let localIdx = calledIdxRef.current + 1;

    // Resetear refs para la simulación
    if (localIdx === 0) {
      playerMatchesRef.current = [];
      playerMissedRef.current = [];
      cpuMatchesAllRef.current = [[]];
      cpuMissedMainRef.current = [];
    }

    const tick = () => {
      if (isPausedRef.current) {
        animTimerRef.current = setTimeout(tick, 200);
        return;
      }

      if (localIdx >= cards.length) {
        const botLine = checkLine(cpuMatchesAllRef.current[0]);
        if (botLine) {
          finishWithCpuWin(0, botLine);
        } else {
          const pLine = calcPriorityLine(cpuMatchesAllRef.current[0]);
          finishWithCpuWin(0, pLine);
        }
        return;
      }

      // ── 1. Cantar carta ──
      const cardName = cards[localIdx];
      const cardNum = nameToNum.get(cardName.toLowerCase()) ?? 0;
      setCalledIdx(localIdx);
      calledIdxRef.current = localIdx;

      // ── 2. Interrupción por Distracción (Acto 6) ──
      if (tutorialPhase === 2 && localIdx === 5 && !hasTriggeredDistraction) {
        setHasTriggeredDistraction(true);
        isPausedRef.current = true;
        setShowDistraction(true);
        const playerCellIdx = playerBoardNums.findIndex((n: number) => n === cardNum);
        if (playerCellIdx !== -1) {
          setHighlightedCell(playerCellIdx);
        }
        animTimerRef.current = setTimeout(tick, 200);
        return;
      }

      // ── 3. Simular marcados del CPU (Bot) ──
      if (cardNum) {
        const botIdx = cpuBoardsNums[0].findIndex((n: number) => n === cardNum);
        if (botIdx !== -1 && !cpuMatchesAllRef.current[0].includes(botIdx)) {
          if (Math.random() >= botMissChance) {
            const newBotMatches = [...cpuMatchesAllRef.current[0], botIdx];
            cpuMatchesAllRef.current[0] = newBotMatches;
            setCpuMatchesAll([newBotMatches]);

            const botLine = checkLine(newBotMatches);
            if (botLine) {
              animTimerRef.current = setTimeout(() => {
                const playerLine = checkLine(playerMatchesRef.current);
                if (playerLine && canShoutLoteria) {
                  return;
                }
                finishWithCpuWin(0, botLine);
              }, 1800 / speedMultiplier);
              return;
            }
          } else {
            const newBotMissed = [...cpuMissedMainRef.current, botIdx];
            cpuMissedMainRef.current = newBotMissed;
            setCpuMissedMain(newBotMissed);
          }
        }
      }

      localIdx++;
      animTimerRef.current = setTimeout(tick, TICK_MS / speedMultiplier);
    };

    animTimerRef.current = setTimeout(tick, localIdx === 0 ? 500 : TICK_MS / speedMultiplier);

    return () => {
      if (animTimerRef.current) clearTimeout(animTimerRef.current);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [phase, result, tutorialPhase, speedMultiplier]);

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
    
    // Manual state
    onCellTap,
    onShoutLoteria,
    onUseHint,
    hintsRemaining,
    showActionBar: true,
    canShoutLoteria,
    highlightedCell,

    // Distraction state
    showDistraction,
    onDismissDistraction,

    // Speed controls
    speedMultiplier,
    setSpeedMultiplier,
  };
}
