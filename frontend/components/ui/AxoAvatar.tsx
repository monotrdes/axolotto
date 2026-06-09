"use client";

import React from "react";

// ── Types ─────────────────────────────────────────────────────────────────────

export type AxoReaction =
  | "idle"
  | "card_called"
  | "cell_marked"
  | "cell_missed"
  | "tension_critical"
  | "won"
  | "lost";

interface AxoAvatarProps {
  /** Name of the axolotito */
  name: string;
  /** Reaction state */
  reaction?: AxoReaction;
  /** Image URL (optional, falls back to emoji) */
  imageUrl?: string;
  /** Size in px (default 80) */
  size?: number;
  /** Show name label below */
  showName?: boolean;
}

// ── Reaction config ───────────────────────────────────────────────────────────

const REACTION_CONFIG: Record<AxoReaction, { emoji: string; animClass: string; label: string }> = {
  idle:              { emoji: "🦎", animClass: "animate-axo-bob",      label: "" },
  card_called:       { emoji: "👀", animClass: "animate-axo-look",     label: "¡Atención!" },
  cell_marked:       { emoji: "✨", animClass: "animate-axo-bounce",   label: "¡Marcada!" },
  cell_missed:       { emoji: "😰", animClass: "animate-axo-shake",    label: "¡Se pasó!" },
  tension_critical:  { emoji: "💓", animClass: "animate-heartbeat",    label: "¡Tensión!" },
  won:               { emoji: "🎉", animClass: "animate-axo-jump",     label: "¡GANADOR!" },
  lost:              { emoji: "💤", animClass: "animate-axo-faint",    label: "Eliminado" },
};

// ── Component ─────────────────────────────────────────────────────────────────

export default function AxoAvatar({
  name,
  reaction = "idle",
  imageUrl,
  size = 80,
  showName = true,
}: AxoAvatarProps) {
  const config = REACTION_CONFIG[reaction] ?? REACTION_CONFIG.idle;
  const displaySize = reaction === "won" ? size * 1.3 : reaction === "lost" ? size * 0.8 : size;

  return (
    <div className="flex flex-col items-center gap-1">
      {/* Avatar circle */}
      <div
        className={`relative rounded-full flex items-center justify-center
          bg-gradient-to-b from-slate-800 to-slate-950 border-2 transition-all duration-300 ${config.animClass}`}
        style={{
          width: displaySize,
          height: displaySize,
          borderColor:
            reaction === "won"
              ? "rgb(251,191,36)"
              : reaction === "tension_critical"
                ? "rgb(239,68,68)"
                : reaction === "lost"
                  ? "rgb(100,116,139)"
                  : "rgb(99,102,241)",
        }}
      >
        {imageUrl ? (
          <img
            src={imageUrl}
            alt={name}
            className="w-full h-full object-cover rounded-full"
          />
        ) : (
          <span
            className="select-none"
            style={{ fontSize: displaySize * 0.5 }}
          >
            {config.emoji}
          </span>
        )}

        {/* Reaction sparks */}
        {reaction === "cell_marked" && (
          <>
            <span className="absolute -top-1 -right-1 text-xs animate-ping">✨</span>
            <span className="absolute -bottom-1 -left-1 text-xs animate-ping" style={{ animationDelay: "200ms" }}>💚</span>
          </>
        )}
        {reaction === "won" && (
          <>
            <span className="absolute -top-2 -right-2 text-base animate-bounce">🎊</span>
            <span className="absolute -bottom-2 -left-2 text-base animate-bounce" style={{ animationDelay: "300ms" }}>🎉</span>
          </>
        )}
        {reaction === "cell_missed" && (
          <span className="absolute -top-1 -right-1 text-xs">💧</span>
        )}
      </div>

      {/* Label */}
      {showName && (
        <span
          className={`text-[10px] font-black uppercase tracking-wider truncate max-w-[120px] ${
            reaction === "won"
              ? "text-amber-400"
              : reaction === "lost"
                ? "text-slate-500"
                : "text-slate-300"
          }`}
        >
          {config.label || name}
        </span>
      )}
    </div>
  );
}
