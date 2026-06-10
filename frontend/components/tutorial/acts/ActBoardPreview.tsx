"use client";

/**
 * ActBoardPreview — Acto 3: cantada interactiva + tour de líneas.
 *
 * Fases:
 *   "intro"       — tablero + diálogo Webito intro → dismiss
 *   "cantada"     — Gritón llama 10 cartas una a una (pausa hasta que el jugador avance).
 *                   Cartas hit: Webito habla + jugador debe TOCAR la celda en el tablero.
 *                   Al completar las 4 de la línea: partículas de victoria + Webito celebra.
 *   "lines-tour"  — Webito explica → cicla las 9 líneas restantes → espera "Continuar"
 *   "full-board"  — Webito dice texto de tabla llena → espera "Continuar"
 *   "outro"       — Webito dice "entendido" → onComplete()
 */

import React, { useState, useCallback, useMemo, useEffect, useRef } from "react";
import WebitoDialogue from "../WebitoDialogue";
import type { WebitoData } from "../TutorialScript";
import {
  ACT3_BOARD_INTRO,
  ACT3_BOARD_REVEALED,
  ACT3_HIT_REACTIONS,
  ACT3_VICTORY,
  ACT3_LINES_EXPLAIN,
  ACT3_FULL_BOARD,
  ACT3_OUTRO,
} from "../dialogues";
import { CARD_IMAGE } from "@/components/ui/LoteriaCard";

// ── Constants ──────────────────────────────────────────────────────────────────

const CARD_SIZE = 48;
const CARD_H    = Math.round(CARD_SIZE * 1.42);
const BIG_CARD  = 96;
const BIG_CARD_H = Math.round(BIG_CARD * 1.42);

const WINNING_LINES: number[][] = [
  [0,1,2,3], [4,5,6,7], [8,9,10,11], [12,13,14,15],
  [0,4,8,12], [1,5,9,13], [2,6,10,14], [3,7,11,15],
  [0,5,10,15], [3,6,9,12],
];
const LINE_LABELS = [
  "Fila 1","Fila 2","Fila 3","Fila 4",
  "Columna 1","Columna 2","Columna 3","Columna 4",
  "Diagonal ↘","Diagonal ↙",
];

// ── Helpers ───────────────────────────────────────────────────────────────────

/** djb2 hash — converts Privy user ID string to a stable numeric seed. */
function stringToSeed(s: string): number {
  let h = 5381;
  for (let i = 0; i < s.length; i++) {
    h = ((h << 5) + h) + s.charCodeAt(i);
    h = h & h; // 32-bit
  }
  return Math.abs(h);
}

function seededBoard(seed: number): number[] {
  const nums = Array.from({ length: 54 }, (_, i) => i + 1);
  let s = (seed || 42) & 0xffffffff;
  for (let i = nums.length - 1; i > 0; i--) {
    s = (s * 1664525 + 1013904223) & 0xffffffff;
    const j = Math.abs(s) % (i + 1);
    [nums[i], nums[j]] = [nums[j], nums[i]];
  }
  return nums.slice(0, 16);
}

function cardName(num: number): string {
  const path = CARD_IMAGE[num] ?? "";
  const m = path.match(/\d+ - (.+)\.webp$/i);
  return m ? m[1] : `Carta ${num}`;
}

interface CantadaCard { num: number; isHit: boolean; boardIdx: number | null; }

function buildCantada(board: number[], seed: number): { seq: CantadaCard[]; lineIdx: number } {
  const lineIdx = Math.abs(seed) % WINNING_LINES.length;
  const line = WINNING_LINES[lineIdx];
  const hitNums = line.map(pos => board[pos]);
  const boardSet = new Set(board);
  const pool = Array.from({ length: 54 }, (_, i) => i + 1).filter(n => !boardSet.has(n));
  let s = (seed * 31) & 0xffffffff;
  const misses: number[] = [];
  const rem = [...pool];
  for (let i = 0; i < 6 && rem.length > 0; i++) {
    s = (s * 1664525 + 1013904223) & 0xffffffff;
    const j = Math.abs(s) % rem.length;
    misses.push(rem.splice(j, 1)[0]);
  }
  // hits at positions 2,4,7,9 → miss=0,1, hit=2, miss=3, hit=4, miss=5,6, hit=7, miss=8, hit=9
  const HIT_SLOTS = [2, 4, 7, 9];
  const seq: CantadaCard[] = [];
  let hi = 0, mi = 0;
  for (let i = 0; i < 10; i++) {
    if (HIT_SLOTS.includes(i)) {
      seq.push({ num: hitNums[hi], isHit: true, boardIdx: line[hi] });
      hi++;
    } else {
      seq.push({ num: misses[mi++], isHit: false, boardIdx: null });
    }
  }
  return { seq, lineIdx };
}

// ── Particle component ────────────────────────────────────────────────────────

function Particles() {
  const particles = useMemo(() =>
    Array.from({ length: 18 }, (_, i) => ({
      x: 20 + Math.random() * 60,
      y: 20 + Math.random() * 60,
      size: 4 + Math.random() * 6,
      color: ["#fbbf24","#34d399","#f87171","#818cf8","#00e5ff"][i % 5],
      delay: Math.random() * 0.4,
      dur: 0.6 + Math.random() * 0.5,
    })), []);

  return (
    <div className="pointer-events-none absolute inset-0 overflow-hidden rounded-2xl z-30">
      {particles.map((p, i) => (
        <div
          key={i}
          className="absolute rounded-full"
          style={{
            left: `${p.x}%`,
            top: `${p.y}%`,
            width: p.size,
            height: p.size,
            background: p.color,
            boxShadow: `0 0 6px ${p.color}`,
            animation: `particle-pop ${p.dur}s ease-out ${p.delay}s both`,
          }}
        />
      ))}
      <style>{`
        @keyframes particle-pop {
          0%   { transform: scale(0) translate(0,0); opacity: 1; }
          60%  { opacity: 1; }
          100% { transform: scale(1) translate(var(--tx,0px), var(--ty,-40px)); opacity: 0; }
        }
      `}</style>
    </div>
  );
}

// ── Phase type ────────────────────────────────────────────────────────────────

type Phase = "intro" | "shuffling" | "dealing" | "cantada" | "lines-tour" | "full-board" | "outro";

// ── Component ─────────────────────────────────────────────────────────────────

interface Props {
  webito: WebitoData;
  onComplete: () => void;
}

export default function ActBoardPreview({ webito, onComplete }: Props) {
  const [phase, setPhase]           = useState<Phase>("intro");
  const [cantadaStep, setCantadaStep] = useState(0);   // 0 = first card shown
  const [markedIndices, setMarkedIndices] = useState<number[]>([]);
  const [boardTapped, setBoardTapped]     = useState(false);  // hit card tapped on board?
  const [showParticles, setShowParticles] = useState(false);
  // tourLineIdx=-1 = waiting for player to dismiss the lines explain dialogue
  const [tourLineIdx, setTourLineIdx]     = useState(-1);
  // fullBoardCount: how many cells are "filled" in the full-board animation (0→16)
  const [fullBoardCount, setFullBoardCount] = useState(0);
  const [dealingComplete, setDealingComplete] = useState(false);
  const tourTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const userSeed = useMemo(() => stringToSeed(webito.userId), [webito.userId]);
  const board    = useMemo(() => seededBoard(userSeed), [userSeed]);
  const { seq, lineIdx } = useMemo(() => buildCantada(board, userSeed), [board, userSeed]);
  const wonLine = WINNING_LINES[lineIdx];

  // How many hits have we shown so far (including current if hit)
  const hitsSoFar = seq.slice(0, cantadaStep + 1).filter(c => c.isHit).length;
  const hitIndex  = hitsSoFar - 1; // 0-based index of current hit (if current is hit)

  const currentCard = seq[cantadaStep];
  const isComplete  = markedIndices.length === 4;

  // ── Shuffling phase timer ──
  useEffect(() => {
    if (phase !== "shuffling") return;
    const t = setTimeout(() => {
      setPhase("dealing");
    }, 1800);
    return () => clearTimeout(t);
  }, [phase]);

  // ── Dealing phase timer ──
  useEffect(() => {
    if (phase !== "dealing") return;
    setDealingComplete(false);
    const t = setTimeout(() => {
      setDealingComplete(true);
    }, 2500);
    return () => clearTimeout(t);
  }, [phase]);

  // ── Cantada auto-advance ──────────────────────────────────────────────

  useEffect(() => {
    if (phase !== "cantada") return;
    if (isComplete) return; // victory dialogue handles transition via onDismiss

    if (currentCard?.isHit && !boardTapped) return; // pause: waiting for tap

    const delay = boardTapped ? 900 : 1300;
    const t = setTimeout(() => {
      if (cantadaStep < seq.length - 1) {
        setCantadaStep(s => s + 1);
        setBoardTapped(false);
      }
    }, delay);
    return () => clearTimeout(t);
  }, [phase, cantadaStep, boardTapped, isComplete, currentCard, seq.length]);

  // ── Lines tour auto-cycle (continuous loop) ──────────────────────────────────

  useEffect(() => {
    if (phase !== "lines-tour") return;
    tourTimerRef.current = setTimeout(() => setTourLineIdx(i => (i + 1) % WINNING_LINES.length), 420);
    return () => { if (tourTimerRef.current) clearTimeout(tourTimerRef.current); };
  }, [phase, tourLineIdx]);

  // ── Full-board fill animation ─────────────────────────────────────────────
  // When phase==="full-board", mark cells one by one every 70ms

  useEffect(() => {
    if (phase !== "full-board") return;
    if (fullBoardCount >= 16) return;
    const t = setTimeout(() => setFullBoardCount(c => c + 1), 35);
    return () => clearTimeout(t);
  }, [phase, fullBoardCount]);

  // ── Handlers ─────────────────────────────────────────────────────────────

  const handleIntroDismiss = useCallback(() => {
    setPhase("shuffling");
  }, []);

  // Player taps a board cell during cantada
  const handleBoardCellTap = useCallback((gridIdx: number) => {
    if (phase !== "cantada" || boardTapped) return;
    if (!currentCard?.isHit) return;
    if (currentCard.boardIdx !== gridIdx) return; // wrong cell

    setBoardTapped(true);
    setMarkedIndices(prev => {
      const next = [...prev, gridIdx];
      if (next.length === 4) {
        // Line complete!
        setTimeout(() => setShowParticles(true), 100);
        setTimeout(() => setShowParticles(false), 2000);
      }
      return next;
    });
  }, [phase, boardTapped, currentCard]);


  // ── Lines tour computed values ─────────────────────────────────────────────

  const tourActive = WINNING_LINES[tourLineIdx] ?? null;
  const tourLabel  = LINE_LABELS[tourLineIdx] ?? null;

  // ── Cell overlay ──────────────────────────────────────────────────────────

  function cellStyle(gridIdx: number): React.CSSProperties {
    const isMarked  = markedIndices.includes(gridIdx);
    const isWonCell = wonLine.includes(gridIdx);
    const isCurrent = currentCard?.boardIdx === gridIdx && phase === "cantada" && currentCard.isHit && !boardTapped;
    const isTourCell = phase === "lines-tour" && tourActive?.includes(gridIdx);

    if (phase === "lines-tour") {
      // Don't show player marks during tour — clean board so lines are clear
      if (isTourCell) return { background: "rgba(251,191,36,0.45)", boxShadow: "0 0 14px rgba(251,191,36,0.8)" };
      return {};
    }

    if (isComplete && isWonCell) return { background: "rgba(251,191,36,0.45)", boxShadow: "0 0 16px rgba(251,191,36,0.9)" };
    if (isMarked)   return { background: "rgba(52,211,153,0.32)", boxShadow: "0 0 10px rgba(52,211,153,0.6)" };
    if (isCurrent)  return { background: "rgba(0,229,255,0.25)", boxShadow: "0 0 18px rgba(0,229,255,0.8)" };
    return {};
  }

  function cellBorder(gridIdx: number): string {
    const isMarked  = markedIndices.includes(gridIdx);
    const isWonCell = wonLine.includes(gridIdx);
    const isCurrent = currentCard?.boardIdx === gridIdx && phase === "cantada" && currentCard.isHit && !boardTapped;
    const isTourCell = phase === "lines-tour" && tourActive?.includes(gridIdx);

    if (isTourCell) return "2px solid rgba(251,191,36,0.7)";
    if (phase === "lines-tour") return "none"; // clean board during tour
    if (phase === "cantada" && isComplete && isWonCell) return "2px solid rgba(251,191,36,0.8)";
    if (isCurrent)  return "2px solid rgba(0,229,255,0.8)";
    if (isMarked)   return "2px solid rgba(52,211,153,0.6)";
    return "none";
  }

  // ── Webito dialogue text for current state ────────────────────────────────

  function cantadaDialogue(): string | null {
    if (!currentCard) return null;
    if (isComplete) return ACT3_VICTORY[webito.nature];
    if (currentCard.isHit) return ACT3_HIT_REACTIONS[webito.nature][hitIndex] ?? null;
    return null;
  }

  // ── Render ────────────────────────────────────────────────────────────────

  return (
    <div className="flex flex-col items-center gap-3 py-2 px-3 max-w-sm mx-auto w-full">

      {/* ── INTRO ─────────────────────────────────────────────────────────── */}
      {phase === "intro" && (
        <>
          <p className="text-[10px] font-black uppercase tracking-widest text-center" style={{ color: "#64748b" }}>
            Tu Tabla del Destino — generada de tu ADN
          </p>
          
          {/* Show a closed deck in the center */}
          <div className="relative w-[70px] h-[100px] my-6 mx-auto">
            <div className="absolute inset-0 rounded-md border border-amber-500/30 bg-indigo-950/80 shadow-md translate-x-1 translate-y-1 rotate-1" />
            <div className="absolute inset-0 rounded-md border border-amber-500 bg-gradient-to-br from-indigo-950 via-slate-900 to-violet-950 flex flex-col items-center justify-center shadow-lg select-none rounded-md">
              <div className="text-[14px] font-black text-amber-500 tracking-wider">AXO</div>
              <div className="text-[8px] text-amber-400">★</div>
            </div>
          </div>
          
          <WebitoDialogue text={ACT3_BOARD_INTRO[webito.nature]} speaker="webito" onDismiss={handleIntroDismiss} />
        </>
      )}

      {/* ── SHUFFLING ────────────────────────────────────────────────────── */}
      {phase === "shuffling" && (
        <div className="flex flex-col items-center justify-center py-6 px-4 w-full min-h-[200px] gap-4">
          <p className="text-sm font-bold text-amber-400 animate-pulse tracking-wide uppercase">
            ⚡ Barajando el mazo de 54 cartas...
          </p>
          <div className="relative w-[80px] h-[114px] my-4" style={{ perspective: "1000px" }}>
            {/* Stacked background cards to give 3D deck depth */}
            <div
              className="absolute inset-0 rounded-md border border-amber-500/20 bg-indigo-950 shadow-md"
              style={{
                transform: "translate3d(-4px, 4px, -10px) rotate(-3deg)",
                animation: "shuffle-left 0.4s ease-in-out infinite",
              }}
            />
            <div
              className="absolute inset-0 rounded-md border border-amber-500/35 bg-indigo-900 shadow-md"
              style={{
                transform: "translate3d(4px, 2px, -5px) rotate(3deg)",
                animation: "shuffle-right 0.4s ease-in-out infinite 0.1s",
              }}
            />
            {/* Top card of the deck */}
            <div
              className="absolute inset-0 rounded-md border border-amber-500 bg-gradient-to-br from-indigo-950 via-slate-900 to-violet-950 flex flex-col items-center justify-center shadow-xl select-none"
              style={{
                transform: "translate3d(0, 0, 0)",
                animation: "shuffle-left 0.4s ease-in-out infinite 0.2s",
              }}
            >
              <div className="text-[16px] font-black text-amber-500 tracking-widest drop-shadow-[0_0_6px_rgba(245,158,11,0.5)]">
                AXO
              </div>
              <div className="text-[10px] text-amber-400 animate-bounce mt-1">★</div>
            </div>
          </div>
          <p className="text-[10px] text-slate-500 italic max-w-[200px] text-center">
            Generando combinación única de 16 cartas según tu ADN...
          </p>
        </div>
      )}

      {/* ── DEALING ───────────────────────────────────────────────────────── */}
      {phase === "dealing" && (
        <>
          <p className="text-[10px] font-black uppercase tracking-widest text-center" style={{ color: "#64748b" }}>
            📜 Creando tu Acta de Nacimiento...
          </p>
          <Board
            board={board}
            markedIndices={[]}
            cellStyle={() => ({})}
            cellBorder={() => "none"}
            onCellTap={() => {}}
            isDealing={true}
          />
          {dealingComplete && (
            <WebitoDialogue
              text={ACT3_BOARD_REVEALED[webito.nature]}
              speaker="webito"
              onDismiss={() => setPhase("cantada")}
            />
          )}
        </>
      )}

      {/* ── CANTADA ───────────────────────────────────────────────────────── */}
      {phase === "cantada" && (
        <>
          <p className="text-[10px] font-black uppercase tracking-widest text-center mb-1" style={{ color: "#64748b" }}>
            📋 Ronda de Prueba (Acta de Nacimiento)
          </p>
          {/* Big card display */}
          <div
            className="flex flex-col items-center gap-2 py-2 px-4 rounded-2xl w-full"
            style={{
              background: "rgba(6,6,20,0.8)",
              border: `1px solid ${currentCard?.isHit ? "rgba(52,211,153,0.35)" : "rgba(255,255,255,0.08)"}`,
            }}
          >
            <p className="text-[10px] font-black uppercase tracking-widest" style={{ color: "#475569" }}>
              📣 El Gritón canta:
            </p>
            <div className="flex items-center gap-3">
              {CARD_IMAGE[currentCard.num] && (
                <img
                  src={CARD_IMAGE[currentCard.num]}
                  alt={cardName(currentCard.num)}
                  className="rounded-lg shadow-lg"
                  style={{
                    width: BIG_CARD,
                    height: BIG_CARD_H,
                    objectFit: "cover",
                    border: currentCard.isHit
                      ? "2px solid rgba(52,211,153,0.7)"
                      : "2px solid rgba(255,255,255,0.1)",
                    boxShadow: currentCard.isHit
                      ? "0 0 20px rgba(52,211,153,0.5)"
                      : "0 4px 16px rgba(0,0,0,0.5)",
                  }}
                />
              )}
              <div className="flex flex-col gap-1">
                <p
                  className="text-base font-black leading-tight"
                  style={{ color: currentCard.isHit ? "#34d399" : "#94a3b8" }}
                >
                  {cardName(currentCard.num)}
                </p>
                <p
                  className="text-[10px] font-bold uppercase tracking-wider"
                  style={{ color: currentCard.isHit ? "#34d399" : "#334155" }}
                >
                  {currentCard.isHit ? "¡Es tuya!" : "No es tuya"}
                </p>
                {currentCard.isHit && !boardTapped && (
                  <p className="text-[10px] animate-pulse" style={{ color: "#00e5ff" }}>
                    Toca la carta en tu tabla ↓
                  </p>
                )}
                {currentCard.isHit && boardTapped && (
                  <p className="text-[10px]" style={{ color: "#34d399" }}>✓ Marcada</p>
                )}
              </div>
            </div>
            {/* Progress dots */}
            <div className="flex gap-1.5">
              {seq.map((c, i) => (
                <div
                  key={i}
                  className="rounded-full transition-all duration-200"
                  style={{
                    width: i <= cantadaStep ? 7 : 5,
                    height: i <= cantadaStep ? 7 : 5,
                    background: i < cantadaStep
                      ? c.isHit ? "#34d399" : "#334155"
                      : i === cantadaStep
                        ? c.isHit ? "#00e5ff" : "#94a3b8"
                        : "rgba(100,116,139,0.2)",
                    boxShadow: i === cantadaStep && c.isHit ? "0 0 6px #00e5ff" : "none",
                  }}
                />
              ))}
            </div>
          </div>

          {/* Board */}
          <div className="relative">
            {showParticles && <Particles />}
            <Board
              board={board}
              markedIndices={markedIndices}
              cellStyle={cellStyle}
              cellBorder={cellBorder}
              onCellTap={handleBoardCellTap}
              wonLine={isComplete ? wonLine : undefined}
              pulseIdx={
                currentCard?.isHit && !boardTapped && !isComplete
                  ? (currentCard.boardIdx ?? undefined)
                  : undefined
              }
            />
          </div>

          {/* Webito dialogue on hit or victory */}
          {cantadaDialogue() && (
            <div className="w-full">
              <WebitoDialogue
                key={`${cantadaStep}-${isComplete}`}
                text={cantadaDialogue()!}
                speaker="webito"
                onDismiss={isComplete
                  ? () => { setPhase("lines-tour"); setTourLineIdx(0); }
                  : undefined}
              />
            </div>
          )}

        </>
      )}

      {/* ── LINES TOUR ────────────────────────────────────────────────────── */}
      {phase === "lines-tour" && (
        <>
          {/* Line label — always shown, loops with animation */}
          <div className="text-center space-y-0.5">
            <p className="text-sm font-black uppercase tracking-widest" style={{ color: "#fbbf24" }}>
              {tourLabel}
            </p>
            <p className="text-[10px]" style={{ color: "#475569" }}>
              10 líneas posibles — filas, columnas y diagonales
            </p>
          </div>

          <Board
            board={board}
            markedIndices={[]}
            cellStyle={cellStyle}
            cellBorder={cellBorder}
            onCellTap={() => {}}
          />

          {/* Webito explains lines — tap to advance to full-board */}
          <div className="w-full">
            <WebitoDialogue
              text={ACT3_LINES_EXPLAIN[webito.nature]}
              speaker="webito"
              onDismiss={() => { setFullBoardCount(0); setPhase("full-board"); }}
            />
          </div>
        </>
      )}

      {/* ── FULL BOARD ────────────────────────────────────────────────────── */}
      {phase === "full-board" && (
        <>
          {/* Cells fill one by one via fullBoardCount */}
          <Board
            board={board}
            markedIndices={Array.from({ length: fullBoardCount }, (_, i) => i)}
            cellStyle={(idx) => {
              if (idx < fullBoardCount)
                return { background: "rgba(52,211,153,0.4)", boxShadow: "0 0 12px rgba(52,211,153,0.7)" };
              return {};
            }}
            cellBorder={(idx) =>
              idx < fullBoardCount ? "2px solid rgba(52,211,153,0.6)" : "none"
            }
            onCellTap={() => {}}
            allGlow={fullBoardCount >= 16}
          />
          {/* Show Webito dialogue after fill completes — tap to advance */}
          {fullBoardCount >= 16 && (
            <div className="w-full">
              <WebitoDialogue
                text={ACT3_FULL_BOARD[webito.nature]}
                speaker="webito"
                onDismiss={() => setPhase("outro")}
              />
            </div>
          )}
        </>
      )}

      {/* ── OUTRO ─────────────────────────────────────────────────────────── */}
      {phase === "outro" && (
        <>
          <Board
            board={board}
            markedIndices={markedIndices}
            cellStyle={() => ({})}
            cellBorder={() => "none"}
            onCellTap={() => {}}
          />
          <WebitoDialogue
            text={ACT3_OUTRO[webito.nature]}
            speaker="webito"
            onDismiss={onComplete}
          />
        </>
      )}
    </div>
  );
}

// ── Board sub-component ───────────────────────────────────────────────────────

interface BoardProps {
  board: number[];
  markedIndices: number[];
  cellStyle: (idx: number) => React.CSSProperties;
  cellBorder: (idx: number) => string;
  onCellTap: (idx: number) => void;
  wonLine?: number[];
  allGlow?: boolean;
  pulseIdx?: number;
  isDealing?: boolean;
}

function Board({ board, markedIndices, cellStyle, cellBorder, onCellTap, wonLine, allGlow, pulseIdx, isDealing }: BoardProps) {
  return (
    <div
      className="grid gap-0.5 p-1.5 rounded-2xl"
      style={{
        gridTemplateColumns: `repeat(4, ${CARD_SIZE}px)`,
        background: "rgba(6,6,20,0.92)",
        border: allGlow
          ? "1px solid rgba(251,191,36,0.3)"
          : "1px solid rgba(0,229,255,0.1)",
        boxShadow: allGlow
          ? "0 0 36px rgba(251,191,36,0.25)"
          : "0 0 12px rgba(0,229,255,0.05)",
        transition: "box-shadow 0.4s",
      }}
    >
      <style>{`
        @keyframes hit-pulse {
          0%, 100% { transform: scale(1) rotate(0deg); }
          25%       { transform: scale(1.1) rotate(-1.5deg); }
          75%       { transform: scale(1.07) rotate(1.5deg); }
        }
        @keyframes shuffle-left {
          0%, 100% { transform: translate(0, 0) rotate(0deg); }
          50% { transform: translate(-28px, -4px) rotate(-10deg); }
        }
        @keyframes shuffle-right {
          0%, 100% { transform: translate(0, 0) rotate(0deg); }
          50% { transform: translate(28px, 4px) rotate(10deg); }
        }
        @keyframes fly-and-flip {
          0% {
            transform: translate(var(--dx), var(--dy)) scale(1.35) rotateY(180deg);
            opacity: 0;
          }
          15% {
            opacity: 1;
          }
          70% {
            transform: translate(0, 0) scale(1.05) rotateY(180deg);
          }
          100% {
            transform: translate(0, 0) scale(1) rotateY(0deg);
            opacity: 1;
          }
        }
      `}</style>
      {board.map((num, idx) => {
        if (isDealing) {
          const r = Math.floor(idx / 4);
          const c = idx % 4;
          const dx = CARD_SIZE * (1.5 - c);
          const dy = CARD_H * (1.5 - r);

          return (
            <div
              key={idx}
              className="relative rounded-md"
              style={{
                width: CARD_SIZE,
                height: CARD_H,
                perspective: "1000px",
              }}
            >
              <div
                className="w-full h-full relative"
                style={{
                  transformStyle: "preserve-3d",
                  animation: "fly-and-flip 0.8s cubic-bezier(0.25, 1, 0.5, 1) forwards",
                  animationDelay: `${idx * 110}ms`,
                  transform: "rotateY(180deg)",
                  opacity: 0,
                  "--dx": `${dx}px`,
                  "--dy": `${dy}px`,
                } as React.CSSProperties}
              >
                {/* Front Side */}
                <div
                  className="absolute inset-0 w-full h-full rounded-md overflow-hidden bg-slate-900 border border-slate-700/50"
                  style={{ backfaceVisibility: "hidden" }}
                >
                  {CARD_IMAGE[num] ? (
                    <img src={CARD_IMAGE[num]} alt="" className="w-full h-full object-cover" draggable={false} />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center text-xs text-slate-500">
                      {num}
                    </div>
                  )}
                </div>

                {/* Back Side */}
                <div
                  className="absolute inset-0 w-full h-full rounded-md overflow-hidden"
                  style={{
                    backfaceVisibility: "hidden",
                    transform: "rotateY(180deg)",
                  }}
                >
                  <div className="w-full h-full border border-amber-500 bg-gradient-to-br from-indigo-950 via-slate-900 to-violet-950 flex flex-col items-center justify-center shadow-inner">
                    <span className="text-[10px] font-black text-amber-500 tracking-wider">AXO</span>
                    <span className="text-[8px] text-amber-400">★</span>
                  </div>
                </div>
              </div>
            </div>
          );
        }

        const ov = cellStyle(idx);
        const border = cellBorder(idx);
        const isMarked = markedIndices.includes(idx);
        const isWon = wonLine?.includes(idx);
        const isPulsing = pulseIdx === idx;

        return (
          <div
            key={idx}
            className="relative rounded-md overflow-hidden select-none"
            style={{
              width: CARD_SIZE,
              height: CARD_H,
              cursor: "pointer",
              animation: isPulsing ? "hit-pulse 0.65s ease-in-out infinite" : undefined,
              zIndex: isPulsing ? 10 : undefined,
            }}
            onClick={() => onCellTap(idx)}
          >
            {CARD_IMAGE[num] ? (
              <img
                src={CARD_IMAGE[num]}
                alt=""
                className="absolute inset-0 w-full h-full object-cover"
                draggable={false}
              />
            ) : (
              <div className="absolute inset-0 bg-slate-900 flex items-center justify-center text-xs" style={{ color: "#475569" }}>
                {num}
              </div>
            )}

            {/* Overlay */}
            {(ov.background || ov.boxShadow) && (
              <div
                className="absolute inset-0 rounded-md pointer-events-none transition-all duration-300"
                style={{ ...ov, border }}
              />
            )}
            {border && border !== "none" && !(ov.background || ov.boxShadow) && (
              <div className="absolute inset-0 rounded-md pointer-events-none" style={{ border }} />
            )}

            {/* ✓ checkmark */}
            {isMarked && (
              <div className="absolute bottom-0.5 right-0.5 pointer-events-none z-10">
                <span
                  className="text-[8px] font-black leading-none px-0.5 rounded-sm"
                  style={{ color: "#34d399", background: "rgba(0,0,0,0.7)" }}
                >
                  ✓
                </span>
              </div>
            )}

            {/* Win star */}
            {isWon && !isMarked && (
              <div className="absolute top-0.5 right-0.5 pointer-events-none z-10 text-[8px]">⭐</div>
            )}
          </div>
        );
      })}
    </div>
  );
}
