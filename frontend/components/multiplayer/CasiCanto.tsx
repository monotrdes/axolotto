"use client";

import React from "react";

// ── Types ─────────────────────────────────────────────────────────────────────

interface CasiCantoProps {
  /** Show the anticipation overlay */
  active: boolean;
  /** Optional player name for the "está a una carta!" reveal text */
  nearWinPlayerName?: string;
  /** How close to winning — controls timing and intensity */
  intensity: "low" | "medium" | "high";
}

// ── Intensity config ──────────────────────────────────────────────────────────

const INTENSITY_CONFIG = {
  low: {
    sweepDuration: 3,        // seconds per sweep cycle
    vignetteOpacity: 0.15,
    drumrollDuration: 3,     // seconds to fill
    drumrollVisible: false,
  },
  medium: {
    sweepDuration: 1.8,
    vignetteOpacity: 0.3,
    drumrollDuration: 1.5,
    drumrollVisible: true,
  },
  high: {
    sweepDuration: 0.8,
    vignetteOpacity: 0.5,
    drumrollDuration: 0.8,
    drumrollVisible: true,
  },
};

// ── Component ─────────────────────────────────────────────────────────────────

export default function CasiCanto({
  active,
  nearWinPlayerName,
  intensity,
}: CasiCantoProps) {
  if (!active) return null;

  const cfg = INTENSITY_CONFIG[intensity];

  return (
    <div
      className="absolute inset-0 pointer-events-none z-40 overflow-hidden"
      aria-hidden="true"
    >
      {/* ── Golden radial vignette at screen edges ──────────────────────────────
           Pulses with golden-heartbeat rhythm */}
      <div
        className="absolute inset-0 transition-all duration-700"
        style={{
          background:
            "radial-gradient(ellipse at center, transparent 40%, rgba(251,191,36,0.08) 60%, rgba(251,191,36,0.15) 100%)",
          opacity: cfg.vignetteOpacity,
          animation: intensity !== "low"
            ? "golden-vignette-pulse 1s ease-in-out infinite"
            : undefined,
        }}
      />

      {/* ── "¡CASI!" whisper sweep ────────────────────────────────────────────
           Sweeps across the top of the screen from left to right */}
      <div className="absolute top-4 left-0 w-full overflow-hidden">
        <span
          className="inline-block text-[9px] font-black text-amber-400/70 uppercase tracking-[0.35em]"
          style={{
            animation: `casi-sweep ${cfg.sweepDuration}s ease-in-out infinite`,
          }}
        >
          {nearWinPlayerName
            ? `${nearWinPlayerName} — ¡CASI!`
            : "¡CASI!"}
        </span>
      </div>

      {/* ── Name reveal (only for medium/high intensity) ───────────────────────
           Shows "¡{name} está a una carta!" in tiny text below the vignette */}
      {intensity !== "low" && nearWinPlayerName && (
        <div className="absolute left-0 w-full text-center" style={{ top: "55%" }}>
          <span
            className="inline-block text-[8px] font-bold text-amber-400/50 tracking-wider"
            style={{
              animation: `casi-sweep ${cfg.sweepDuration * 1.5}s ease-in-out infinite`,
              animationDelay: "0.5s",
            }}
          >
            ¡{nearWinPlayerName} está a una carta!
          </span>
        </div>
      )}

      {/* ── Drumroll bar at the bottom ────────────────────────────────────────
           Fills from left to right repeatedly while active */}
      {cfg.drumrollVisible && (
        <div
          className="absolute bottom-3 left-4 right-4 h-0.5 overflow-hidden"
          style={{
            background: "rgba(251,191,36,0.1)",
            borderRadius: "2px",
          }}
        >
          <div
            className="h-full"
            style={{
              width: 0,
              background:
                "linear-gradient(90deg, rgba(251,191,36,0.3), rgba(251,191,36,0.8), rgba(251,191,36,0.3))",
              borderRadius: "2px",
              animation: `drumroll-fill ${cfg.drumrollDuration}s linear infinite`,
            }}
          />
        </div>
      )}
    </div>
  );
}
