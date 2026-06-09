"use client";

import React from "react";
import BoardCardGrid from "./BoardCardGrid";

// ── Types ─────────────────────────────────────────────────────────────────────

export interface OpponentInfo {
  axolotito_id?: number;
  axo_name?: string;
  /** 16 lotería numbers for the mini board */
  boardNums: number[];
  /** Marked cell indices */
  matchedIndices: number[];
  /** Threat level 0-4 (cells in best line) */
  threat?: number;
  /** Is a bot (CPU/Auto) or human (Manual) */
  kind?: "bot" | "human";
  /** Highlight if this opponent just won */
  isWinner?: boolean;
}

interface OpponentStripProps {
  opponents: OpponentInfo[];
  /** Max opponents to show (scroll if more) */
  maxVisible?: number;
  /** Card size for mini boards (default 13) */
  cardSize?: number;
}

// ── Component ─────────────────────────────────────────────────────────────────

export default function OpponentStrip({
  opponents,
  maxVisible = 6,
  cardSize = 13,
}: OpponentStripProps) {
  if (opponents.length === 0) {
    return (
      <div className="flex items-center justify-center py-2">
        <p className="text-[9px] text-slate-600 font-black uppercase tracking-widest">
          Esperando oponentes...
        </p>
      </div>
    );
  }

  const display = opponents.slice(0, maxVisible);
  const overflow = opponents.length - maxVisible;

  return (
    <div className="overflow-x-auto flex items-end gap-2 px-1 py-2
      [&::-webkit-scrollbar]:hidden [-ms-overflow-style:none] [scrollbar-width:none]">
      {display.map((opp, i) => {
        const threatPct = Math.round(((opp.threat ?? 0) / 4) * 100);

        return (
          <div key={opp.axolotito_id ?? i} className="flex flex-col items-center gap-1 shrink-0">
            {/* Mini board */}
            <div className={opp.isWinner ? "animate-player-win-bloom" : ""}>
              <BoardCardGrid
                boardNums={opp.boardNums}
                cardSize={cardSize}
                matchedIndices={opp.matchedIndices}
                variant="cpu"
                depth="back"
                label={opp.isWinner ? "🏆" : undefined}
                isCpuLoser={opp.isWinner}
              />
            </div>

            {/* Name + threat bar */}
            <div className="flex flex-col items-center gap-0.5">
              <span className="text-[8px] font-black text-slate-400 tracking-wider truncate max-w-[60px]">
                {opp.axo_name ?? (opp.kind === "bot" ? "Bot" : "Jugador")}
              </span>
              {/* Threat bar */}
              <div className="w-10 h-1 bg-slate-800 rounded-full overflow-hidden">
                <div
                  className="h-full rounded-full transition-all duration-500"
                  style={{
                    width: `${threatPct}%`,
                    backgroundColor:
                      threatPct >= 75
                        ? "rgb(239,68,68)"
                        : threatPct >= 50
                          ? "rgb(251,191,36)"
                          : "rgb(52,211,153)",
                  }}
                />
              </div>
              {/* Badge */}
              {opp.kind === "human" ? (
                <span className="text-[6px] font-black text-pink-400 bg-pink-950/60 px-1 rounded-full leading-none">
                  PVP
                </span>
              ) : (
                <span className="text-[6px] font-black text-slate-500 bg-slate-800 px-1 rounded-full leading-none">
                  CPU
                </span>
              )}
            </div>
          </div>
        );
      })}

      {/* Overflow indicator */}
      {overflow > 0 && (
        <div className="flex items-center justify-center shrink-0 w-8 h-8 rounded-full bg-slate-800/60 border border-slate-700">
          <span className="text-[9px] font-black text-slate-400">+{overflow}</span>
        </div>
      )}
    </div>
  );
}
