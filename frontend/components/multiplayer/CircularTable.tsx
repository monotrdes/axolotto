"use client";

import React from "react";
import type { TensionLevel } from "../ui/TensionEffects";

// ── Types ─────────────────────────────────────────────────────────────────────

interface CircularTableProps {
  /** Diameter in px (min 400, defaults to 440) */
  diameter?: number;
  tensionLevel?: TensionLevel;
  children?: React.ReactNode;
}

// ── Glow intensity map ────────────────────────────────────────────────────────

const TENSION_GLOW: Record<TensionLevel, { color: string; spread: number }> = {
  low:      { color: "rgba(30,120,200,0.15)", spread: 20 },
  medium:   { color: "rgba(30,120,200,0.3)",  spread: 35 },
  high:     { color: "rgba(200,80,80,0.35)",  spread: 45 },
  critical: { color: "rgba(239,68,68,0.5)",   spread: 60 },
};

// ── Rune positions (12 runes around the edge) ─────────────────────────────────

const RUNE_POSITIONS = Array.from({ length: 12 }, (_, i) => {
  const angle = (i / 12) * Math.PI * 2 - Math.PI / 2;
  // Positioned on a ring ~46% from center (just inside the edge)
  const r = 46;
  return {
    angle: angle,
    x: 50 + r * Math.cos(angle),
    y: 50 + r * Math.sin(angle),
  };
});

// ── Component ─────────────────────────────────────────────────────────────────

export default function CircularTable({
  diameter = 440,
  tensionLevel = "low",
  children,
}: CircularTableProps) {
  const glow = TENSION_GLOW[tensionLevel] ?? TENSION_GLOW.low;
  const tableSize = Math.max(400, diameter);

  return (
    <div
      className="relative flex items-center justify-center"
      style={{
        width: tableSize,
        height: tableSize,
      }}
    >
      {/* Main stone table */}
      <div
        className="absolute rounded-full animate-stone-pulse"
        style={{
          width: "92%",
          height: "92%",
          background: `
            conic-gradient(
              from 0deg,
              rgba(60,65,75,1) 0deg,
              rgba(80,85,95,1) 30deg,
              rgba(55,60,70,1) 60deg,
              rgba(70,75,85,1) 90deg,
              rgba(50,55,65,1) 120deg,
              rgba(75,80,90,1) 150deg,
              rgba(55,60,70,1) 180deg,
              rgba(65,70,80,1) 210deg,
              rgba(50,55,65,1) 240deg,
              rgba(80,85,95,1) 270deg,
              rgba(60,65,75,1) 300deg,
              rgba(70,75,85,1) 330deg,
              rgba(60,65,75,1) 360deg
            )
          `,
          borderRadius: "50%",
          boxShadow: `
            0 8px 32px rgba(0,0,0,0.5),
            inset 0 2px 4px rgba(255,255,255,0.05),
            inset 0 -4px 8px rgba(0,0,0,0.3),
            0 0 ${glow.spread}px ${glow.color}
          `,
          transition: "box-shadow 0.6s ease",
        }}
      >
        {/* Inner carved ring (concentric) */}
        <div
          className="absolute rounded-full"
          style={{
            top: "8%",
            left: "8%",
            width: "84%",
            height: "84%",
            border: "1px solid rgba(255,255,255,0.04)",
            background: "radial-gradient(ellipse at 50% 50%, rgba(40,45,55,0.3) 0%, transparent 70%)",
            borderRadius: "50%",
            pointerEvents: "none",
          }}
        />

        {/* Center depression */}
        <div
          className="absolute rounded-full"
          style={{
            top: "38%",
            left: "38%",
            width: "24%",
            height: "24%",
            background: "radial-gradient(ellipse at 50% 50%, rgba(30,35,45,0.6) 0%, rgba(40,45,55,0.3) 60%, transparent 100%)",
            borderRadius: "50%",
            boxShadow: "inset 0 2px 8px rgba(0,0,0,0.4)",
            pointerEvents: "none",
          }}
        />
      </div>

      {/* Rune marks around the edge */}
      {RUNE_POSITIONS.map((rune, i) => (
        <div
          key={`rune-${i}`}
          className="absolute rounded-full"
          style={{
            width: "8px",
            height: "8px",
            left: `${rune.x}%`,
            top: `${rune.y}%`,
            transform: "translate(-50%, -50%)",
            background:
              i % 3 === 0
                ? "rgba(100,180,220,0.25)"
                : i % 3 === 1
                  ? "rgba(80,160,200,0.18)"
                  : "rgba(60,140,180,0.12)",
            boxShadow:
              i % 3 === 0
                ? "0 0 6px rgba(100,180,220,0.2)"
                : "none",
            pointerEvents: "none",
          }}
        />
      ))}

      {/* Second ring of smaller marks */}
      {RUNE_POSITIONS.filter((_, i) => i % 2 === 0).map((rune, i) => (
        <div
          key={`rune-small-${i}`}
          className="absolute rounded-full"
          style={{
            width: "4px",
            height: "4px",
            left: `${50 + 40 * Math.cos(rune.angle + 0.2)}%`,
            top: `${50 + 40 * Math.sin(rune.angle + 0.2)}%`,
            transform: "translate(-50%, -50%)",
            background: "rgba(60,140,200,0.10)",
            pointerEvents: "none",
          }}
        />
      ))}

      {/* Content area (center of table) */}
      <div
        className="relative z-10 flex items-center justify-center"
        style={{
          width: "50%",
          height: "50%",
        }}
      >
        {children}
      </div>
    </div>
  );
}
