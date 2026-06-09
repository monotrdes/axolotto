"use client";

import React from 'react';
import { LOTERIA_EMOJI } from './LoteriaCard';

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
}: LoteriaBoardProps) {
  const depthStyle: React.CSSProperties = {
    front: { transform: 'scale(1)',    opacity: 1,    filter: 'none' },
    mid:   { transform: 'scale(0.95)', opacity: 0.85, filter: 'none' },
    back:  { transform: 'scale(0.88)', opacity: 0.6,  filter: 'blur(0.5px)' },
  }[depth];

  const isCpu = variant === 'cpu';

  const winClass    = isWinner   ? 'animate-player-win-bloom' : '';
  const cpuWinClass = isCpuLoser ? 'animate-cpu-win-surge'    : '';

  const cellBase = size === 'xs'
    ? 'w-2.5 h-2.5 text-[5px]'
    : size === 'sm'
      ? 'w-5 h-5 text-[11px]'
      : 'w-7 h-7 sm:w-8 sm:h-8 text-[14px] sm:text-[16px]';

  const gridGap = size === 'xs' ? 'gap-0.5' : 'gap-1';

  return (
    <div
      className={`relative flex flex-col items-center gap-1 transition-all duration-500 ${winClass} ${cpuWinClass}`}
      style={depthStyle}
    >
      {label && (
        <span className="text-[9px] font-black uppercase tracking-widest text-slate-400 bg-slate-950/80 px-2 py-0.5 rounded-full border border-slate-800">
          {label}
        </span>
      )}
      <div className={`grid grid-cols-4 ${gridGap} p-1 rounded-xl border ${
        isWinner
          ? 'bg-emerald-950/40 border-emerald-500/40 shadow-[0_0_20px_rgba(52,211,153,0.3)]'
          : isCpu && depth === 'back'
            ? 'bg-slate-950/60 border-rose-500/20 shadow-[0_0_10px_rgba(244,63,94,0.1)]'
            : 'bg-slate-950/60 border-slate-800'
      }`}>
        {boardCards.map((num, idx) => {
          const matched      = matchedIndices.includes(idx);
          const isMissed     = missedIndices.includes(idx);
          const isDimmed     = dimmedIndices.includes(idx);
          const isWinCell    = winLine?.includes(idx) ?? false;
          const isPriority   = priorityLine.includes(idx);
          const isPatternHint = !matched && patternHintCells.includes(idx);
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
            </div>
          );
        })}
      </div>
    </div>
  );
}
