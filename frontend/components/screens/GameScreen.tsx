"use client";

import React, { useMemo, useState, useRef, useCallback, useEffect } from "react";
import { Play, Sparkles, RotateCcw, ArrowLeft, Trophy, Frown } from "lucide-react";
import BoardCardGrid from "../ui/BoardCardGrid";
import GritonBanner from "../ui/GritonBanner";
import OpponentStrip, { type OpponentInfo } from "../ui/OpponentStrip";
import TensionEffects, { type TensionLevel } from "../ui/TensionEffects";
import AxoAvatar, { type AxoReaction } from "../ui/AxoAvatar";
import MiniGriton from "../ui/MiniGriton";
import CalledCardsHistory, { type CardHistoryEntry } from "../ui/CalledCardsHistory";
import ChatFeed, { type ChatMessage } from "../chat/ChatFeed";
import { LOTERIA_EMOJI, CARD_IMAGE } from "../ui/LoteriaCard";
import Image from "next/image";

// ── Win-line definitions ──────────────────────────────────────────────────────

const WINNING_LINES: number[][] = [
  [0, 1, 2, 3], [4, 5, 6, 7], [8, 9, 10, 11], [12, 13, 14, 15],
  [0, 4, 8, 12], [1, 5, 9, 13], [2, 6, 10, 14], [3, 7, 11, 15],
  [0, 5, 10, 15], [3, 6, 9, 12],
];

// ── Pattern metadata ──────────────────────────────────────────────────────────

const PATTERN_META: Record<string, { icon: string; label: string; cells: number[] }> = {
  line:          { icon: '📏', label: 'Línea',          cells: [] },  // cells = priority-line (dynamic)
  cuadrito:      { icon: '🟫', label: 'Cuadrito',       cells: [0,1,4,5, 1,2,5,6, 2,3,6,7, 4,5,8,9, 5,6,9,10, 6,7,10,11, 8,9,12,13, 9,10,13,14, 10,11,14,15] },
  pocito:        { icon: '🧿', label: 'El Pocito',      cells: [5, 6, 9, 10] },
  esquinas:      { icon: '🔲', label: '4 Esquinas',     cells: [0, 3, 12, 15] },
  cruz:          { icon: '✝️', label: 'La Cruz',        cells: [] },  // depends on row+col combo
  cruz_diagonal: { icon: '✖️', label: 'La X',           cells: [0, 3, 5, 6, 9, 10, 12, 15] },
  l_shape:       { icon: '🔡', label: 'La L',           cells: [0,1,2,3,4,8,12] },
  z_shape:       { icon: '🅿️', label: 'La Z',           cells: [0,1,2,3,6,9,12,13,14,15] },
  full_board:    { icon: '🏆', label: 'Full Board',     cells: Array.from({length:16},(_,i)=>i) },
};

function getPatternHintCells(patterns: string[]): number[] {
  const cells = new Set<number>();
  for (const p of patterns) {
    if (p === 'line' || p === 'cruz') continue; // too broad for static hints
    const meta = PATTERN_META[p];
    if (meta) meta.cells.forEach(c => cells.add(c));
  }
  return [...cells];
}

// ── Types ─────────────────────────────────────────────────────────────────────

export type GameMode = "cpu" | "auto" | "manual";

export interface PlayerBoardState {
  boardNums: number[];
  matchedIndices: number[];
  boardId?: number;
}

export interface GameScreenProps {
  // ── Core ────────────────────────────────────────────────────────────────
  mode: GameMode;
  phase: "loading" | "countdown" | "playing" | "result";

  // ── Player ──────────────────────────────────────────────────────────────
  axoName: string;
  playerBoards: PlayerBoardState[];
  /** Cell indices affected by salinity fog (manual mode stat effect) */
  salinityFogCells?: number[];

  // ── Cards ───────────────────────────────────────────────────────────────
  allCards: any[];
  currentCard: { cardId?: number; cardNumber?: number; turn: number; windowMs?: number; name?: string } | null;
  totalCards?: number;

  // ── Opponents ───────────────────────────────────────────────────────────
  opponents: OpponentInfo[];

  // ── Tension ─────────────────────────────────────────────────────────────
  tensionLevel: TensionLevel;
  /** IDs of axolotitos near win */
  nearWinPlayers?: number[];

  // ── Countdown ───────────────────────────────────────────────────────────
  countdownSeconds?: number;

  // ── Manual mode actions ─────────────────────────────────────────────────
  /** Highlight cell matching current card (manual mode) */
  highlightedCell?: number | null;
  /** Tapped when a cell is pressed (manual mode) */
  onCellTap?: (boardIdx: number, cellIdx: number) => void;
  /** Shout ¡LOTERÍA! button (manual mode) */
  onShoutLoteria?: () => void;
  /** Use a hint (manual mode) */
  onUseHint?: () => void;
  hintsRemaining?: number;
  showActionBar?: boolean;

  // ── Auto mode ───────────────────────────────────────────────────────────
  escrowBalance?: number;
  initialBudget?: number;
  onRecall?: () => void;

  // ── Result ──────────────────────────────────────────────────────────────
  result?: {
    resultado: "victoria" | "derrota";
    prize_gal?: number;
    axo_xp_gained?: number;
    board_xp_gained?: number;
    turns: number;
    player_missed_cards?: string[];
    streak_bonus_pct?: number;
    streak_broken?: boolean;
    win_streak_after?: number;
    lucky_save_occurred?: boolean;
    wisdom_saves?: number;
  };

  // ── Result screen extras (winning board, history, MiniGriton) ──────────
  /** Card names called during the game, in order */
  calledCardsHistory?: string[];
  /** Map from card name (lowercase) → lotería number (1-54) */
  nameToNumMap?: Map<string, number>;
  /** Winning line indices on the playerʼs board (empty until result phase) */
  playerWinLine?: number[];
  /** Winning line indices on the CPU board that won (empty until result) */
  cpuWinLine?: number[];
  /** The CPU winnerʼs board numbers (16 cells; used when player loses) */
  cpuWinnerBoardNums?: number[];
  /** The playerʼs matched indices at result time */
  playerMatchedResult?: number[];
  /** The playerʼs missed indices at result time */
  playerMissedResult?: number[];

  // ── Win patterns ────────────────────────────────────────────────────────────
  winPatterns?: string[];

  // ── Chat ─────────────────────────────────────────────────────────────────
  /** Chat messages for the ChatFeed */
  chatMessages?: ChatMessage[];
  /** WebSocket send function for chat */
  onSendChat?: ((msg: any) => void) | null;
  /** Whether the chat feed is collapsed */
  chatCollapsed?: boolean;
  /** Toggle chat collapse */
  onToggleChat?: () => void;

  // ── Actions ─────────────────────────────────────────────────────────────
  onPlayAgain?: () => void;
  onChangeBoard?: () => void;
  onChangeAll?: () => void;

  // ── CPU Speed control ───────────────────────────────────────────────────
  /** Called when player holds to accelerate CPU animation (1 = normal, 2 = fast) */
  onSpeedChange?: (multiplier: number) => void;
  /** Current speed multiplier (shows x2 badge when > 1) */
  speedMultiplier?: number;
}

// ── Helpers ───────────────────────────────────────────────────────────────────

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

// ── Component ─────────────────────────────────────────────────────────────────

export default function GameScreen(props: GameScreenProps) {
  const {
    mode,
    phase,
    axoName,
    playerBoards,
    salinityFogCells = [],
    allCards,
    currentCard,
    totalCards,
    opponents,
    tensionLevel,
    countdownSeconds,
    highlightedCell = null,
    onCellTap,
    onShoutLoteria,
    onUseHint,
    hintsRemaining = 0,
    showActionBar = false,
    escrowBalance,
    initialBudget,
    onRecall,
    result,
    calledCardsHistory = [],
    nameToNumMap,
    playerWinLine = [],
    cpuWinLine = [],
    cpuWinnerBoardNums,
    playerMatchedResult,
    playerMissedResult = [],
    winPatterns = ['line', 'cuadrito'],
    onPlayAgain,
    onChangeBoard,
    onChangeAll,
    onSpeedChange,
    speedMultiplier = 1,
    chatMessages = [],
    onSendChat,
    chatCollapsed = true,
    onToggleChat,
  } = props;

  const patternHintCells = useMemo(() => getPatternHintCells(winPatterns), [winPatterns]);

  // ── Axo reaction derived from game state ─────────────────────────────────
  const axoReaction: AxoReaction = useMemo(() => {
    if (phase === "result" && result?.resultado === "victoria") return "won";
    if (phase === "result" && result?.resultado === "derrota") return "lost";
    if (tensionLevel === "critical" || tensionLevel === "high") return "tension_critical";
    if (currentCard) return "card_called";
    return "idle";
  }, [phase, result, tensionLevel, currentCard]);

  // ── Sort opponents by threat ─────────────────────────────────────────────
  const sortedOpponents = useMemo(() => {
    return [...opponents].sort(
      (a, b) => cpuThreat(b.matchedIndices ?? []) - cpuThreat(a.matchedIndices ?? [])
    );
  }, [opponents]);

  // ── Primary board ────────────────────────────────────────────────────────
  const primaryBoard = playerBoards[0];
  const primaryMatched = primaryBoard?.matchedIndices ?? [];
  const primaryBoardNums = primaryBoard?.boardNums ?? Array(16).fill(0);
  const priorityLine = calcPriorityLine(primaryMatched);

  // ── Card history entries for result screen ────────────────────────────────
  const cardHistoryEntries: CardHistoryEntry[] = useMemo(() => {
    if (!calledCardsHistory.length || !nameToNumMap) return [];
    const missedSet = new Set(
      (result?.player_missed_cards ?? []).map((m: string) => m.toLowerCase())
    );
    const matchedIndicesSet = new Set(playerMatchedResult ?? primaryMatched);
    const playerBoardNumSet = new Set(primaryBoardNums.filter((n) => n > 0));

    return calledCardsHistory.map((cardName, i) => {
      const num = nameToNumMap.get(cardName.toLowerCase()) ?? 0;
      const onPlayerBoard = num > 0 && playerBoardNumSet.has(num);
      const isMatched = onPlayerBoard && !missedSet.has(cardName.toLowerCase());
      const isMissed = onPlayerBoard && missedSet.has(cardName.toLowerCase());

      return {
        name: cardName,
        number: num,
        turn: i,
        matched: isMatched,
        missed: isMissed,
      };
    });
  }, [calledCardsHistory, nameToNumMap, result?.player_missed_cards, playerMatchedResult, primaryMatched, primaryBoardNums]);

  // ── Winning card numbers (cards that form the winning line) ───────────────
  const winningCardNumbers: number[] = useMemo(() => {
    const winLine = result?.resultado === "victoria" ? playerWinLine : cpuWinLine;
    if (!winLine || winLine.length === 0) return [];

    const boardNums =
      result?.resultado === "victoria"
        ? primaryBoardNums
        : cpuWinnerBoardNums ?? [];

    return winLine
      .map((idx) => boardNums[idx])
      .filter((n) => n && n > 0) as number[];
  }, [result?.resultado, playerWinLine, cpuWinLine, primaryBoardNums, cpuWinnerBoardNums]);

  // ── Cercanía (how close player was to winning) ─────────────────────────────
  const cercaniaDisplay = useMemo(() => {
    if (phase !== "result" || !result) return null;
    if (result.resultado === "victoria") return null; // no need to show when won

    const matchedCount = primaryMatched.length;
    const priorityCount = priorityLine.filter((i) => primaryMatched.includes(i)).length;
    const totalNeeded = 4; // standard line needs 4

    if (priorityCount >= 3) {
      return { text: `¡A 1 carta!`, pct: Math.round((priorityCount / totalNeeded) * 100), urgent: true };
    }
    if (priorityCount >= 2) {
      return { text: `Te faltaron ${totalNeeded - priorityCount} cartas`, pct: Math.round((priorityCount / totalNeeded) * 100), urgent: false };
    }
    if (matchedCount > 0) {
      return { text: `${matchedCount} aciertos`, pct: Math.round((matchedCount / 16) * 100), urgent: false };
    }
    return null;
  }, [phase, result, primaryMatched, priorityLine]);

  // ── CPU speed hold gesture ────────────────────────────────────────────────
  const holdTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const [holding, setHolding] = useState(false);

  const handleSpeedHoldStart = useCallback(() => {
    if (mode !== "cpu") return;
    holdTimerRef.current = setTimeout(() => {
      setHolding(true);
      onSpeedChange?.(2);
    }, 400);
  }, [mode, onSpeedChange]);

  const handleSpeedHoldEnd = useCallback(() => {
    if (holdTimerRef.current) clearTimeout(holdTimerRef.current);
    setHolding(false);
    onSpeedChange?.(1);
  }, [onSpeedChange]);

  // Cleanup hold timer on unmount
  useEffect(() => {
    return () => {
      if (holdTimerRef.current) clearTimeout(holdTimerRef.current);
    };
  }, []);

  // Keyboard: Space bar hold for desktop
  useEffect(() => {
    if (mode !== "cpu") return;
    const onKeyDown = (e: KeyboardEvent) => {
      if (e.code === "Space" && !e.repeat) {
        e.preventDefault();
        handleSpeedHoldStart();
      }
    };
    const onKeyUp = (e: KeyboardEvent) => {
      if (e.code === "Space") {
        e.preventDefault();
        handleSpeedHoldEnd();
      }
    };
    window.addEventListener("keydown", onKeyDown);
    window.addEventListener("keyup", onKeyUp);
    return () => {
      window.removeEventListener("keydown", onKeyDown);
      window.removeEventListener("keyup", onKeyUp);
    };
  }, [mode, handleSpeedHoldStart, handleSpeedHoldEnd]);

  // ── Loading ──────────────────────────────────────────────────────────────
  if (phase === "loading") {
    return (
      <div className="flex flex-col items-center justify-center py-20 gap-4">
        <div className="w-12 h-12 border-4 border-[var(--brand-hot)] border-t-transparent rounded-full animate-spin" />
        <p className="text-slate-400 text-xs font-black uppercase tracking-widest animate-pulse">
          {mode === "manual" ? "Conectando a la sala..." : "Iniciando partida..."}
        </p>
        {mode === "auto" && (
          <div className="flex items-center gap-2 bg-purple-950/40 border border-purple-500/30 rounded-2xl px-4 py-2.5 mt-2">
            <span className="text-lg">🦎</span>
            <p className="text-[10px] font-black text-purple-300 uppercase tracking-widest">
              {axoName} está entrando a las canchas
            </p>
          </div>
        )}
      </div>
    );
  }

  // ── Countdown ────────────────────────────────────────────────────────────
  if (phase === "countdown") {
    return (
      <div className="flex flex-col items-center justify-center py-20 gap-4">
        <div className="text-8xl font-black text-white animate-pulse">
          {countdownSeconds ?? "..."}
        </div>
        <p className="text-slate-400 text-xs font-black uppercase tracking-widest">
          {countdownSeconds === 0 ? "¡YA!" : "Preparados..."}
        </p>
      </div>
    );
  }

  // ── Result ───────────────────────────────────────────────────────────────
  if (phase === "result" && result) {
    const won = result.resultado === "victoria";
    const winLineToShow = won ? playerWinLine : cpuWinLine;
    const boardToShow = won
      ? primaryBoardNums
      : cpuWinnerBoardNums ?? primaryBoardNums;
    const matchedToShow = won ? primaryMatched : [];

    return (
      <TensionEffects level={tensionLevel}>
        <div
          className="animate-result-fade-in rounded-3xl overflow-hidden border max-h-[85vh] overflow-y-auto scrollbar-hide"
          style={{
            background: won
              ? "radial-gradient(ellipse at 50% 0%, rgba(5,46,22,0.9) 0%, rgba(2,6,23,0.95) 60%)"
              : "radial-gradient(ellipse at 50% 0%, rgba(76,5,25,0.9) 0%, rgba(2,6,23,0.95) 60%)",
            borderColor: won
              ? "rgba(52,211,153,0.3)"
              : "rgba(244,63,94,0.3)",
          }}
        >
          <div className="p-5 space-y-4 text-center">
            {/* Axo reaction */}
            <AxoAvatar name={axoName} reaction={axoReaction} size={80} />

            {/* Title + prize */}
            <div>
              {won ? (
                <>
                  <h3 className="text-4xl font-black text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-teal-300">
                    ✨ ¡VICTORIA!
                  </h3>
                  <p className="text-3xl font-black text-white mt-1">
                    +{result.prize_gal?.toFixed(1) ?? "?"}{" "}
                    <span className="text-lg text-emerald-300">FRJ</span>
                  </p>
                  {(result.streak_bonus_pct ?? 0) > 0 && (
                    <p className="text-[10px] text-amber-400 font-black mt-1">
                      🔥 Racha +{result.streak_bonus_pct}% bonus
                    </p>
                  )}
                  <div className="flex items-center justify-center gap-2 mt-1">
                    <Sparkles size={12} className="text-indigo-400" />
                    <span className="text-indigo-300 text-[11px] font-black">
                      +{result.axo_xp_gained ?? 0} XP
                    </span>
                  </div>
                </>
              ) : (
                <>
                  <h3 className="text-4xl font-black text-transparent bg-clip-text bg-gradient-to-r from-rose-400 to-red-300">
                    💀 DERROTA
                  </h3>
                  <p className="text-sm text-slate-400 mt-1">
                    {mode === "cpu" ? "El CPU completó su línea primero" : "Otro jugador ganó la partida"}
                  </p>
                  {result.streak_broken && (
                    <p className="text-sm font-black text-slate-300 mt-1">💔 Racha rota</p>
                  )}
                </>
              )}
            </div>

            {/* ── Winning Board (STAGED: fades in after title) ──────────────── */}
            <div
              className="animate-result-fade-in pt-2"
              style={{ animationDelay: "300ms", animationFillMode: "both" }}
            >
              <div className="flex items-center justify-center gap-2 mb-2">
                <Trophy size={14} className={won ? "text-amber-400" : "text-rose-400"} />
                <span className="text-[10px] font-black uppercase tracking-widest text-slate-400">
                  {won ? "Tabla Ganadora" : "Tabla del Ganador"}
                </span>
              </div>

              {/* Player winning board (when won) OR CPU winning board (when lost) */}
              <div className="flex justify-center">
                <BoardCardGrid
                  boardNums={boardToShow}
                  cardSize={won ? 80 : 72}
                  matchedIndices={matchedToShow}
                  missedIndices={won ? playerMissedResult : []}
                  winLine={winLineToShow.length > 0 ? winLineToShow : undefined}
                  priorityLine={[]}
                  isWinner={won}
                  isCpuLoser={!won}
                  variant={won ? "player" : "cpu"}
                  label={won ? axoName : "CPU"}
                />
              </div>

              {/* Cercanía indicator (when lost) */}
              {!won && cercaniaDisplay && (
                <div
                  className={`mt-3 mx-auto inline-flex items-center gap-2 px-4 py-2 rounded-xl border ${
                    cercaniaDisplay.urgent
                      ? "bg-amber-950/40 border-amber-500/30 text-amber-300"
                      : "bg-slate-900/60 border-slate-700/40 text-slate-400"
                  }`}
                >
                  <Frown size={12} className={cercaniaDisplay.urgent ? "text-amber-400" : "text-slate-500"} />
                  <span className="text-[10px] font-black uppercase tracking-wider">
                    {cercaniaDisplay.text}
                  </span>
                  {/* Mini progress bar */}
                  <div className="w-16 h-1.5 bg-slate-800 rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full transition-all duration-1000 ${
                        cercaniaDisplay.urgent ? "bg-amber-500" : "bg-slate-500"
                      }`}
                      style={{ width: `${cercaniaDisplay.pct}%` }}
                    />
                  </div>
                </div>
              )}
            </div>

            {/* ── Mini Gritón (STAGED: fades in after board) ────────────────── */}
            {calledCardsHistory.length > 0 && nameToNumMap && winningCardNumbers.length > 0 && (
              <div
                className="animate-result-fade-in pt-2"
                style={{ animationDelay: "600ms", animationFillMode: "both" }}
              >
                <div className="flex items-center justify-center gap-2 mb-2">
                  <span className="text-[10px] font-black uppercase tracking-widest text-slate-400">
                    🎤 El Gritón
                  </span>
                </div>
                <MiniGriton
                  calledCards={calledCardsHistory}
                  nameToNum={nameToNumMap}
                  winningCardNumbers={winningCardNumbers}
                  isWinner={won}
                />
              </div>
            )}

            {/* ── Card History Strip (STAGED: fades in last) ────────────────── */}
            {cardHistoryEntries.length > 0 && (
              <div
                className="animate-result-fade-in pt-1"
                style={{ animationDelay: "900ms", animationFillMode: "both" }}
              >
                <CalledCardsHistory entries={cardHistoryEntries} />
              </div>
            )}

            {/* Stats */}
            <div
              className="animate-result-fade-in grid grid-cols-3 gap-2"
              style={{ animationDelay: "400ms", animationFillMode: "both" }}
            >
              <div className="bg-slate-950/60 border border-white/5 rounded-2xl p-3">
                <p className="text-[9px] text-slate-500 uppercase tracking-widest">Cartas</p>
                <p className="text-base font-black text-white">{result.turns}</p>
              </div>
              <div className="bg-slate-950/60 border border-white/5 rounded-2xl p-3">
                <p className="text-[9px] text-slate-500 uppercase tracking-widest">XP Axo</p>
                <p className="text-base font-black text-indigo-300">+{result.axo_xp_gained ?? 0}</p>
              </div>
              <div className="bg-slate-950/60 border border-white/5 rounded-2xl p-3">
                <p className="text-[9px] text-slate-500 uppercase tracking-widest">XP Tabla</p>
                <p className="text-base font-black text-emerald-300">+{result.board_xp_gained ?? 0}</p>
              </div>
            </div>

            {/* Lucky Save */}
            {result.lucky_save_occurred && (
              <div className="bg-emerald-950/30 border border-emerald-500/20 rounded-2xl p-3 text-left">
                <p className="text-[10px] font-black text-emerald-300 uppercase tracking-wider">
                  🍀 Lucky Save activado
                </p>
                <p className="text-[9px] text-slate-400 mt-0.5">
                  Tu suerte bloqueó la victoria del oponente
                </p>
              </div>
            )}

            {/* Actions */}
            <div className="flex flex-col gap-2 pt-1">
              {onPlayAgain && (
                <>
                  <button
                    onClick={onPlayAgain}
                    className="w-full py-4 bg-gradient-to-r from-[var(--brand-hot)] to-indigo-600 hover:from-pink-500 hover:to-indigo-500 text-white font-black text-lg uppercase tracking-widest rounded-2xl transition-all shadow-[0_0_30px_var(--brand-glow)] active:scale-[0.97]"
                  >
                    <Play size={16} className="inline mr-2" fill="currentColor" />
                    JUGAR OTRA VEZ
                  </button>
                  {onChangeBoard && (
                    <button
                      onClick={onChangeBoard}
                      className="w-full py-3 border border-slate-700 hover:border-slate-500 text-slate-300 hover:text-white text-xs font-black uppercase tracking-widest rounded-2xl transition-all active:scale-[0.98]"
                    >
                      <RotateCcw size={12} className="inline mr-1" /> Cambiar Tabla o Sala
                    </button>
                  )}
                </>
              )}
              {onChangeAll && (
                <button
                  onClick={onChangeAll}
                  className="w-full py-2 text-slate-500 hover:text-slate-300 text-[10px] font-black uppercase tracking-widest transition-colors"
                >
                  <ArrowLeft size={10} className="inline mr-1" /> Cambiar todo
                </button>
              )}
            </div>
          </div>
        </div>
        {/* Chat Feed for result phase (always expanded) */}
        {onSendChat && onToggleChat && (
          <ChatFeed
            messages={chatMessages ?? []}
            send={onSendChat ?? null}
            phase="result"
            playMode={mode === "manual" ? "manual" : "auto"}
            collapsed={false}
            onToggleCollapse={onToggleChat}
          />
        )}
      </TensionEffects>
    );
  }

  // ── Playing (mode = cpu | auto | manual) ─────────────────────────────────
  return (
    <TensionEffects level={tensionLevel} disableHeartbeat={mode === "auto"}>
      <div className="relative">
        {/* Chat Feed */}
        {onSendChat && onToggleChat && (
          <ChatFeed
            messages={chatMessages ?? []}
            send={onSendChat ?? null}
            phase={phase}
            playMode={mode === "manual" ? "manual" : "auto"}
            collapsed={chatCollapsed ?? true}
            onToggleCollapse={onToggleChat}
          />
        )}
        <div
          className="space-y-3 animate-slide-step"
          onPointerDown={handleSpeedHoldStart}
          onPointerUp={handleSpeedHoldEnd}
          onPointerLeave={handleSpeedHoldEnd}
          onPointerCancel={handleSpeedHoldEnd}
        >
        {/* ── Speed badge (CPU mode only) ──────────────────────────────────── */}
        {mode === "cpu" && holding && (
          <div className="flex justify-center -mb-1">
            <span className="inline-flex items-center gap-1 bg-amber-500/90 text-white font-black text-xs px-3 py-1 rounded-full shadow-[0_0_16px_rgba(245,158,11,0.5)] animate-pulse">
              ⚡ x2
            </span>
          </div>
        )}
        {/* ── AxoAvatar + Status row ─────────────────────────────────────── */}
        <div className="flex items-center justify-between">
          <AxoAvatar name={axoName} reaction={axoReaction} size={60} />

          {/* Escrow info (auto mode only) */}
          {mode === "auto" && escrowBalance != null && (
            <div className="bg-purple-950/40 border border-purple-500/20 rounded-xl px-3 py-1.5 text-right">
              <p className="text-[8px] text-purple-400 uppercase tracking-widest font-black">
                En custodia
              </p>
              <p className="text-sm font-black text-purple-200">
                {escrowBalance.toFixed(1)} FRJ
              </p>
            </div>
          )}

          {/* Player count badge (manual mode) */}
          {mode === "manual" && (
            <div className="bg-pink-950/40 border border-pink-500/20 rounded-xl px-3 py-1.5">
              <p className="text-[8px] text-pink-400 uppercase tracking-widest font-black">
                Jugadores
              </p>
              <p className="text-sm font-black text-pink-200">
                {opponents.length + 1}
              </p>
            </div>
          )}
        </div>

        {/* ── Gritón Banner ──────────────────────────────────────────────── */}
        <GritonBanner
          card={currentCard}
          totalCards={totalCards}
          allCards={allCards}
          showTimer={mode === "manual"}
        />

        {/* ── Opponent Strip ─────────────────────────────────────────────── */}
        <OpponentStrip opponents={sortedOpponents} cardSize={16} />

        {/* ── Pattern indicator ──────────────────────────────────────────── */}
        {phase === "playing" && winPatterns.length > 0 && (
          <div className="flex items-center justify-center gap-1.5 flex-wrap">
            <span className="text-[8px] font-black uppercase tracking-widest text-slate-500">Para ganar:</span>
            {winPatterns.map(p => {
              const meta = PATTERN_META[p];
              if (!meta) return null;
              return (
                <span
                  key={p}
                  className="flex items-center gap-0.5 px-2 py-0.5 rounded-full bg-violet-950/40 border border-violet-500/25 text-[9px] font-black text-violet-300"
                >
                  {meta.icon} {meta.label}
                </span>
              );
            })}
          </div>
        )}

        {/* ── Player Board ───────────────────────────────────────────────── */}
        <div className="flex justify-center">
          <div className="flex flex-col items-center gap-1">
            <BoardCardGrid
              boardNums={primaryBoardNums}
              cardSize={mode === "manual" ? 80 : 90}
              matchedIndices={primaryMatched}
              winLine={undefined}
              priorityLine={phase === "result" ? [] : priorityLine}
              patternHintCells={phase === "playing" ? patternHintCells : []}
              isWinner={result?.resultado === "victoria"}
              interactive={mode === "manual"}
              highlightedCell={mode === "manual" ? highlightedCell : null}
              salinityFogCells={mode === "manual" ? salinityFogCells : []}
              onCellTap={(idx) => onCellTap?.(0, idx)}
              variant="player"
              label={axoName}
              winPatterns={winPatterns}
            />
          </div>
        </div>

        {/* ── Action Bar (manual mode only) ──────────────────────────────── */}
        {showActionBar && mode === "manual" && (
          <div className="flex items-center gap-3 pt-2">
            {/* Hint button */}
            <button
              onClick={onUseHint}
              disabled={hintsRemaining <= 0}
              className="flex-1 py-3 bg-indigo-950/60 border border-indigo-500/30 hover:border-indigo-500/60 text-indigo-300 font-black text-xs uppercase tracking-widest rounded-2xl transition-all disabled:opacity-40 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              💡 Pista {hintsRemaining > 0 ? `(${hintsRemaining})` : "(0)"}
            </button>

            {/* ¡LOTERÍA! button */}
            <button
              onClick={onShoutLoteria}
              className="flex-1 py-4 bg-gradient-to-r from-amber-600 to-[var(--brand-hot)] hover:from-amber-500 hover:to-pink-500 text-white font-black text-base uppercase tracking-widest rounded-2xl transition-all shadow-[0_0_24px_var(--brand-glow)] active:scale-[0.96] animate-pulse"
            >
              📣 ¡LOTERÍA!
            </button>
          </div>
        )}

        {/* ── Recall button (auto mode only) ─────────────────────────────── */}
        {mode === "auto" && onRecall && (
          <button
            onClick={onRecall}
            className="w-full py-3 bg-slate-800 hover:bg-red-900/30 border border-slate-700 hover:border-red-500/40 text-slate-300 hover:text-red-300 font-bold text-xs uppercase tracking-widest rounded-2xl transition-all flex items-center justify-center gap-2"
          >
            📣 Llamar de Regreso
          </button>
        )}
      </div>
      </div> {/* close relative wrapper */}
    </TensionEffects>
  );
}
