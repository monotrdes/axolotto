"use client";

import LoteriaCard from './LoteriaCard';
import { rarityFrameClass } from '@/lib/boardRarity';
import type { BoardRarity } from '@/lib/boardRarity';

interface BoardCardGridProps {
  boardNums: number[];
  cardSize?: number;
  matchedIndices?: number[];
  missedIndices?: number[];
  winLine?: number[];
  priorityLine?: number[];
  dimmedIndices?: number[];
  isWinner?: boolean;
  isCpuLoser?: boolean;
  depth?: 'front' | 'mid' | 'back';
  label?: string;
  variant?: 'player' | 'cpu';
  frameRarity?: BoardRarity;
  isShiny?: boolean;
  /** Enable interactive tapping (manual mode) */
  interactive?: boolean;
  /** Cell index to highlight (e.g., current card match) */
  highlightedCell?: number | null;
  /** Cell indices affected by salinity fog (blur + salt) */
  salinityFogCells?: number[];
  /** Cells belonging to active win patterns (subtle guide, only shown on unmatched cells) */
  patternHintCells?: number[];
  /** Callback when a cell is tapped (only if interactive=true) */
  onCellTap?: (idx: number) => void;
}

const DEPTH_STYLE: Record<string, React.CSSProperties> = {
  front: { transform: 'scale(1)',    opacity: 1,    filter: 'none' },
  mid:   { transform: 'scale(0.95)', opacity: 0.85, filter: 'none' },
  back:  { transform: 'scale(0.88)', opacity: 0.6,  filter: 'blur(0.5px)' },
};

export default function BoardCardGrid({
  boardNums,
  cardSize = 44,
  matchedIndices  = [],
  missedIndices   = [],
  winLine,
  priorityLine    = [],
  dimmedIndices   = [],
  isWinner        = false,
  isCpuLoser      = false,
  depth           = 'front',
  label,
  variant         = 'player',
  frameRarity,
  isShiny         = false,
  interactive      = false,
  highlightedCell  = null,
  salinityFogCells = [],
  patternHintCells = [],
  onCellTap,
}: BoardCardGridProps) {
  const isCpu       = variant === 'cpu';
  const cardH       = Math.round(cardSize * 1.5);
  const winClass    = isWinner   ? 'animate-player-win-bloom' : '';
  const cpuWinClass = isCpuLoser ? 'animate-cpu-win-surge'    : '';

  const hasGameState = isWinner || isCpuLoser;
  const rarityClass  = !hasGameState && frameRarity ? rarityFrameClass(frameRarity) : '';

  const gridBg = isWinner
    ? 'bg-emerald-950/40 border-emerald-500/40 shadow-[0_0_20px_rgba(52,211,153,0.3)]'
    : isCpu && depth === 'back'
      ? 'bg-slate-950/60 border-rose-500/20 shadow-[0_0_10px_rgba(244,63,94,0.1)]'
      : 'bg-slate-950/60 border-slate-800';

  return (
    <div
      className={`relative flex flex-col items-center gap-1 transition-all duration-500 ${winClass} ${cpuWinClass}`}
      style={DEPTH_STYLE[depth]}
    >
      {label && (
        <span className="text-[9px] font-black uppercase tracking-widest text-slate-400 bg-slate-950/80 px-2 py-0.5 rounded-full border border-slate-800">
          {label}
        </span>
      )}

      <div className={`relative grid grid-cols-4 gap-0.5 p-1 rounded-xl border ${gridBg} ${rarityClass}`}>
        {!hasGameState && isShiny && <div className="board-shiny-overlay rounded-xl" />}
        {Array(16).fill(null).map((_, idx) => {
          const num        = boardNums[idx] ?? 0;
          const matched    = matchedIndices.includes(idx);
          const isMissed   = missedIndices.includes(idx);
          const isDimmed   = dimmedIndices.includes(idx);
          const isWinCell  = winLine?.includes(idx) ?? false;
          const isPriority = priorityLine.includes(idx);
          const isHighlighted  = highlightedCell === idx;
          const isFoggy        = salinityFogCells.includes(idx);
          const isPatternHint  = !matched && !isMissed && patternHintCells.includes(idx);

          // Wrapper opacity for dimmed/missed/fog
          const wrapperOpacity = isDimmed ? 'opacity-60' : isFoggy ? 'opacity-50' : '';
          const wrapperBlur = isFoggy ? 'blur-[2px]' : '';
          const wrapperInteractive = interactive ? 'cursor-pointer hover:scale-105 active:scale-95 transition-transform' : '';

          // State overlay class (rendered on top of card image)
          let overlayClass  = '';
          let overlayShadow = '';
          let overlayRing   = '';
          let overlayAnim   = '';
          let overlayDelay: React.CSSProperties | undefined;

          if (isWinCell) {
            overlayClass = 'bg-amber-400/40 border border-amber-400/60';
            overlayShadow = 'shadow-[0_0_10px_rgba(251,191,36,0.6)]';
            overlayAnim  = 'animate-board-fill-cell';
            overlayDelay = { animationDelay: `${idx * 40}ms` };
          } else if (isHighlighted && interactive) {
            // Gold pulsing border for the cell matching current card (manual mode)
            overlayClass = 'bg-amber-500/20 border-2 border-amber-400/70';
            overlayShadow = 'shadow-[0_0_14px_rgba(251,191,36,0.7)]';
            overlayAnim  = 'animate-pulse';
          } else if (isFoggy) {
            // Salinity fog effect — blur + salt overlay
            overlayClass = 'bg-slate-100/20 border border-white/10';
          } else if (matched && isPriority) {
            overlayClass = isCpu
              ? 'bg-rose-500/40 border border-rose-300/60'
              : 'bg-emerald-500/45 border border-emerald-300/70';
            overlayShadow = isCpu
              ? 'shadow-[0_0_10px_rgba(244,63,94,0.6)]'
              : 'shadow-[0_0_12px_rgba(52,211,153,0.8)]';
            overlayRing  = isCpu
              ? 'ring-1 ring-rose-300/20'
              : 'ring-1 ring-emerald-300/30';
            overlayAnim  = 'animate-board-fill-cell';
            overlayDelay = { animationDelay: `${idx * 30}ms` };
          } else if (matched) {
            overlayClass = isCpu
              ? 'bg-rose-500/30 border border-rose-500/40'
              : 'bg-emerald-500/30 border border-emerald-500/50';
            overlayShadow = isCpu
              ? 'shadow-[0_0_6px_rgba(244,63,94,0.4)]'
              : 'shadow-[0_0_6px_rgba(52,211,153,0.4)]';
            overlayAnim  = 'animate-board-fill-cell';
            overlayDelay = { animationDelay: `${idx * 30}ms` };
          } else if (isPriority) {
            overlayClass = isCpu
              ? 'bg-rose-950/40 border border-rose-500/40'
              : 'bg-emerald-950/40 border border-emerald-500/50';
            overlayShadow = isCpu
              ? 'shadow-[0_0_5px_rgba(244,63,94,0.2)]'
              : 'shadow-[0_0_5px_rgba(52,211,153,0.25)]';
          } else if (isMissed) {
            overlayClass = 'bg-orange-900/40 border border-orange-600/40';
          } else if (isDimmed) {
            overlayClass = 'bg-slate-900/50';
          } else if (isPatternHint) {
            overlayClass  = 'bg-violet-500/10 border border-violet-400/30';
            overlayShadow = 'shadow-[0_0_6px_rgba(167,139,250,0.2)]';
          }

          const hasOverlay = overlayClass !== '';
          const fakeCard   = { item_metadata: { numero_loteria: num }, dynamic_rarity: 'Común', name: '' };

          return (
            <div
              key={idx}
              className={`relative transition-all ${wrapperOpacity} ${wrapperBlur} ${wrapperInteractive}`}
              style={{ width: cardSize, height: cardH }}
              onClick={() => interactive && onCellTap?.(idx)}
              onPointerDown={(e) => {
                if (!interactive) return;
                // Prevent default to avoid double-fire on mobile
                e.preventDefault();
                onCellTap?.(idx);
              }}
            >
              {/* Card or empty slot */}
              {num > 0 ? (
                <LoteriaCard
                  card={fakeCard}
                  size={cardSize}
                  showQty={false}
                />
              ) : (
                <div
                  className="absolute inset-0 rounded-md bg-slate-900/30 border border-slate-800/40"
                />
              )}

              {/* State overlay */}
              {hasOverlay && (
                <div
                  className={`absolute inset-0 rounded-md pointer-events-none z-10 ${overlayClass} ${overlayShadow} ${overlayRing} ${overlayAnim}`}
                  style={overlayDelay}
                />
              )}

              {/* Missed ✗ */}
              {isMissed && (
                <span
                  className="absolute inset-0 flex items-center justify-center font-black text-orange-400 pointer-events-none z-20"
                  style={{ fontSize: Math.max(8, cardSize * 0.45) }}
                >
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
