"use client";
import { API_BASE } from "@/lib/api";

import React, { useState, useEffect, useRef, useCallback } from 'react';
import axios from 'axios';
import { Play, Sparkles } from 'lucide-react';
import BoardCardGrid from '../ui/BoardCardGrid';
import { LOTERIA_EMOJI, CARD_IMAGE } from '../ui/LoteriaCard';
import Image from 'next/image';

// ── Win-line definitions (4×4 grid, indices 0-15) ─────────────────────────────
// Must mirror backend: app/api/v1/endpoints/game.py → WINNING_LINES
const WINNING_LINES: number[][] = [
  // Rows
  [0, 1, 2, 3], [4, 5, 6, 7], [8, 9, 10, 11], [12, 13, 14, 15],
  // Columns
  [0, 4, 8, 12], [1, 5, 9, 13], [2, 6, 10, 14], [3, 7, 11, 15],
  // Diagonals
  [0, 5, 10, 15], [3, 6, 9, 12],
];

/** Returns the first completed winning line, or null if none yet. */
function checkLine(matched: number[]): number[] | null {
  const s = new Set(matched);
  for (const line of WINNING_LINES) {
    if (line.every(i => s.has(i))) return line;
  }
  return null;
}

// ── Animation timing ──────────────────────────────────────────────────────────
// animate-card-call is 400ms — TICK_MS must be > 400 to avoid clipping it.
const TICK_MS       = 1200;
const INITIAL_DELAY = 200;

// ── Props & types ─────────────────────────────────────────────────────────────

interface CpuSimScreenProps {
  userId: string;
  token: string | null;
  selectedAxo: any;
  selectedBoardId: number;
  playerBoards: any[];
  allCards: any[];
  selectedRoom: 'rookie' | 'champion';
  multiplier?: number;
  /** Re-play with the exact same axo + board + room (no navigation — parent remounts via key) */
  onPlayAgainInPlace: () => void;
  /** Navigate back to board-select to pick a different table or room */
  onChangeBoard: () => void;
  /** Reset everything and go back to axo-select */
  onChangeAll: () => void;
  onDone: () => void;
  /** Fires when animation ends and result is determined. Tutorial uses this to skip the XP panel. */
  onResultReady?: (won: boolean) => void;
}

type SimPhase = 'loading' | 'animating' | 'result';

interface SimResult {
  resultado: 'victoria' | 'derrota';
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
}

// ── Board helpers ─────────────────────────────────────────────────────────────

/** card name → lotería number (from allCards catalog) */
function buildNameToNum(allCards: any[]): Map<string, number> {
  const m = new Map<string, number>();
  allCards.forEach(c => {
    const num = Number(c.item_metadata?.numero_loteria);
    if (num && c.name) m.set(c.name.toLowerCase(), num);
  });
  return m;
}

/** board card_ids → array of 16 lotería numbers */
function resolveBoardNums(board: any, allCards: any[]): number[] {
  return (board.card_ids || []).slice(0, 16).map((id: number | null) => {
    if (!id) return 0;
    const c = allCards.find((card: any) => Number(card.id) === Number(id));
    return c ? Number(c.item_metadata?.numero_loteria) || 0 : 0;
  });
}

/** Random CPU board (pure display — not used for win logic) */
function fakeCpuBoard(): number[] {
  const nums = Array.from({ length: 54 }, (_, i) => i + 1);
  for (let i = nums.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [nums[i], nums[j]] = [nums[j], nums[i]];
  }
  return nums.slice(0, 16);
}

/** Mirrors backend _get_priority_line: returns the most-advanced winning line. */
function calcPriorityLine(matched: number[]): number[] {
  const matchedSet = new Set(matched);
  let bestLine: number[] = [];
  let bestCount = -1;
  for (const line of WINNING_LINES) {
    const count = line.filter(i => matchedSet.has(i)).length;
    if (count > bestCount) {
      bestCount = count;
      bestLine = line;
    }
  }
  return bestLine;
}

// ── cpuThreat ─────────────────────────────────────────────────────────────────
// Max matched cells in any winning line — used to sort bots by danger level.
function cpuThreat(matched: number[]): number {
  const s = new Set(matched);
  return Math.max(...WINNING_LINES.map(line => line.filter(i => s.has(i)).length));
}

// ── MiniCpuBoard ──────────────────────────────────────────────────────────────
// Compact 4×4 emoji grid for background enemy bots in Champion mode.

function MiniCpuBoard({
  boardNums,
  matchedIndices,
  priorityLine,
  label,
}: {
  boardNums: number[];
  matchedIndices: number[];
  priorityLine: number[];
  label: string;
}) {
  return (
    <div className="opacity-65">
      <BoardCardGrid
        boardNums={boardNums}
        cardSize={13}
        matchedIndices={matchedIndices}
        priorityLine={priorityLine}
        variant="cpu"
        depth="back"
        label={label}
      />
    </div>
  );
}

// ── Component ─────────────────────────────────────────────────────────────────

export default function CpuSimScreen({
  userId,
  token,
  selectedAxo,
  selectedBoardId,
  playerBoards,
  allCards,
  selectedRoom,
  multiplier = 1,
  onPlayAgainInPlace,
  onChangeBoard,
  onChangeAll,
  onResultReady,
  onDone,
}: CpuSimScreenProps) {
  // Derived from room config — stable for this component's lifetime
  const BOT_COUNT = selectedRoom === 'champion' ? 5 : 1;

  const [phase, setPhase]   = useState<SimPhase>('loading');
  const [result, setResult] = useState<SimResult | null>(null);
  const [error, setError]   = useState<string | null>(null);
  const [resultFlash, setResultFlash] = useState<{ type: 'win' | 'loss'; msg: string } | null>(null);
  const flashTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // ── Animation state ────────────────────────────────────────────────────────
  const [calledIdx, setCalledIdx]                     = useState(-1);
  const [playerMatches, setPlayerMatches]             = useState<number[]>([]);
  const [playerMissedIndices, setPlayerMissedIndices] = useState<number[]>([]);
  // cpuMatchesAll[i] = matched cell indices for bot board i
  const [cpuMatchesAll, setCpuMatchesAll]             = useState<number[][]>(() => Array.from({ length: BOT_COUNT }, () => []));
  // cpuMissedMain = missed cell indices for the main bot (index 0)
  const [cpuMissedMain, setCpuMissedMain]             = useState<number[]>([]);
  const [playerWinLine, setPlayerWinLine]             = useState<number[]>([]);
  const [cpuWinLine, setCpuWinLine]                   = useState<number[]>([]);
  const [showPlayAgain, setShowPlayAgain]             = useState(false);
  const [cpuWon, setCpuWon]                           = useState(false);
  const [playerWon, setPlayerWon]                     = useState(false);
  const [showLuckySave, setShowLuckySave]             = useState(false);
  const [priorityLine, setPriorityLine]               = useState<number[]>([]);
  const [cpuWinnerBotIdx, setCpuWinnerBotIdx]         = useState(0);

  // Refs for closure-safe access inside the animation setTimeout chain
  const playerMatchesRef  = useRef<number[]>([]);
  const playerMissedRef   = useRef<number[]>([]);
  const cpuMatchesAllRef  = useRef<number[][]>(Array.from({ length: BOT_COUNT }, () => []));
  const cpuMissedMainRef  = useRef<number[]>([]);
  const animTimerRef      = useRef<ReturnType<typeof setTimeout> | null>(null);

  // ── Step 1: fetch result from backend ────────────────────────────────────
  const isTutorial = selectedAxo.id === 0;

  // N fake CPU boards — stable, initialized once
  const [cpuBoardsNums, setCpuBoardsNums]  = useState<number[][]>(() => Array.from({ length: BOT_COUNT }, () => fakeCpuBoard()));
  // In tutorial mode, the backend returns the name→number map since allCards=[]
  const [tutorialNameToNum, setTutorialNameToNum] = useState<Map<string, number>>(new Map());

  // Resolved board data (stable — computed once)
  // In tutorial mode, player_board_nums arrives from the backend result after fetch.
  const board            = playerBoards.find(b => b.id === selectedBoardId);
  const playerBoardNums  = (isTutorial && result?.player_board_nums)
    ? (result.player_board_nums as number[])
    : (board ? resolveBoardNums(board, allCards) : Array(16).fill(0));
  const nameToNum        = isTutorial ? tutorialNameToNum : buildNameToNum(allCards);

  const fetchResult = useCallback(async () => {
    try {
      const headers = token ? { Authorization: `Bearer ${token}` } : {};

      let res;
      if (isTutorial) {
        // Tutorial mode: no bot-config, dedicated endpoint without economy effects
        res = await axios.post(`${API_BASE}/tutorial/play-game`, {}, { headers });
      } else {
        // Real game: configure bot first, then play
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
            multiplier: multiplier,
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
      // else: keep the fakeCpuBoard fallback for backwards compatibility
      if (isTutorial && res.data.name_to_num) {
        setTutorialNameToNum(new Map(Object.entries(res.data.name_to_num).map(([k, v]) => [k, v as number])));
      }
      onDone();
      setPhase('animating');
    } catch (err: any) {
      setError(err.response?.data?.detail ?? 'Error al obtener resultado. Intenta de nuevo.');
    }
  }, [token, userId, selectedAxo.id, selectedBoardId, selectedRoom, multiplier, onDone, isTutorial]);

  useEffect(() => {
    fetchResult();
    return () => {
      if (animTimerRef.current) clearTimeout(animTimerRef.current);
      if (flashTimerRef.current) clearTimeout(flashTimerRef.current);
    };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // ── Step 2: animate cards one by one, detect lines ───────────────────────
  useEffect(() => {
    if (phase !== 'animating' || !result) return;

    // Destructure for closure safety (result is non-null, narrowed by guard above)
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

    const backendWon    = resultado === 'victoria';
    // Bot miss chance: same formula as backend _miss_chance(focus)
    const botMissChance = Math.max(0, Math.min(0.3, (100 - (bot_focus ?? 50)) * 0.003));
    const botCount      = cpuBoardsNums.length;
    let idx             = 0;

    // Reset refs at animation start
    playerMatchesRef.current  = [];
    playerMissedRef.current   = [];
    cpuMatchesAllRef.current  = Array.from({ length: botCount }, () => []);
    cpuMissedMainRef.current  = [];

    const finishWithPlayerWin = (line: number[]) => {
      setPlayerWinLine(line);
      setPlayerWon(true);
      setPhase('result');
      onResultReady?.(true);
      setTimeout(() => setShowPlayAgain(true), 2000);
      // Economy flash
      if (flashTimerRef.current) clearTimeout(flashTimerRef.current);
      setResultFlash({ type: 'win', msg: `+${result?.prize_gal ?? 0} FRJ` });
      flashTimerRef.current = setTimeout(() => setResultFlash(null), 3000);
    };

    const finishWithCpuWin = (
      allMatches: number[][],
      winnerBotIdx: number,
      winLine: number[]
    ) => {
      setCpuWinLine(winLine);
      setCpuWinnerBotIdx(winnerBotIdx);
      const newAll = allMatches.map(arr => [...arr]);
      setCpuMatchesAll(newAll);
      cpuMatchesAllRef.current = newAll;
      setCpuWon(true);
      setPhase('result');
      onResultReady?.(false);
      setTimeout(() => setShowPlayAgain(true), 2000);
      // Economy flash
      if (flashTimerRef.current) clearTimeout(flashTimerRef.current);
      setResultFlash({ type: 'loss', msg: 'Derrota — el CPU completó su línea' });
      flashTimerRef.current = setTimeout(() => setResultFlash(null), 3000);
    };

    const tick = () => {
      // Defensive guard: all cards played
      if (idx >= cards.length) {
        if (backendWon) {
          finishWithPlayerWin([0, 1, 2, 3]); // fallback (shouldn't normally reach)
        } else {
          // Prefer backend-provided winning line and bot index (avoids divergence from Math.random())
          let winLine: number[];
          let winBot: number;
          if (
            backendWinningLine && backendWinningLine.length > 0
            && backendWinnerBotIdx != null && backendWinnerBotIdx < botCount
          ) {
            winLine = backendWinningLine;
            winBot = backendWinnerBotIdx;
          } else {
            // Fallback for old backends: find bot with a completed line, or most dangerous
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
                .sort((a, bIdx) => cpuThreat(cpuMatchesAllRef.current[bIdx] ?? []) - cpuThreat(cpuMatchesAllRef.current[a] ?? []))[0];
              const priorityFull = calcPriorityLine(cpuMatchesAllRef.current[winBot] ?? []);
              const matchedSet = new Set(cpuMatchesAllRef.current[winBot] ?? []);
              winLine = priorityFull.filter(i => matchedSet.has(i));
            }
          }
          finishWithCpuWin(cpuMatchesAllRef.current, winBot, winLine!);
        }
        return;
      }

      const cardName = cards[idx];
      const cardNum  = nameToNum.get(cardName.toLowerCase()) ?? 0;
      setCalledIdx(idx);

      // Lucky Save detection
      if (lucky_save_turn !== null && idx === lucky_save_turn) {
        setShowLuckySave(true);
        setTimeout(() => setShowLuckySave(false), 1600);
      }

      if (cardNum) {
        // ── Update player board ───────────────────────────────────────────
        const playerIdx = playerBoardNums.findIndex(n => n === cardNum);
        if (
          playerIdx !== -1
          && !playerMatchesRef.current.includes(playerIdx)
          && !playerMissedRef.current.includes(playerIdx)
        ) {
          const wasMissed = player_missed_cards.some(
            m => m.toLowerCase() === cardName.toLowerCase()
          );

          if (wasMissed) {
            // Player was distracted — show orange ✗ indicator instead of green mark
            const newMissed = [...playerMissedRef.current, playerIdx];
            playerMissedRef.current = newMissed;
            setPlayerMissedIndices([...newMissed]);
          } else {
            playerMatchesRef.current = [...playerMatchesRef.current, playerIdx];
            setPlayerMatches([...playerMatchesRef.current]);

            // Check for a winning line on player board
            const line = checkLine(playerMatchesRef.current);
            if (line && backendWon) {
              idx++;
              setCalledIdx(idx - 1);
              finishWithPlayerWin(line);
              return;
            }
          }

          // Recalculate Wisdom priority line after any player state change
          setPriorityLine(calcPriorityLine(playerMatchesRef.current));
        }

        // ── Update all bot boards (probabilistic miss) ────────────────────
        const newMatchesAll   = cpuMatchesAllRef.current.map(arr => [...arr]);
        const newMissedMain   = [...cpuMissedMainRef.current];
        let matchesChanged    = false;
        let missedMainChanged = false;

        for (let b = 0; b < botCount; b++) {
          const botIdx = cpuBoardsNums[b].findIndex(n => n === cardNum);
          if (botIdx !== -1 && !newMatchesAll[b].includes(botIdx)) {
            if (Math.random() >= botMissChance) {
              // Bot marks it
              newMatchesAll[b] = [...newMatchesAll[b], botIdx];
              matchesChanged = true;
            } else if (b === 0 && !newMissedMain.includes(botIdx)) {
              // Main bot (index 0) missed — show dim indicator on its board
              newMissedMain.push(botIdx);
              missedMainChanged = true;
            }
          }
        }

        if (matchesChanged) {
          cpuMatchesAllRef.current = newMatchesAll;
          setCpuMatchesAll([...newMatchesAll]);

          // If backend says player lost, check if any bot just completed a line
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
      animTimerRef.current = setTimeout(tick, TICK_MS);
    };

    animTimerRef.current = setTimeout(tick, INITIAL_DELAY);
    return () => { if (animTimerRef.current) clearTimeout(animTimerRef.current); };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [phase, result]);

  // ── Loading screen ─────────────────────────────────────────────────────────
  if (phase === 'loading') {
    return (
      <div className="flex flex-col items-center justify-center py-20 gap-4">
        <div className="w-12 h-12 border-4 border-[var(--brand-hot)] border-t-transparent rounded-full animate-spin" />
        <p className="text-slate-400 text-xs font-black uppercase tracking-widest animate-pulse">
          Iniciando partida...
        </p>
        {/* Active streak banner */}
        {selectedAxo.cpu_win_streak >= 1 && (
          <div className="flex items-center gap-2 bg-amber-950/40 border border-amber-500/30 rounded-2xl px-4 py-2.5">
            <span className="text-xl">🔥</span>
            <div>
              <p className="text-[10px] font-black text-amber-300 uppercase tracking-widest">
                Racha ×{selectedAxo.cpu_win_streak} activa
              </p>
              <p className="text-[9px] text-slate-400">
                Gana y obtendrás +{Math.min(50, selectedAxo.cpu_win_streak * 15)}% FRJ extra
              </p>
            </div>
          </div>
        )}
        {error && (
          <div className="mt-4 bg-red-950/50 border border-red-500/30 text-red-300 text-xs font-bold rounded-2xl p-4 max-w-sm text-center">
            <p>{error}</p>
            <button
              onClick={() => { setError(null); fetchResult(); }}
              className="mt-3 px-4 py-2 bg-red-800/50 hover:bg-red-700/50 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all"
            >
              Reintentar
            </button>
          </div>
        )}
      </div>
    );
  }

  // ── Derived display values ────────────────────────────────────────────────
  const cpuNearWin   = phase === 'animating' && cpuMatchesAll.some(m => m.length / 16 >= 0.7);
  const cards        = result?.drawn_cards_sample ?? [];
  const currentCard  = calledIdx >= 0 ? cards[calledIdx] : null;
  const currentNum   = currentCard ? (nameToNum.get(currentCard.toLowerCase()) ?? 0) : 0;
  // All called cards so far, newest first. On result show all — avoids last card being missing.
  const historyCards = phase === 'result'
    ? [...cards].reverse()
    : (calledIdx >= 0 ? cards.slice(0, calledIdx + 1).reverse() : []);

  // Numbers of the 4 cards that completed the winning line — highlighted in history
  const winningCardNums = new Set<number>();
  if (playerWon && playerWinLine.length > 0) {
    playerWinLine.forEach(i => { const n = playerBoardNums[i]; if (n) winningCardNums.add(n); });
  } else if (cpuWon && cpuWinLine.length > 0) {
    cpuWinLine.forEach(i => { const n = cpuBoardsNums[cpuWinnerBotIdx]?.[i]; if (n) winningCardNums.add(n); });
  }

  // ── Animation + Result ────────────────────────────────────────────────────
  return (
    <div className="relative space-y-2">

      {/* ── Called card strip — card images, newest first, horizontally scrollable ─── */}
      {(phase === 'animating' || phase === 'result') && historyCards.length > 0 && (
        <div className="overflow-x-auto flex items-end gap-1 px-2 py-1
          [&::-webkit-scrollbar]:hidden [-ms-overflow-style:none] [scrollbar-width:none]">
          {historyCards.map((name, i) => {
            const n         = nameToNum.get(name.toLowerCase()) ?? 0;
            const img        = n ? CARD_IMAGE[n] : null;
            const em         = n ? LOTERIA_EMOJI[n] : '🃏';
            const isCurr     = phase === 'animating' && i === 0;
            const isWinCard  = winningCardNums.has(n);
            // Current card: large (~96px). History: small (~48px).
            const cardW      = isCurr ? 96 : 48;
            const cardH      = Math.round(cardW * 1.5);

            return (
              <div
                key={cards.length - 1 - i}
                className={`shrink-0 relative group cursor-pointer transition-transform duration-200
                  ${!isCurr ? 'hover:scale-150 hover:z-20' : ''}`}
                style={{
                  width: cardW,
                  height: cardH,
                  marginLeft: i > 0 && !isCurr ? '-8px' : undefined,
                  filter: isWinCard
                    ? 'drop-shadow(0 0 8px rgba(251,191,36,0.85))'
                    : undefined,
                  opacity: 1,
                }}
                title={name}
              >
                {/* Card image */}
                <div
                  className={`absolute inset-0 overflow-hidden rounded-lg bg-[#0a0a14]
                    ${isCurr
                      ? 'border border-indigo-500/30 shadow-lg shadow-indigo-500/20'
                      : 'border border-white/10 rounded-md'}`}
                >
                  {img ? (
                    <Image
                      src={img}
                      alt={name}
                      className={`absolute inset-0 w-full h-full object-cover ${isCurr ? 'animate-card-call' : ''}`}
                      draggable={false}
                      fill
                      sizes={`${cardW}px`}
                    />
                  ) : (
                    /* Fallback: emoji + gradient when no image */
                    <div className="absolute inset-0 flex items-center justify-center text-2xl"
                      style={{
                        background: `radial-gradient(110% 75% at 50% 0%, hsl(${(n*47)%360},75%,55%) 0%, hsl(${(n*47)%360},70%,30%) 55%, hsl(${(n*47)%360},80%,12%) 100%)`,
                      }}>
                      {em}
                    </div>
                  )}
                </div>
                {/* Progress badge on current card */}
                {isCurr && (
                  <span className="absolute -top-1 -right-1 z-10 bg-indigo-600 text-white
                    text-[9px] font-black px-1.5 py-0.5 rounded-full leading-none
                    shadow-md">
                    {calledIdx + 1}/{cards.length}
                  </span>
                )}
              </div>
            );
          })}
        </div>
      )}

      {/* ── CPU near-win warning ───────────────────────────────────────── */}
      {cpuNearWin && (
        <div className="animate-result-fade-in flex items-center gap-2 bg-amber-950/80 border border-amber-500/40 rounded-2xl px-3 py-2 text-amber-300 text-xs font-black">
          <span>⚠️</span>
          <span>CPU cerca...</span>
        </div>
      )}

      {/* ── Boards — side-by-side layout ────────────────────────────────── */}
      {(phase === 'animating' || phase === 'result') && (() => {
        // Danger sort: most dangerous bot goes to front
        const cpuSortedIndices = cpuBoardsNums
          .map((_, i) => i)
          .sort((a, b) => cpuThreat(cpuMatchesAll[b] ?? []) - cpuThreat(cpuMatchesAll[a] ?? []));
        const frontIdx        = cpuSortedIndices[0];
        const backIndices     = cpuSortedIndices.slice(1);
        // Clear priority and missed when game ends — cleaner result screen
        const isOver          = phase === 'result';
        const cpuPriorityLine = isOver ? [] : calcPriorityLine(cpuMatchesAll[frontIdx] ?? []);
        const playerPriority  = isOver ? [] : priorityLine;
        const playerMissed    = isOver ? [] : playerMissedIndices;
        const cpuDimmed       = isOver ? [] : (frontIdx === 0 ? cpuMissedMain : []);

        return (
        <div className="relative overflow-x-auto">
        <div className="relative flex gap-3 items-start" style={{ minWidth: 'max-content' }}>

          {/* Lucky Save overlay */}
          {showLuckySave && (
            <div className="absolute inset-0 z-20 flex items-center justify-center pointer-events-none animate-result-fade-in">
              <div className="bg-emerald-950/90 border border-emerald-400/50 rounded-2xl px-4 py-2.5 shadow-[0_0_30px_rgba(52,211,153,0.4)] text-center">
                <p className="text-xl">🍀</p>
                <p className="text-[11px] font-black text-emerald-300 uppercase tracking-widest">
                  ¡Suerte de {selectedAxo.name}!
                </p>
                <p className="text-[9px] text-slate-400 mt-0.5">El bot falló en el último momento</p>
              </div>
            </div>
          )}

          {/* LEFT — Player board (natural size) */}
          <div className="flex flex-col items-center gap-1 shrink-0">
            {/* Win flash */}
            {phase === 'animating' && playerWinLine.length > 0 && (
              <p className="text-lg font-black text-amber-400 animate-pulse">🏆 ¡LOTERÍA!</p>
            )}
            <BoardCardGrid
              boardNums={playerBoardNums}
              cardSize={90}
              matchedIndices={playerMatches}
              missedIndices={playerMissed}
              winLine={playerWinLine.length > 0 ? playerWinLine : undefined}
              priorityLine={playerPriority}
              isWinner={playerWon}
              depth={playerWon ? 'front' : 'mid'}
              label={selectedAxo.name}
              variant="player"
            />
          </div>

          {/* RIGHT — CPU boards (natural size) */}
          <div className="flex flex-col items-center gap-2 pointer-events-none shrink-0">
            {/* Main CPU board — most dangerous */}
            <div className="opacity-75">
              <BoardCardGrid
                boardNums={cpuBoardsNums[frontIdx]}
                cardSize={26}
                matchedIndices={cpuMatchesAll[frontIdx] ?? []}
                dimmedIndices={cpuDimmed}
                winLine={cpuWinLine.length > 0 ? cpuWinLine : undefined}
                priorityLine={cpuPriorityLine}
                depth={cpuWon ? 'front' : 'back'}
                isCpuLoser={cpuWon}
                label={BOT_COUNT > 1 ? `Bot ${frontIdx + 1} ⚠` : 'CPU'}
                variant="cpu"
              />
            </div>

            {/* Mini boards 2×2 — Champion only */}
            {BOT_COUNT > 1 && (
              <div className="grid grid-cols-2 gap-1.5 w-full">
                {backIndices.map((botIdx) => (
                  <MiniCpuBoard
                    key={botIdx}
                    boardNums={cpuBoardsNums[botIdx]}
                    matchedIndices={cpuMatchesAll[botIdx] ?? []}
                    priorityLine={isOver ? [] : calcPriorityLine(cpuMatchesAll[botIdx] ?? [])}
                    label={`Bot ${botIdx + 1}`}
                  />
                ))}
              </div>
            )}
          </div>

        </div>
        </div>
        );
      })()}

      {/* ── Economy flash toast ─────────────────────────────────────────────── */}
      {resultFlash && (
        <div
          className={`animate-result-fade-in flex items-center justify-center gap-2 rounded-2xl px-5 py-3 text-center font-black text-lg tracking-wide ${
            resultFlash.type === 'win'
              ? 'bg-emerald-950/90 border border-emerald-400/60 text-emerald-300 shadow-[0_0_24px_rgba(52,211,153,0.5)]'
              : 'bg-rose-950/90 border border-rose-500/50 text-rose-300 shadow-[0_0_24px_rgba(244,63,94,0.4)]'
          }`}
        >
          <span>{resultFlash.type === 'win' ? '🏆' : '💀'}</span>
          <span>{resultFlash.msg}</span>
        </div>
      )}

      {/* ── Result overlay ──────────────────────────────────────────────────── */}
      {phase === 'result' && result && (
        <div
          className="animate-result-fade-in rounded-3xl overflow-hidden border"
          style={{
            background: result.resultado === 'victoria'
              ? 'radial-gradient(ellipse at 50% 0%, rgba(5,46,22,0.9) 0%, rgba(2,6,23,0.95) 60%)'
              : 'radial-gradient(ellipse at 50% 0%, rgba(76,5,25,0.9) 0%, rgba(2,6,23,0.95) 60%)',
            borderColor: result.resultado === 'victoria'
              ? 'rgba(52,211,153,0.3)'
              : 'rgba(244,63,94,0.3)',
          }}
        >
          <div className="p-6 space-y-4 text-center">

            {/* Title + prize */}
            <div>
              {result.resultado === 'victoria' ? (
                <>
                  <h3 className="text-5xl font-black text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-teal-300">
                    ✨ VICTORIA
                  </h3>
                  {result.streak_bonus_pct > 0 ? (
                    <div className="mt-1 space-y-1">
                      {/* Breakdown */}
                      <div className="text-[10px] text-slate-400 font-bold">
                        Base: {(result.prize_gal / (1 + result.streak_bonus_pct / 100)).toFixed(1)} FRJ
                      </div>
                      <div className="text-[10px] text-amber-400 font-black">
                        🔥 Racha ×{result.win_streak_after - 1} +{result.streak_bonus_pct}%:{' '}
                        +{(result.prize_gal - result.prize_gal / (1 + result.streak_bonus_pct / 100)).toFixed(1)} FRJ
                      </div>
                      <div className="h-px bg-white/10 w-32 mx-auto" />
                      <p className="text-3xl font-black text-white">
                        +{result.prize_gal.toFixed(1)}{' '}
                        <span className="text-lg text-emerald-300">FRJ</span>
                      </p>
                    </div>
                  ) : (
                    <p className="text-3xl font-black text-white mt-1">
                      +{result.prize_gal}{' '}
                      <span className="text-lg text-emerald-300">FRJ</span>
                    </p>
                  )}
                  <div className="flex items-center justify-center gap-2 mt-1">
                    <Sparkles size={12} className="text-indigo-400" />
                    <span className="text-indigo-300 text-[11px] font-black">
                      +{result.axo_xp_gained} XP
                    </span>
                  </div>
                </>
              ) : (
                <>
                  <h3 className="text-5xl font-black text-transparent bg-clip-text bg-gradient-to-r from-rose-400 to-red-300">
                    💀 DERROTA
                  </h3>
                  <p className="text-sm text-slate-400 mt-1">
                    El CPU completó su línea primero...
                  </p>
                  {result.streak_broken && (
                    <div className="mt-2 flex flex-col items-center gap-1 animate-result-fade-in">
                      <p className="text-base font-black text-slate-300">💔 Racha rota</p>
                      <p className="text-[9px] text-slate-500">
                        Racha de {selectedAxo.cpu_win_streak} victoria{selectedAxo.cpu_win_streak !== 1 ? 's' : ''} terminada
                      </p>
                    </div>
                  )}
                </>
              )}
            </div>

            {/* Stats */}
            <div className="grid grid-cols-3 gap-2">
              <div className="bg-slate-950/60 border border-white/5 rounded-2xl p-3">
                <p className="text-[9px] text-slate-500 uppercase tracking-widest">Cartas</p>
                <p className="text-base font-black text-white">{result.turns}</p>
              </div>
              <div className="bg-slate-950/60 border border-white/5 rounded-2xl p-3">
                <p className="text-[9px] text-slate-500 uppercase tracking-widest">XP Axo</p>
                <p className="text-base font-black text-indigo-300">+{result.axo_xp_gained}</p>
              </div>
              <div className="bg-slate-950/60 border border-white/5 rounded-2xl p-3">
                <p className="text-[9px] text-slate-500 uppercase tracking-widest">XP Tabla</p>
                <p className="text-base font-black text-emerald-300">+{result.board_xp_gained}</p>
              </div>
            </div>

            {/* Lucky Save badge */}
            {result.lucky_save_occurred && (
              <div className="bg-emerald-950/30 border border-emerald-500/20 rounded-2xl p-3 text-left">
                <p className="text-[10px] font-black text-emerald-300 uppercase tracking-wider">
                  🍀 Lucky Save activado
                </p>
                <p className="text-[9px] text-slate-400 mt-0.5">
                  Tu suerte bloqueó la victoria del bot en el turno {result.lucky_save_turn !== null ? result.lucky_save_turn + 1 : '?'}
                </p>
              </div>
            )}

            {/* OJO saves badge */}
            {result.wisdom_saves > 0 && (
              <div className="bg-indigo-950/30 border border-indigo-500/20 rounded-2xl p-3 text-left">
                <p className="text-[10px] font-black text-indigo-300 uppercase tracking-wider">
                  👁️ OJO activo
                </p>
                <p className="text-[9px] text-slate-400 mt-0.5">
                  Tu concentración evitó {result.wisdom_saves} error{result.wisdom_saves !== 1 ? 'es' : ''} en tu línea prioritaria
                </p>
              </div>
            )}

            {/* Missed cards */}
            {result.player_missed_cards?.length > 0 && (
              <div className="bg-rose-950/30 border border-rose-500/20 rounded-2xl p-3 text-left">
                <p className="text-[10px] font-black text-rose-300 uppercase tracking-wider mb-1">
                  😵 Distracciones ({result.player_missed_cards.length})
                </p>
                <p className="text-[9px] text-slate-400 leading-normal">
                  {result.player_missed_cards.slice(0, 5).join(', ')}
                  {result.player_missed_cards.length > 5 ? '...' : ''}
                  {' '}— ¡Mejora el OJO!
                </p>
              </div>
            )}

            {/* Actions — 3 levels of commitment */}
            <div className="flex flex-col gap-2 pt-1">
              {showPlayAgain && (
                <>
                  {/* Level 1: Play again instantly — same axo, board, room */}
                  <button
                    onClick={onPlayAgainInPlace}
                    className="w-full py-4 bg-gradient-to-r from-[var(--brand-hot)] to-indigo-600 hover:from-pink-500 hover:to-indigo-500 text-white font-black text-lg uppercase tracking-widest rounded-2xl transition-all shadow-[0_0_30px_var(--brand-glow)] active:scale-[0.97] animate-result-fade-in"
                    style={{ borderRadius: '20px' }}
                  >
                    <Play size={16} className="inline mr-2" fill="currentColor" />
                    JUGAR OTRA VEZ
                  </button>

                  {/* Level 2: Change table or room */}
                  <button
                    onClick={onChangeBoard}
                    className="w-full py-3 border border-slate-700 hover:border-slate-500 text-slate-300 hover:text-white text-xs font-black uppercase tracking-widest rounded-2xl transition-all active:scale-[0.98] animate-result-fade-in"
                  >
                    🔄 Cambiar Tabla o Sala
                  </button>
                </>
              )}

              {/* Level 3: Full reset */}
              <button
                onClick={onChangeAll}
                className="w-full py-2 text-slate-500 hover:text-slate-300 text-[10px] font-black uppercase tracking-widest transition-colors"
              >
                ← Cambiar todo
              </button>
            </div>

          </div>
        </div>
      )}
    </div>
  );
}
