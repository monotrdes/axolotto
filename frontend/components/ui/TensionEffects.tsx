"use client";

import React from "react";

// ── Types ─────────────────────────────────────────────────────────────────────

export type TensionLevel = "low" | "medium" | "high" | "critical";

interface TensionEffectsProps {
  level: TensionLevel;
  children?: React.ReactNode;
  /** Disable heartbeat animation (mobile performance) */
  disableHeartbeat?: boolean;
}

// ── Component ─────────────────────────────────────────────────────────────────

export default function TensionEffects({
  level,
  children,
  disableHeartbeat = false,
}: TensionEffectsProps) {
  if (level === "low") {
    return <>{children}</>;
  }

  // Medium: subtle border pulse
  if (level === "medium") {
    return (
      <div className="relative animate-tension-pulse">
        <div className="absolute inset-0 rounded-2xl border-2 border-amber-500/20 pointer-events-none" />
        {children}
      </div>
    );
  }

  // High: heartbeat animation on container
  if (level === "high") {
    return (
      <div className={`relative ${disableHeartbeat ? "" : "animate-heartbeat"}`}>
        {/* Glow border overlay */}
        <div className="absolute inset-0 rounded-2xl border-2 border-rose-500/30 shadow-[0_0_20px_rgba(244,63,94,0.15)] pointer-events-none animate-tension-pulse" />
        {children}
      </div>
    );
  }

  // Critical: heartbeat + vignette overlay
  return (
    <div className={`relative ${disableHeartbeat ? "" : "animate-heartbeat"}`}>
      {/* Red vignette overlay */}
      <div className="absolute inset-0 rounded-2xl pointer-events-none z-10"
        style={{
          background: "radial-gradient(ellipse at center, transparent 40%, rgba(239,68,68,0.12) 80%, rgba(239,68,68,0.2) 100%)",
        }}
      />
      {/* Glow border */}
      <div className="absolute inset-0 rounded-2xl border-2 border-red-500/40 shadow-[0_0_30px_rgba(239,68,68,0.25)] pointer-events-none animate-pulse z-10" />
      {children}
    </div>
  );
}
