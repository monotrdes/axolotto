"use client";

/**
 * ActWorldIntro — Ecosystem tour by the newly born Axolotito.
 * Section cards appear staggered (400ms each).
 * Ends with karma-based CTA → onComplete().
 */

import React, { useState, useEffect, useCallback } from "react";
import WebitoDialogue from "../WebitoDialogue";
import type { WebitoData } from "../TutorialScript";
import { ACT10_INTRO, ACT10_CTA } from "../dialogues";

interface Section {
  emoji: string;
  title: string;
  desc: string;
  color: string;
  comingSoon?: boolean;
}

const SECTIONS: Section[] = [
  {
    emoji: "🎴",
    title: "Salas de Juego",
    desc: "Partidas reales. FRJ en juego. La liga mayor del cenote.",
    color: "#E4007C",
  },
  {
    emoji: "🥚",
    title: "El Nido",
    desc: "Aquí vivo y crezco. Puedo subir mis stats, evolucionar, incubar.",
    color: "#34d399",
  },
  {
    emoji: "🏪",
    title: "La Tienda",
    desc: "Cartas especiales, consumibles, potenciadores. La economía del cenote.",
    color: "#fbbf24",
  },
  {
    emoji: "👑",
    title: "El Ranking",
    desc: "Los mejores jugadores del cenote. Un día tú estarás aquí.",
    color: "#818cf8",
  },
  {
    emoji: "🗺️",
    title: "El Mapa",
    desc: "Algún día podrás caminar por todo el cenote. Por ahora... ¡a las salas!",
    color: "#475569",
    comingSoon: true,
  },
];

interface Props {
  webito: WebitoData;
  onComplete: () => void;
}

export default function ActWorldIntro({ webito, onComplete }: Props) {
  const [introDone, setIntroDone] = useState(false);
  const [visibleSections, setVisibleSections] = useState(0);
  const [ctaVisible, setCtaVisible] = useState(false);

  // Reveal sections one by one after intro
  useEffect(() => {
    if (!introDone) return;
    if (visibleSections >= SECTIONS.length) {
      setTimeout(() => setCtaVisible(true), 400);
      return;
    }
    const t = setTimeout(() => setVisibleSections(n => n + 1), 400);
    return () => clearTimeout(t);
  }, [introDone, visibleSections]);

  const handleIntroDismiss = useCallback(() => setIntroDone(true), []);

  const karma = webito.karma ?? "lucky";
  const ctaText = ACT10_CTA[karma];

  return (
    <div className="flex flex-col items-center gap-4 py-4 px-3 max-w-sm mx-auto w-full">
      {/* Axolotito floating */}
      <div
        className="text-[64px] leading-none"
        role="img"
        aria-label="Tu Axolotito"
        style={{
          filter: "drop-shadow(0 0 18px rgba(52,211,153,0.6))",
          animation: "axo-bob 2s ease-in-out infinite",
        }}
      >
        🦎
      </div>

      {/* Intro dialogue */}
      {!introDone && (
        <div className="w-full">
          <WebitoDialogue
            text={ACT10_INTRO[webito.nature]}
            speaker="axo"
            onDismiss={handleIntroDismiss}
          />
        </div>
      )}

      {/* Section cards */}
      {introDone && (
        <div className="w-full space-y-2">
          {SECTIONS.map((sec, idx) => (
            <div
              key={sec.title}
              className="flex items-start gap-3 p-3 rounded-2xl transition-all duration-500"
              style={{
                opacity: idx < visibleSections ? 1 : 0,
                transform: idx < visibleSections ? "translateY(0)" : "translateY(10px)",
                background: sec.comingSoon
                  ? "rgba(255,255,255,0.02)"
                  : "rgba(255,255,255,0.04)",
                border: `1px solid ${sec.comingSoon ? "rgba(255,255,255,0.06)" : `${sec.color}30`}`,
              }}
            >
              <span
                className="text-2xl flex-shrink-0"
                style={{ filter: sec.comingSoon ? "grayscale(1) opacity(0.4)" : "none" }}
              >
                {sec.emoji}
              </span>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <p
                    className="text-sm font-black uppercase tracking-wide"
                    style={{ color: sec.comingSoon ? "#334155" : sec.color }}
                  >
                    {sec.title}
                  </p>
                  {sec.comingSoon && (
                    <span
                      className="text-[9px] font-black px-1.5 py-0.5 rounded uppercase tracking-widest"
                      style={{ background: "rgba(255,255,255,0.06)", color: "#475569" }}
                    >
                      pronto
                    </span>
                  )}
                </div>
                <p
                  className="text-[11px] mt-0.5 leading-snug"
                  style={{ color: sec.comingSoon ? "#334155" : "#64748b" }}
                >
                  {sec.desc}
                </p>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* CTA */}
      {ctaVisible && (
        <button
          onClick={onComplete}
          className="w-full py-4 mt-2 rounded-2xl font-black text-lg uppercase tracking-widest text-white transition-all active:scale-95"
          style={{
            background: karma === "lucky"
              ? "linear-gradient(135deg, #fbbf24, #E4007C)"
              : "linear-gradient(135deg, #00e5ff, #475569)",
            boxShadow: karma === "lucky"
              ? "0 0 32px rgba(251,191,36,0.4)"
              : "0 0 32px rgba(0,229,255,0.3)",
            animation: "karma-appear 0.5s cubic-bezier(0.34,1.56,0.64,1) both",
          }}
        >
          {ctaText}
        </button>
      )}
    </div>
  );
}
