"use client";

import React, { useId } from "react";

// ── Types ─────────────────────────────────────────────────────────────────────

interface RippleEffectProps {
  /** Show the ripple animation */
  active: boolean;
  /** 0-100, controls ripple speed (higher = faster) */
  intensity: number;
  /** CSS color for the ripple rings (default indigo) */
  color?: string;
}

// ── Component ─────────────────────────────────────────────────────────────────

export default function RippleEffect({
  active,
  intensity,
  color = "rgba(99,102,241,0.6)",
}: RippleEffectProps) {
  const id = useId();

  if (!active) return null;

  // Duration inversely proportional to intensity (higher intensity = faster)
  const duration = Math.max(0.6, 1.5 - (intensity / 100) * 0.9);
  const animName = `ripple-expand-${id.replace(/[^a-zA-Z0-9]/g, "")}`;

  return (
    <>
      <style>{`
        @keyframes ${animName} {
          0% {
            box-shadow: 0 0 0 0px ${color};
          }
          100% {
            box-shadow: 0 0 0 75px transparent;
          }
        }
      `}</style>
      <div className="absolute inset-0 pointer-events-none z-30">
        {[0, 1, 2].map((i) => (
          <div
            key={i}
            className="absolute w-0.5 h-0.5 rounded-full"
            style={{
              left: "50%",
              top: "50%",
              transform: "translate(-50%, -50%)",
              background: "transparent",
              animation: `${animName} ${duration}s ease-out infinite`,
              animationDelay: `${i * 0.2}s`,
            }}
          />
        ))}
      </div>
    </>
  );
}
