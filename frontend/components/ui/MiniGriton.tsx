"use client";

import React, { useRef, useEffect, useState } from "react";
import { LOTERIA_EMOJI, CARD_IMAGE } from "./LoteriaCard";
import Image from "next/image";

// ── Types ─────────────────────────────────────────────────────────────────────

export interface MiniGritonProps {
  /** All card names called during the game, in order */
  calledCards: string[];
  /** Map from card name → lotería number (1-54) */
  nameToNum: Map<string, number>;
  /** The 4 card numbers that form the winning pattern on the board */
  winningCardNumbers: number[];
  /** Whether the player won (affects dialogue and styling) */
  isWinner: boolean;
  /** Optional additional class names */
  className?: string;
}

// ── Gritón dialogue variants ──────────────────────────────────────────────────

const GRITON_WIN_PHRASES = [
  "¡BUENA SUERTE!",
  "¡FELICIDADES!",
  "¡YA GANÓOOO!",
  "¡LOTERÍAAAA!",
];

const GRITON_LOSE_PHRASES = [
  "¡MEJOR SUERTE LA PRÓXIMA!",
  "¡OTRO JUGADOR GANÓ!",
  "¡LA SUERTE NO ACOMPAÑÓ!",
  "¡ÁNIMO, CAMPEÓN!",
];

// ── Component ─────────────────────────────────────────────────────────────────

export default function MiniGriton({
  calledCards,
  nameToNum,
  winningCardNumbers,
  isWinner,
  className = "",
}: MiniGritonProps) {
  const scrollRef = useRef<HTMLDivElement>(null);
  const [dialogue] = useState(() => {
    const pool = isWinner ? GRITON_WIN_PHRASES : GRITON_LOSE_PHRASES;
    return pool[Math.floor(Math.random() * pool.length)];
  });
  const [showDialogue, setShowDialogue] = useState(false);

  // Auto-scroll to end on mount (after cards render)
  useEffect(() => {
    const timer = setTimeout(() => {
      if (scrollRef.current) {
        scrollRef.current.scrollTo({
          left: scrollRef.current.scrollWidth,
          behavior: "smooth",
        });
      }
      // Show dialogue after scroll
      setTimeout(() => setShowDialogue(true), 400);
    }, 300);
    return () => clearTimeout(timer);
  }, []);

  // Resolve called cards to {name, number} pairs (deduplicated by number, keep last)
  const resolvedCards = React.useMemo(() => {
    const seen = new Map<number, { name: string; number: number }>();
    for (const cardName of calledCards) {
      const num = nameToNum.get(cardName.toLowerCase()) ?? 0;
      if (num > 0 && !seen.has(num)) {
        seen.set(num, { name: cardName, number: num });
      }
    }
    return [...seen.values()];
  }, [calledCards, nameToNum]);

  const winningSet = new Set(winningCardNumbers);

  if (resolvedCards.length === 0) return null;

  return (
    <div className={`flex flex-col items-center gap-2 ${className}`}>
      {/* Gritón character + dialogue bubble */}
      <div className="relative flex items-center gap-2">
        {/* Gritón avatar */}
        <div
          className={`shrink-0 w-12 h-12 rounded-full flex items-center justify-center text-3xl border-2 transition-all duration-500 ${
            isWinner
              ? "bg-amber-950/60 border-amber-500/50 shadow-[0_0_16px_rgba(251,191,36,0.4)]"
              : "bg-slate-900/60 border-slate-600/50"
          }`}
        >
          <span className={isWinner ? "animate-bounce" : ""}>🎤</span>
        </div>

        {/* Speech bubble */}
        <div
          className={`relative px-4 py-2 rounded-2xl border transition-all duration-700 ${
            showDialogue ? "opacity-100 scale-100" : "opacity-0 scale-75"
          } ${
            isWinner
              ? "bg-amber-950/40 border-amber-500/30 text-amber-200"
              : "bg-slate-900/60 border-slate-700/40 text-slate-300"
          }`}
        >
          {/* Bubble tail */}
          <div
            className={`absolute left-[-6px] top-1/2 -translate-y-1/2 w-3 h-3 rotate-45 border-l border-b ${
              isWinner
                ? "bg-amber-950/40 border-amber-500/30"
                : "bg-slate-900/60 border-slate-700/40"
            }`}
          />
          <p className="text-[11px] font-black uppercase tracking-widest whitespace-nowrap">
            {dialogue}
          </p>
        </div>
      </div>

      {/* Cards grid — compact scrollable */}
      <div
        ref={scrollRef}
        className="w-full overflow-x-auto scrollbar-hide rounded-xl border border-white/10 bg-slate-950/50 p-2"
        style={{ scrollSnapType: "x mandatory" }}
      >
        <div className="flex gap-1 min-w-max">
          {resolvedCards.map((card, i) => {
            const isWinning = winningSet.has(card.number);
            const emoji = LOTERIA_EMOJI[card.number] || "🃏";
            const imageSrc = CARD_IMAGE[card.number];

            return (
              <div
                key={`${card.number}-${i}`}
                className={`relative shrink-0 rounded-md transition-all duration-500 flex flex-col items-center justify-center ${
                  isWinning
                    ? "animate-board-fill-cell"
                    : "opacity-40 hover:opacity-80"
                }`}
                style={{
                  width: 40,
                  height: 60,
                  animationDelay: `${i * 15}ms`,
                  scrollSnapAlign: "center",
                }}
              >
                {/* Card background */}
                <div
                  className={`absolute inset-0 rounded-md overflow-hidden border ${
                    isWinning
                      ? "border-amber-400/80 shadow-[0_0_12px_rgba(251,191,36,0.7)]"
                      : "border-slate-700/40"
                  }`}
                >
                  {imageSrc ? (
                    <Image
                      src={imageSrc}
                      alt={card.name}
                      className="absolute inset-0 w-full h-full object-cover"
                      draggable={false}
                      fill
                      sizes="40px"
                    />
                  ) : (
                    <div
                      className="absolute inset-0 flex items-center justify-center text-xl"
                      style={{
                        background: isWinning
                          ? "radial-gradient(110% 75% at 50% 0%, hsl(45,85%,55%) 0%, hsl(45,75%,30%) 55%, hsl(45,80%,12%) 100%)"
                          : `radial-gradient(110% 75% at 50% 0%, hsl(${card.number * 47 % 360},50%,30%) 0%, hsl(${card.number * 47 % 360},40%,15%) 55%, hsl(${card.number * 47 % 360},30%,8%) 100%)`,
                      }}
                    >
                      {emoji}
                    </div>
                  )}
                </div>

                {/* Winning overlay glow */}
                {isWinning && (
                  <div className="absolute inset-0 rounded-md bg-amber-400/30 pointer-events-none z-10" />
                )}

                {/* Card number badge */}
                <span
                  className={`absolute -bottom-1 z-20 text-[7px] font-black px-1 rounded-full ${
                    isWinning
                      ? "bg-amber-500 text-amber-950"
                      : "bg-slate-800 text-slate-500"
                  }`}
                >
                  {card.number}
                </span>

                {/* "¡LOTERÍA!" tiny badge on winning cards */}
                {isWinning && (
                  <div className="absolute -top-1.5 -right-1 z-20">
                    <span className="text-[7px] font-black text-amber-200 bg-amber-600/90 px-1 py-0.5 rounded-full leading-none whitespace-nowrap animate-pulse">
                      ¡LOT!
                    </span>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Legend */}
      <div className="flex items-center gap-3 text-[8px] font-black uppercase tracking-wider">
        <span className="flex items-center gap-1">
          <span className="w-2.5 h-2.5 rounded-sm bg-amber-400/80 shadow-[0_0_6px_rgba(251,191,36,0.6)]" />
          <span className="text-amber-300">
            {isWinner ? "Cartas ganadoras" : "Cartas del ganador"}
          </span>
        </span>
        <span className="flex items-center gap-1">
          <span className="w-2.5 h-2.5 rounded-sm bg-slate-700/40" />
          <span className="text-slate-500">Cartas llamadas</span>
        </span>
      </div>
    </div>
  );
}
