"use client";

import React, { useEffect, useRef, useState } from 'react';
import { LOTERIA_EMOJI } from './LoteriaCard';
import gsap from 'gsap';
import { cartasFaltantes } from '@/lib/loteria/winPatterns';

// ── Lotería Patterns Setup for Match Point ─────────────────────────────────────
const LINES = [
  [0, 1, 2, 3], [4, 5, 6, 7], [8, 9, 10, 11], [12, 13, 14, 15],
  [0, 4, 8, 12], [1, 5, 9, 13], [2, 6, 10, 14], [3, 7, 11, 15],
  [0, 5, 10, 15], [3, 6, 9, 12],
];
const CUADRITOS = [
  [0, 1, 4, 5], [1, 2, 5, 6], [2, 3, 6, 7],
  [4, 5, 8, 9], [5, 6, 9, 10], [6, 7, 10, 11],
  [8, 9, 12, 13], [9, 10, 13, 14], [10, 11, 14, 15],
];
const POCITO = [[5, 6, 9, 10]];
const ESQUINAS = [[0, 3, 12, 15]];
const CRUZ_DIAGONAL = [[0, 3, 5, 6, 9, 10, 12, 15]];
const L_SHAPES = [
  [0, 1, 2, 3, 4, 8, 12],
  [0, 1, 2, 3, 7, 11, 15],
  [0, 4, 8, 12, 13, 14, 15],
  [3, 7, 11, 12, 13, 14, 15],
];
const Z_SHAPES = [
  [0, 1, 2, 3, 5, 10, 12, 13, 14, 15],
  [0, 1, 2, 3, 6, 9, 12, 13, 14, 15],
];
const CRUZ = (() => {
  const rows = LINES.slice(0, 4);
  const cols = LINES.slice(4, 8);
  const out: number[][] = [];
  for (const r of rows) for (const c of cols) out.push([...new Set([...r, ...c])]);
  return out;
})();
const FULL_BOARD = [Array.from({ length: 16 }, (_, i) => i)];

const PATTERNS: Record<string, number[][]> = {
  line: LINES,
  cuadrito: CUADRITOS,
  pocito: POCITO,
  esquinas: ESQUINAS,
  cruz: CRUZ,
  cruz_diagonal: CRUZ_DIAGONAL,
  l_shape: L_SHAPES,
  z_shape: Z_SHAPES,
  full_board: FULL_BOARD,
};

function getMatchPointCells(matched: number[], winPatterns: string[] = ["line", "cuadrito"]): number[] {
  const markedSet = new Set(matched);
  const matchPointCells = new Set<number>();
  
  for (const name of winPatterns) {
    const sets = PATTERNS[name];
    if (!sets) continue;
    for (const cells of sets) {
      const missing = cells.filter(c => !markedSet.has(c));
      if (missing.length === 1 || missing.length === 2) {
        missing.forEach(c => matchPointCells.add(c));
      }
    }
  }
  return Array.from(matchPointCells);
}

// ── Sub-components for Visual FX ──────────────────────────────────────────────

function Frijolito({ matched }: { matched: boolean }) {
  const beanRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (matched && beanRef.current) {
      gsap.fromTo(
        beanRef.current,
        {
          y: -40,
          opacity: 0,
          scale: 1.4,
          rotation: -12 + Math.random() * 24,
        },
        {
          y: 0,
          opacity: 1,
          scale: 1,
          rotation: 0,
          duration: 0.6,
          ease: 'bounce.out',
        }
      );
    }
  }, [matched]);

  if (!matched) return null;

  return (
    <div
      ref={beanRef}
      className="absolute inset-0 z-10 flex items-center justify-center pointer-events-none p-0.5 sm:p-1"
    >
      <svg
        viewBox="0 0 24 24"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        className="w-full h-full drop-shadow-[0_2px_3px_rgba(0,0,0,0.65)]"
      >
        <defs>
          <radialGradient id="beanGrad" cx="35%" cy="35%" r="65%">
            <stop offset="0%" stopColor="#d97706" />
            <stop offset="70%" stopColor="#78350f" />
            <stop offset="100%" stopColor="#451a03" />
          </radialGradient>
        </defs>
        {/* Cutout border backing */}
        <path
          d="M16 6C14.5 4.5 11 4 9 5C6.5 6.2 5 9 5 12C5 15.5 7.5 18.5 11 19C13.5 19.3 16 18 18 16C19.5 14.5 19.8 11.5 19 9.5C18.2 7.5 17.5 7.5 16 6Z"
          fill="#ffffff"
          stroke="#cbd5e1"
          strokeWidth="0.5"
        />
        {/* The bean */}
        <path
          d="M15.5 7C14.2 5.8 11.2 5.3 9.5 6.2C7.3 7.2 6 9.7 6 12.2C6 15.2 8.2 17.8 11.2 18.2C13.4 18.5 15.6 17.3 17.3 15.5C18.6 14.2 18.8 11.6 18.1 9.9C17.4 8.2 16.8 8.2 15.5 7Z"
          fill="url(#beanGrad)"
        />
        {/* Highlight for 3D depth */}
        <ellipse
          cx="10"
          cy="9"
          rx="1.5"
          ry="0.8"
          transform="rotate(-30 10 9)"
          fill="#fef3c7"
          opacity="0.8"
        />
      </svg>
    </div>
  );
}

function PapelPicadoGoldBorder() {
  return (
    <div className="absolute -inset-1 z-20 pointer-events-none animate-pulse">
      <svg viewBox="0 0 100 100" fill="none" preserveAspectRatio="none" className="w-full h-full filter drop-shadow-[0_0_3px_rgba(251,191,36,0.85)]">
        <path
          d="M 4,4 L 96,4 L 96,96 L 4,96 Z"
          stroke="#fbbf24"
          strokeWidth="2.5"
          strokeLinecap="round"
          strokeDasharray="4 3"
        />
        <rect x="2" y="2" width="96" height="96" rx="4" stroke="#f59e0b" strokeWidth="0.75" opacity="0.5" />
        <polygon points="10,4 15,8 20,4" fill="#fbbf24" />
        <polygon points="30,4 35,8 40,4" fill="#fbbf24" />
        <polygon points="50,4 55,8 60,4" fill="#fbbf24" />
        <polygon points="70,4 75,8 80,4" fill="#fbbf24" />
        <polygon points="90,4 96,8 96,4" fill="#fbbf24" />
        
        <polygon points="96,20 92,25 96,30" fill="#fbbf24" />
        <polygon points="96,40 92,45 96,50" fill="#fbbf24" />
        <polygon points="96,60 92,65 96,70" fill="#fbbf24" />
        <polygon points="96,80 92,85 96,90" fill="#fbbf24" />

        <polygon points="90,96 85,92 80,96" fill="#fbbf24" />
        <polygon points="70,96 65,92 60,96" fill="#fbbf24" />
        <polygon points="50,96 45,92 40,96" fill="#fbbf24" />
        <polygon points="30,96 25,92 20,96" fill="#fbbf24" />
        <polygon points="10,96 4,92 4,96" fill="#fbbf24" />

        <polygon points="4,80 8,75 4,70" fill="#fbbf24" />
        <polygon points="4,60 8,55 4,50" fill="#fbbf24" />
        <polygon points="4,40 8,35 4,30" fill="#fbbf24" />
        <polygon points="4,20 8,15 4,10" fill="#fbbf24" />
      </svg>
    </div>
  );
}

function ConfettiParticles() {
  const [particles, setParticles] = useState<{ id: number; x: number; y: number; r: number; color: string; scale: number }[]>([]);

  useEffect(() => {
    const colors = ['#fbbf24', '#f59e0b', '#ec4899', '#3b82f6', '#10b981'];
    const list = Array.from({ length: 5 }).map((_, i) => ({
      id: i,
      x: Math.random() * 70 + 15,
      y: Math.random() * 70 + 15,
      r: Math.random() * 360,
      color: colors[Math.floor(Math.random() * colors.length)],
      scale: Math.random() * 0.35 + 0.15,
    }));
    setParticles(list);
  }, []);

  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none z-20">
      {particles.map((p) => (
        <div
          key={p.id}
          className="absolute w-1 h-1 opacity-75"
          style={{
            left: `${p.x}%`,
            top: `${p.y}%`,
            backgroundColor: p.color,
            transform: `rotate(${p.r}deg) scale(${p.scale})`,
            borderRadius: p.id % 2 === 0 ? '50%' : '20%',
            animation: `float-confetti-${p.id} ${2 + Math.random() * 2}s ease-in-out infinite alternate`,
          }}
        />
      ))}
    </div>
  );
}

function BoardGoldenParticles() {
  const [particles, setParticles] = useState<{ id: number; left: number; top: number; size: number; delay: number; duration: number }[]>([]);

  useEffect(() => {
    const list = Array.from({ length: 8 }).map((_, i) => ({
      id: i,
      left: Math.random() * 120 - 10,
      top: Math.random() * 120 - 10,
      size: Math.random() * 2.2 + 1.2,
      delay: Math.random() * 2,
      duration: Math.random() * 3 + 3,
    }));
    setParticles(list);
  }, []);

  return (
    <div className="absolute -inset-6 pointer-events-none overflow-hidden z-0">
      {particles.map((p) => (
        <div
          key={p.id}
          className="absolute bg-amber-300 rounded-full opacity-50 shadow-[0_0_4px_#f59e0b]"
          style={{
            left: `${p.left}%`,
            top: `${p.top}%`,
            width: `${p.size}px`,
            height: `${p.size}px`,
            animation: `float-up-${p.id} ${p.duration}s linear infinite`,
            animationDelay: `${p.delay}s`,
          }}
        />
      ))}
    </div>
  );
}

// ── Main Component ────────────────────────────────────────────────────────────

interface LoteriaBoardProps {
  boardCards: number[];        // Lotería numbers (1–54) at each of the 16 positions
  matchedIndices: number[];    // Which positions (0–15) are already matched
  missedIndices?: number[];    // Positions where the player missed the card (orange ✗)
  dimmedIndices?: number[];    // Positions where the bot missed the card (subtle grey)
  winLine?: number[];          // Indices of the winning line (highlighted in gold)
  priorityLine?: number[];     // Most advanced winning line highlight
  patternHintCells?: number[]; // Cells belonging to active win patterns (subtle guide)
  isWinner?: boolean;
  isCpuLoser?: boolean;        // CPU board that lost — surges then dims
  depth: 'front' | 'mid' | 'back';
  label?: string;
  variant?: 'player' | 'cpu'; // team color: emerald (player) or rose (cpu)
  size?: 'xs' | 'sm' | 'md';  // xs=10px thumbnail, sm=w-5 side panel, md=w-7 default
  winPatterns?: string[];     // Active game patterns for calculating Match Point
}

export default function LoteriaBoard({
  boardCards,
  matchedIndices,
  missedIndices      = [],
  dimmedIndices      = [],
  winLine,
  priorityLine       = [],
  patternHintCells   = [],
  isWinner  = false,
  isCpuLoser = false,
  depth,
  label,
  variant = 'player',
  size    = 'md',
  winPatterns = ["line", "cuadrito"],
}: LoteriaBoardProps) {
  const isCpu = variant === 'cpu';

  // Calculate Match Point (1-2 cards missing from win)
  const isMatchPoint = !isWinner && cartasFaltantes(matchedIndices, winPatterns) <= 2 && cartasFaltantes(matchedIndices, winPatterns) > 0;
  const matchPointCells = isMatchPoint ? getMatchPointCells(matchedIndices, winPatterns) : [];

  const depthStyle: React.CSSProperties = {
    front: { 
      transform: isMatchPoint ? 'scale(1.15)' : 'scale(1)',    
      opacity: 1,    
      filter: 'none',
      transition: 'transform 0.5s cubic-bezier(0.34, 1.56, 0.64, 1)'
    },
    mid:   { transform: 'scale(0.95)', opacity: 0.85, filter: 'none' },
    back:  { transform: 'scale(0.88)', opacity: 0.6,  filter: 'blur(0.5px)' },
  }[depth];

  const winClass    = isWinner   ? 'animate-player-win-bloom' : '';
  const cpuWinClass = isCpuLoser ? 'animate-cpu-win-surge'    : '';

  const cellBase = size === 'xs'
    ? 'w-2.5 h-2.5 text-[5px]'
    : size === 'sm'
      ? 'w-5 h-5 text-[11px]'
      : 'w-7 h-7 sm:w-8 sm:h-8 text-[14px] sm:text-[16px]';

  const gridGap = size === 'xs' ? 'gap-0.5' : 'gap-1';

  // Set grid background style including Moonlight Glow on Match Point
  const gridBgClass = isWinner
    ? 'bg-emerald-950/40 border-emerald-500/40 shadow-[0_0_20px_rgba(52,211,153,0.3)]'
    : isMatchPoint && depth === 'front'
      ? 'bg-amber-950/35 border-amber-400 shadow-[0_0_25px_rgba(253,224,71,0.45),_0_0_12px_rgba(147,197,253,0.25)] z-20'
      : isCpu && depth === 'back'
        ? 'bg-slate-950/60 border-rose-500/20 shadow-[0_0_10px_rgba(244,63,94,0.1)]'
        : 'bg-slate-950/60 border-slate-800';

  return (
    <div
      className={`relative flex flex-col items-center gap-1 transition-all duration-500 ${winClass} ${cpuWinClass}`}
      style={depthStyle}
    >
      {label && (
        <span className="text-[9px] font-black uppercase tracking-widest text-slate-400 bg-slate-950/80 px-2 py-0.5 rounded-full border border-slate-800 z-10">
          {label}
        </span>
      )}
      
      {/* Board Golden Particles for Match Point */}
      {isMatchPoint && depth === 'front' && <BoardGoldenParticles />}

      <div className={`grid grid-cols-4 ${gridGap} p-1 rounded-xl border ${gridBgClass}`}>
        {boardCards.map((num, idx) => {
          const matched      = matchedIndices.includes(idx);
          const isMissed     = missedIndices.includes(idx);
          const isDimmed     = dimmedIndices.includes(idx);
          const isWinCell    = winLine?.includes(idx) ?? false;
          const isPriority   = priorityLine.includes(idx);
          const isPatternHint = !matched && patternHintCells.includes(idx);
          const isMatchPointCell = !matched && !isMissed && matchPointCells.includes(idx);
          const emoji      = LOTERIA_EMOJI[num] ?? '🃏';

          let cellClass = '';
          let cellStyle: React.CSSProperties | undefined;

          if (isWinCell) {
            cellClass = 'bg-amber-400/30 border-amber-400/80 shadow-[0_0_10px_rgba(251,191,36,0.6)] animate-board-fill-cell';
            cellStyle = { animationDelay: `${idx * 40}ms` };
          } else if (isMissed) {
            cellClass = 'bg-orange-900/40 border-orange-600/40';
          } else if (matched && isPriority) {
            cellClass = isCpu
              ? 'bg-rose-500/30 border-rose-300/60 shadow-[0_0_10px_rgba(244,63,94,0.6)] ring-1 ring-rose-300/20 animate-board-fill-cell'
              : 'bg-emerald-500/40 border-emerald-300/70 shadow-[0_0_12px_rgba(52,211,153,0.8)] ring-1 ring-emerald-300/30 animate-board-fill-cell';
            cellStyle = { animationDelay: `${idx * 30}ms` };
          } else if (matched) {
            cellClass = isCpu
              ? 'bg-rose-500/20 border-rose-500/40 shadow-[0_0_6px_rgba(244,63,94,0.4)] animate-board-fill-cell'
              : 'bg-emerald-500/20 border-emerald-500/50 shadow-[0_0_6px_rgba(52,211,153,0.4)] animate-board-fill-cell';
            cellStyle = { animationDelay: `${idx * 30}ms` };
          } else if (isPriority) {
            cellClass = isCpu
              ? 'bg-rose-950/40 border-rose-500/40 shadow-[0_0_5px_rgba(244,63,94,0.2)]'
              : 'bg-emerald-950/40 border-emerald-500/50 shadow-[0_0_5px_rgba(52,211,153,0.25)]';
          } else if (isDimmed) {
            cellClass = 'bg-slate-800/50 border-slate-600/30 opacity-60';
          } else if (isPatternHint) {
            cellClass = 'bg-violet-950/30 border-violet-500/25';
          } else {
            cellClass = 'bg-slate-900/60 border-slate-800';
          }

          return (
            <div
              key={idx}
              className={`relative ${cellBase} rounded-md flex items-center justify-center transition-all border ${cellClass}`}
              style={cellStyle}
              title={num ? String(num) : '—'}
            >
              {num ? (
                <span className={isMissed ? 'opacity-30' : undefined}>{emoji}</span>
              ) : (
                <span className="text-[8px] text-slate-700">—</span>
              )}
              
              {isMissed && (
                <span className="absolute inset-0 flex items-center justify-center text-[12px] font-black text-orange-400 pointer-events-none rounded-md">
                  ✗
                </span>
              )}

              {/* Frijolito Falling Animation */}
              <Frijolito matched={matched} />

              {/* Match Point Cell Highlight */}
              {isMatchPointCell && depth === 'front' && (
                <>
                  <PapelPicadoGoldBorder />
                  <ConfettiParticles />
                </>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
