"use client";

/**
 * ActStatReveal — Animated "Ficha de Incubación" card showing the 4 stats.
 * Stats appear one by one (staggered). Ends with Webito's final comment.
 */

import React, { useState, useEffect, useCallback } from "react";
import WebitoDialogue from "../WebitoDialogue";
import type { WebitoData } from "../TutorialScript";
import { getStatOneliner, ACT2_FINAL_COMMENT } from "../dialogues";

interface Props {
  webito: WebitoData;
  onComplete: () => void;
}

interface StatRow {
  key: "SAL" | "OJO" | "PILA" | "SUERTE";
  emoji: string;
  label: string;
  value: number;
  color: string;
  glowColor: string;
}

function clamp(v: number, lo: number, hi: number): number {
  return Math.max(lo, Math.min(hi, v));
}

export default function ActStatReveal({ webito, onComplete }: Props) {
  const [visibleCount, setVisibleCount] = useState(0);
  const [showFinalComment, setShowFinalComment] = useState(false);

  // Final stats: base + bonus, clamped to valid ranges (matches backend final_stats())
  const finalSal     = Math.round(clamp(webito.baseStatSalinity + webito.bonusSalinityAdj, 0, 100));
  const finalFocus   = Math.round(clamp(webito.baseStatFocus    + webito.bonusFocus,       0, 100));
  // PILA: floor (no round) para igualar el valor persistido del juego (final_stats usa int()).
  const finalStamina = Math.floor(clamp(webito.baseStatStamina  + webito.bonusStamina,    50, 200));
  const finalLuck    = Math.round(clamp(webito.baseStatLuck     + webito.bonusLuck,        0, 100));

  const stats: StatRow[] = [
    { key: "SAL",    emoji: "🧂", label: "SAL",    value: finalSal,     color: "#00e5ff", glowColor: "rgba(0,229,255,0.4)" },
    { key: "OJO",    emoji: "👁️",  label: "OJO",    value: finalFocus,   color: "#818cf8", glowColor: "rgba(129,140,248,0.4)" },
    { key: "PILA",   emoji: "🔋", label: "PILA",   value: finalStamina, color: "#34d399", glowColor: "rgba(52,211,153,0.4)" },
    { key: "SUERTE", emoji: "✨", label: "SUERTE", value: finalLuck,    color: "#fbbf24", glowColor: "rgba(251,191,36,0.4)" },
  ];

  // Reveal stats one by one
  useEffect(() => {
    if (visibleCount >= stats.length) return;
    const t = setTimeout(() => setVisibleCount(c => c + 1), visibleCount === 0 ? 400 : 600);
    return () => clearTimeout(t);
  }, [visibleCount, stats.length]);

  // Show final comment once all stats are visible
  useEffect(() => {
    if (visibleCount < stats.length) return;
    const t = setTimeout(() => setShowFinalComment(true), 500);
    return () => clearTimeout(t);
  }, [visibleCount, stats.length]);

  const handleDismiss = useCallback(() => {
    onComplete();
  }, [onComplete]);

  const natureLabel: Record<string, string> = {
    hyperactive: "HIPERACTIVO",
    lucky:       "SUERTUDO",
    salty:       "SALADO",
    methodical:  "METÓDICO",
    shy:         "TÍMIDO",
  };

  return (
    <div className="flex flex-col items-center gap-4 py-6 px-3 max-w-sm mx-auto w-full">
      {/* Card */}
      <div
        className="w-full rounded-3xl overflow-hidden"
        style={{
          background: "rgba(6,6,20,0.85)",
          border: "1px solid rgba(0,229,255,0.2)",
          boxShadow: "0 0 40px rgba(0,229,255,0.08)",
        }}
      >
        {/* Header */}
        <div
          className="px-5 py-3 flex items-center justify-between"
          style={{ borderBottom: "1px solid rgba(255,255,255,0.06)" }}
        >
          <div className="flex items-center gap-2">
            <span className="text-2xl" role="img" aria-label="Webito">🥚</span>
            <div>
              <p className="text-xs font-black uppercase tracking-widest" style={{ color: "#00e5ff" }}>
                Ficha de Incubación
              </p>
              <p className="text-[10px]" style={{ color: "#475569" }}>
                #{webito.tutorialId} — Sin Nacer
              </p>
            </div>
          </div>
          <span
            className="text-[9px] font-black px-2 py-1 rounded-full uppercase tracking-widest"
            style={{
              background: "rgba(129,140,248,0.15)",
              border: "1px solid rgba(129,140,248,0.3)",
              color: "#818cf8",
            }}
          >
            {natureLabel[webito.nature] ?? webito.nature.toUpperCase()}
          </span>
        </div>

        {/* Stats */}
        <div className="p-5 space-y-4">
          {stats.map((stat, idx) => (
            <div
              key={stat.key}
              className="transition-all duration-500"
              style={{
                opacity: idx < visibleCount ? 1 : 0,
                transform: idx < visibleCount ? "translateY(0)" : "translateY(12px)",
              }}
            >
              <div className="flex items-center gap-2 mb-1">
                <span className="text-base" role="img" aria-label={stat.label}>{stat.emoji}</span>
                <span className="text-xs font-black uppercase tracking-widest" style={{ color: stat.color }}>
                  {stat.label}
                </span>
                <span className="ml-auto text-sm font-black tabular-nums" style={{ color: stat.color }}>
                  {Math.round(stat.value)}
                </span>
              </div>
              {/* Bar */}
              <div
                className="h-2 rounded-full overflow-hidden"
                style={{ background: "rgba(255,255,255,0.06)" }}
              >
                <div
                  className="h-full rounded-full transition-all duration-700"
                  style={{
                    width: idx < visibleCount ? `${Math.min(100, stat.value)}%` : "0%",
                    background: `linear-gradient(90deg, ${stat.color}88, ${stat.color})`,
                    boxShadow: `0 0 8px ${stat.glowColor}`,
                    transitionDelay: `${idx * 120}ms`,
                  }}
                />
              </div>
              {/* One-liner */}
              {idx < visibleCount && (
                <p className="text-[11px] mt-1" style={{ color: "#64748b" }}>
                  {getStatOneliner(stat.key, stat.value)}
                </p>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Final comment */}
      {showFinalComment && (
        <div className="w-full">
          <WebitoDialogue
            text={ACT2_FINAL_COMMENT[webito.nature]}
            speaker="webito"
            onDismiss={handleDismiss}
          />
        </div>
      )}
    </div>
  );
}
