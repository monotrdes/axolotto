"use client";

/**
 * ActKarmaReveal — Dramatic karma determination + card reveal.
 * 1. Suspense dialogue from Webito
 * 2. 2s loading animation "El cenote evalúa..."
 * 3. Karma card appears (lucky 🍀 or salty 🧂)
 * 4. Webito reacts per karma × nature
 * 5. "¡Hacer eclosionar!" → onComplete(karma)
 */

import React, { useState, useCallback, useEffect } from "react";
import WebitoDialogue from "../WebitoDialogue";
import type { WebitoData } from "../TutorialScript";
import { ACT8_SUSPENSE, ACT8_KARMA_REACTION } from "../dialogues";
import { API_BASE } from "@/lib/api";

type KarmaPhase = "suspense" | "loading" | "reveal" | "reaction";

const KARMA_CONFIG = {
  lucky: {
    emoji:       "🍀",
    title:       "Karma de Suerte",
    subtitle:    "Las estrellas te sonríen. Tu Axolotito nace con el aura del afortunado — drops raros, lucky saves y sorpresas doradas te esperan.",
    gradient:    "linear-gradient(135deg, rgba(251,191,36,0.18) 0%, rgba(52,211,153,0.12) 100%)",
    borderColor: "#fbbf24",
    glowColor:   "rgba(251,191,36,0.45)",
  },
  salty: {
    emoji:       "🧂",
    title:       "Karma Salado",
    subtitle:    "La sal forja el carácter. Tu Axolotito nace con el karma del superviviente — más resistente, más seco, con un humor que solo mejora con las derrotas.",
    gradient:    "linear-gradient(135deg, rgba(0,229,255,0.16) 0%, rgba(99,102,241,0.12) 100%)",
    borderColor: "#00e5ff",
    glowColor:   "rgba(0,229,255,0.4)",
  },
};

interface Props {
  webito: WebitoData;
  onComplete: (karma: "lucky" | "salty") => void;
}

export default function ActKarmaReveal({ webito, onComplete }: Props) {
  const [phase, setPhase]           = useState<KarmaPhase>("suspense");
  const [resolvedKarma, setKarma]   = useState<"lucky" | "salty">(
    webito.karma ?? (webito.bonusLuck > 60 ? "lucky" : "salty")
  );

  // After suspense dismissed, fetch karma from backend then show reveal
  const handleSuspenseDismiss = useCallback(async () => {
    setPhase("loading");
    try {
      const headers: Record<string, string> = {};
      if (webito.token) headers["Authorization"] = `Bearer ${webito.token}`;
      // karma is already determined by next-step phase 3 → we just read it
      // The loading delay is for dramatic effect
    } catch { /* non-fatal */ }
    setTimeout(() => setPhase("reveal"), 2200);
  }, [webito.token]);

  const handleReactionDismiss = useCallback(() => {
    onComplete(resolvedKarma);
  }, [resolvedKarma, onComplete]);

  const cfg = KARMA_CONFIG[resolvedKarma];

  return (
    <div className="flex flex-col items-center gap-5 py-8 px-3 max-w-sm mx-auto w-full text-center">

      {/* Suspense phase */}
      {phase === "suspense" && (
        <>
          <div className="text-[80px] leading-none" style={{ animation: "axo-bob 1.5s ease-in-out infinite" }}>
            🥚
          </div>
          <p className="text-[10px] font-black uppercase tracking-widest" style={{ color: "#64748b" }}>
            El cenote evalúa...
          </p>
          <WebitoDialogue
            text={ACT8_SUSPENSE[webito.nature]}
            speaker="webito"
            onDismiss={handleSuspenseDismiss}
          />
        </>
      )}

      {/* Loading phase */}
      {phase === "loading" && (
        <>
          <div className="text-[80px] leading-none" style={{ animation: "axo-bob 0.8s ease-in-out infinite" }}>
            🥚
          </div>
          <div className="space-y-2">
            <p className="text-base font-black uppercase tracking-widest animate-pulse" style={{ color: "#818cf8" }}>
              El cenote decide...
            </p>
            <div className="flex justify-center gap-1.5">
              {[0, 1, 2].map(i => (
                <div
                  key={i}
                  className="w-2 h-2 rounded-full animate-bounce"
                  style={{
                    background: "#818cf8",
                    animationDelay: `${i * 150}ms`,
                  }}
                />
              ))}
            </div>
          </div>
        </>
      )}

      {/* Reveal phase */}
      {phase === "reveal" && (
        <>
          <p className="text-[10px] font-black uppercase tracking-widest" style={{ color: "#64748b" }}>
            Tu Axolotito nace con...
          </p>
          <div
            className="w-full rounded-3xl p-7 space-y-4"
            style={{
              background: cfg.gradient,
              border: `2px solid ${cfg.borderColor}`,
              boxShadow: `0 0 36px ${cfg.glowColor}`,
              animation: "karma-appear 0.6s cubic-bezier(0.34,1.56,0.64,1) both",
            }}
          >
            <p className="text-6xl" role="img" aria-label={cfg.title}>{cfg.emoji}</p>
            <h3 className="text-2xl font-black uppercase tracking-tight" style={{ color: cfg.borderColor }}>
              {cfg.title}
            </h3>
            <p className="text-slate-300 text-sm leading-relaxed">{cfg.subtitle}</p>
          </div>
          <button
            onClick={() => setPhase("reaction")}
            className="w-full py-3.5 rounded-2xl font-black text-base uppercase tracking-widest text-white transition-all active:scale-95"
            style={{
              background: `linear-gradient(135deg, ${cfg.borderColor}, ${cfg.borderColor}99)`,
              boxShadow: `0 0 24px ${cfg.glowColor}`,
            }}
          >
            ¡Así naceré!
          </button>
        </>
      )}

      {/* Reaction phase */}
      {phase === "reaction" && (
        <>
          <div className="text-[80px] leading-none" style={{ animation: "axo-bob 1s ease-in-out infinite" }}>
            🥚
          </div>
          <WebitoDialogue
            text={ACT8_KARMA_REACTION[resolvedKarma][webito.nature]}
            speaker="webito"
            onDismiss={handleReactionDismiss}
          />
          <button
            onClick={handleReactionDismiss}
            className="w-full py-4 rounded-2xl font-black text-lg uppercase tracking-widest text-white transition-all active:scale-95"
            style={{
              background: "linear-gradient(135deg, #E4007C, #B30062)",
              boxShadow: "0 0 32px rgba(228,0,124,0.55)",
            }}
          >
            ¡Hacer eclosionar! 🥚
          </button>
        </>
      )}
    </div>
  );
}
