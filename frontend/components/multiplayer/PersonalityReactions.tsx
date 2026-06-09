"use client";

import React from "react";
import {
  PERSONALITY_REACTIONS,
  generateAuraParticles,
  type NatureType,
  type NatureTrigger,
  type AuraParticle,
} from "@/data/personality-config";

// ── Types ────────────────────────────────────────────────────────────────────

interface PersonalityReactionsProps {
  /** Naturaleza del axolotito */
  nature?: NatureType | null;
  /** Evento/trigger actual */
  trigger: NatureTrigger;
  /** Tamaño en px (default 80) */
  size?: number;
  /** Mostrar particulas de aura alrededor */
  showAura?: boolean;
  /** Clase adicional para el contenedor */
  className?: string;
}

// ── Component ────────────────────────────────────────────────────────────────

export default function PersonalityReactions({
  nature,
  trigger,
  size = 80,
  showAura = true,
  className = "",
}: PersonalityReactionsProps) {
  // Fallback a hyperactive si nature es null/undefined/desconocido
  const safeNature: NatureType =
    nature && nature in PERSONALITY_REACTIONS
      ? (nature as NatureType)
      : "hyperactive";

  const config = PERSONALITY_REACTIONS[safeNature][trigger];
  const auraParticles: AuraParticle[] = showAura
    ? generateAuraParticles(safeNature)
    : [];

  return (
    <div
      className={`relative inline-flex items-center justify-center ${className}`}
      style={{ width: size, height: size }}
      aria-label={`${config.description} (${safeNature})`}
    >
      {/* Aura particles */}
      {showAura &&
        auraParticles.map((p, i) => (
          <span
            key={i}
            className={`absolute text-[8px] pointer-events-none select-none ${p.animClass}`}
            style={{
              top: `${p.y}%`,
              left: `${p.x}%`,
              animationDelay: `${i * 200}ms`,
              color: p.color,
            }}
          >
            {p.emoji}
          </span>
        ))}

      {/* Emoji principal con animación de personalidad */}
      <span
        className={`select-none leading-none ${config.animClass}`}
        style={{
          fontSize: size * 0.5,
          filter:
            safeNature === "curious"
              ? "drop-shadow(0 0 4px rgba(0,206,209,0.5))"
              : safeNature === "hyperactive"
                ? "drop-shadow(0 0 4px rgba(255,215,0,0.6))"
                : safeNature === "showoff"
                  ? "drop-shadow(0 0 6px rgba(255,215,0,0.7))"
                  : "none",
        }}
      >
        {config.emoji}
      </span>
    </div>
  );
}
