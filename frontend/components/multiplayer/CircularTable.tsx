/**
 * CircularTable — Mesa de lotería en estética de cartón y papel picado
 * (plan task-84 §5, reemplaza la mesa de piedra neón).
 */

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

// ── Tension → papel edge glow ─────────────────────────────────────────────────

const TENSION_GLOW: Record<TensionLevel, { color: string; spread: number }> = {
  low:      { color: "rgba(255,247,236,0.12)", spread: 12 },
  medium:   { color: "rgba(228,0,124,0.15)",   spread: 22 },
  high:     { color: "rgba(245,158,11,0.25)",  spread: 35 },
  critical: { color: "rgba(228,0,124,0.4)",    spread: 50 },
};

// ── Papel picado marks around the edge (12 cut-out dots) ──────────────────────

const PAPEL_MARKS = Array.from({ length: 12 }, (_, i) => {
  const angle = (i / 12) * Math.PI * 2 - Math.PI / 2;
  const r = 46;
  return {
    angle,
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
      {/* ── Main cartón table ────────────────────────────────────────────── */}
      <div
        className="absolute rounded-full"
        style={{
          width: "92%",
          height: "92%",
          background: `
            radial-gradient(ellipse at 40% 35%, rgba(162,115,64,1) 0%, rgba(139,94,52,1) 40%, rgba(107,68,34,1) 100%)
          `,
          borderRadius: "50%",
          boxShadow: `
            0 6px 24px rgba(0,0,0,0.45),
            inset 0 2px 0 rgba(255,247,236,0.1),
            inset 0 -3px 0 rgba(0,0,0,0.25),
            0 0 ${glow.spread}px ${glow.color}
          `,
          border: "3px solid rgba(255,247,236,0.25)",
          transition: "box-shadow 0.6s ease, border-color 0.6s ease",
        }}
      >
        {/* Inner ring — papel picado filigrana */}
        <div
          className="absolute rounded-full"
          style={{
            top: "8%",
            left: "8%",
            width: "84%",
            height: "84%",
            border: "2px dashed rgba(255,247,236,0.12)",
            borderRadius: "50%",
            pointerEvents: "none",
          }}
        />

        {/* Center depression — mancha de tinta */}
        <div
          className="absolute rounded-full"
          style={{
            top: "38%",
            left: "38%",
            width: "24%",
            height: "24%",
            background: "radial-gradient(ellipse at 50% 50%, rgba(59,42,24,0.5) 0%, rgba(107,68,34,0.2) 60%, transparent 100%)",
            borderRadius: "50%",
            boxShadow: "inset 0 2px 6px rgba(0,0,0,0.3)",
            pointerEvents: "none",
          }}
        />
      </div>

      {/* ── Papel picado cutout marks around the edge ─────────────────────── */}
      {PAPEL_MARKS.map((mark, i) => (
        <div
          key={`papel-mark-${i}`}
          className="absolute rounded-full"
          style={{
            width: i % 3 === 0 ? "7px" : "5px",
            height: i % 3 === 0 ? "7px" : "5px",
            left: `${mark.x}%`,
            top: `${mark.y}%`,
            transform: "translate(-50%, -50%)",
            background:
              i % 3 === 0
                ? "rgba(228,0,124,0.3)"
                : i % 3 === 1
                  ? "rgba(245,158,11,0.22)"
                  : "rgba(45,212,191,0.18)",
            boxShadow:
              i % 3 === 0
                ? "0 0 4px rgba(228,0,124,0.15)"
                : "none",
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
