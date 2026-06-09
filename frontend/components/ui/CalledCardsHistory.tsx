"use client";

import React, { useRef, useEffect, useMemo } from "react";
import { LOTERIA_EMOJI, CARD_IMAGE } from "./LoteriaCard";
import Image from "next/image";

// ── Types ─────────────────────────────────────────────────────────────────────

export interface CardHistoryEntry {
  /** Card name (e.g. "El Corazón") */
  name: string;
  /** Lotería number (1-54) */
  number: number;
  /** Turn index (0-based, order called) */
  turn: number;
  /** Was this card matched by the player? */
  matched: boolean;
  /** Was this card missed by the player? (on board but failed to mark) */
  missed: boolean;
}

export interface CalledCardsHistoryProps {
  /** All cards called during the game, in order */
  entries: CardHistoryEntry[];
  /** Optional additional class names */
  className?: string;
}

// ── Component ─────────────────────────────────────────────────────────────────

export default function CalledCardsHistory({
  entries,
  className = "",
}: CalledCardsHistoryProps) {
  const scrollRef = useRef<HTMLDivElement>(null);
  const lastCardRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to end on mount and when new entries arrive
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTo({
        left: scrollRef.current.scrollWidth,
        behavior: "smooth",
      });
    }
  }, [entries.length]);

  // Stats
  const stats = useMemo(() => {
    const matched = entries.filter((e) => e.matched).length;
    const missed = entries.filter((e) => e.missed).length;
    return { matched, missed, total: entries.length };
  }, [entries]);

  if (entries.length === 0) return null;

  return (
    <div className={`flex flex-col gap-1.5 ${className}`}>
      {/* Header row */}
      <div className="flex items-center justify-between px-1">
        <div className="flex items-center gap-2">
          <span className="text-[9px] font-black uppercase tracking-widest text-slate-500">
            📜 Historial del Gritón
          </span>
          <span className="text-[9px] font-bold text-slate-600">
            {stats.total} cartas
          </span>
        </div>
        {/* Mini legend */}
        <div className="flex items-center gap-2">
          <span className="flex items-center gap-1 text-[7px] font-black uppercase tracking-wider text-emerald-400">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400/80" />
            {stats.matched}
          </span>
          <span className="flex items-center gap-1 text-[7px] font-black uppercase tracking-wider text-orange-400">
            <span className="w-1.5 h-1.5 rounded-full bg-orange-400/80" />
            {stats.missed}
          </span>
          <span className="flex items-center gap-1 text-[7px] font-black uppercase tracking-wider text-slate-600">
            <span className="w-1.5 h-1.5 rounded-full bg-slate-600/60" />
            {stats.total - stats.matched - stats.missed}
          </span>
        </div>
      </div>

      {/* Scrollable cards strip */}
      <div
        ref={scrollRef}
        className="overflow-x-auto scrollbar-hide rounded-xl border border-white/10 bg-slate-950/50 px-2 py-2"
        style={{
          scrollSnapType: "x proximity",
          scrollBehavior: "smooth",
        }}
      >
        <div className="flex gap-1 min-w-max">
          {entries.map((entry, i) => {
            const emoji = LOTERIA_EMOJI[entry.number] || "🃏";
            const imageSrc = CARD_IMAGE[entry.number];

            // Border color based on state
            let borderClass = "border-slate-700/30";
            let badgeEl: React.ReactNode = null;
            let dimClass = "opacity-50";

            if (entry.matched) {
              borderClass = "border-emerald-400/60 shadow-[0_0_6px_rgba(52,211,153,0.3)]";
              dimClass = "opacity-100";
              badgeEl = (
                <div className="absolute -top-1 -right-1 z-20 w-3 h-3 rounded-full bg-emerald-500 flex items-center justify-center">
                  <span className="text-[6px] font-black text-white leading-none">✓</span>
                </div>
              );
            } else if (entry.missed) {
              borderClass = "border-orange-500/50 shadow-[0_0_4px_rgba(249,115,22,0.25)]";
              dimClass = "opacity-100";
              badgeEl = (
                <div className="absolute -top-1 -right-1 z-20 w-3 h-3 rounded-full bg-orange-500 flex items-center justify-center">
                  <span className="text-[6px] font-black text-white leading-none">✗</span>
                </div>
              );
            }

            return (
              <div
                key={i}
                ref={i === entries.length - 1 ? lastCardRef : undefined}
                className={`relative shrink-0 rounded-md overflow-hidden border ${borderClass} ${dimClass} transition-all duration-300`}
                style={{
                  width: 32,
                  height: 48,
                  scrollSnapAlign: "center",
                  animationDelay: `${Math.min(i, 30) * 20}ms`,
                }}
                title={`#${entry.number} ${entry.name} — Turno ${entry.turn + 1}${
                  entry.matched ? " (Acertada)" : entry.missed ? " (Fallada)" : ""
                }`}
              >
                {/* Card image or emoji fallback */}
                {imageSrc ? (
                  <Image
                    src={imageSrc}
                    alt={entry.name}
                    className="absolute inset-0 w-full h-full object-cover"
                    draggable={false}
                    fill
                    sizes="32px"
                  />
                ) : (
                  <div
                    className="absolute inset-0 flex items-center justify-center text-sm"
                    style={{
                      background: `radial-gradient(110% 75% at 50% 0%, hsl(${entry.number * 47 % 360},50%,30%) 0%, hsl(${entry.number * 47 % 360},40%,15%) 55%, hsl(${entry.number * 47 % 360},30%,8%) 100%)`,
                    }}
                  >
                    {emoji}
                  </div>
                )}

                {/* Turn number at bottom */}
                <div className="absolute bottom-0 left-0 right-0 bg-black/70 px-0.5 z-10">
                  <span className="text-[6px] font-black text-white block text-center leading-tight">
                    {entry.turn + 1}
                  </span>
                </div>

                {/* Match/miss badge */}
                {badgeEl}
              </div>
            );
          })}
        </div>
      </div>

      {/* "Scroll for more" hint — shown only if scrollable */}
      {entries.length > 12 && (
        <p className="text-[7px] text-slate-600 text-center font-bold">
          ← desplaza para ver todas las cartas →
        </p>
      )}
    </div>
  );
}
