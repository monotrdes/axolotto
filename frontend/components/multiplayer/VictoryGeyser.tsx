"use client";

import React, { useMemo, useState, useEffect } from "react";

// ── Types ─────────────────────────────────────────────────────────────────────

interface VictoryGeyserProps {
  /** Trigger the celebration sequence */
  active: boolean;
  /** Name of the winning player shown in floating text */
  winnerName: string;
  /** Position in the scene (pixel coords). Defaults to center of parent. */
  position?: { x: number; y: number };
}

// ── Constants ─────────────────────────────────────────────────────────────────

const VICTORY_COLORS = ["#FBBF24", "#34D399", "#6366F1", "#EC4899"];
const SPLASH_COLORS = ["#38BDF8", "#22D3EE", "#67E8F9", "#7DD3FC"];

// ── Helpers ───────────────────────────────────────────────────────────────────

function pick<T>(arr: readonly T[]): T {
  return arr[Math.floor(Math.random() * arr.length)];
}

function rand(min: number, max: number): number {
  return Math.random() * (max - min) + min;
}

function generateParticles(len: number) {
  return Array.from({ length: len }, (_, i) => ({
    id: i,
    xDrift: rand(-60, 60),
    yRise: rand(-200, -120),
    duration: rand(0.8, 1.5),
    delay: rand(0, 0.3),
    size: rand(3, 6),
    color: pick(VICTORY_COLORS),
  }));
}

function generateConfetti(len: number) {
  return Array.from({ length: len }, (_, i) => ({
    id: i,
    color: pick(VICTORY_COLORS),
    drift: rand(-40, 40),
    rotation: rand(180, 720),
    delay: 0.8 + rand(0, 0.8),
    duration: rand(2, 3),
    size: rand(4, 7),
    shape: (Math.random() > 0.5 ? "circle" : "square") as "circle" | "square",
  }));
}

function generateSplash(len: number) {
  // Evenly distribute droplets around the full circle
  return Array.from({ length: len }, (_, i) => {
    const angle = (i / len) * Math.PI * 2 + rand(-0.15, 0.15);
    const dist = rand(30, 60);
    return {
      id: i,
      sX: Math.cos(angle) * dist,
      sY: Math.sin(angle) * dist,
      delay: rand(0, 0.2),
      size: rand(2, 5),
      color: pick(SPLASH_COLORS),
    };
  });
}

// ── Component ─────────────────────────────────────────────────────────────────

export default function VictoryGeyser({
  active,
  winnerName,
  position,
}: VictoryGeyserProps) {
  const [phase, setPhase] = useState<"idle" | "geyser" | "confetti" | "done">(
    "idle"
  );

  // Stable random data — regenerated only when `active` changes
  const particles = useMemo(() => (active ? generateParticles(16) : []), [active]);
  const confetti = useMemo(() => (active ? generateConfetti(12) : []), [active]);
  const splash = useMemo(() => (active ? generateSplash(8) : []), [active]);

  // Manage phase transitions
  useEffect(() => {
    if (!active) {
      setPhase("idle");
      return;
    }
    setPhase("geyser");
    const tConfetti = setTimeout(() => setPhase("confetti"), 800);
    const tDone = setTimeout(() => setPhase("done"), 3500);
    return () => {
      clearTimeout(tConfetti);
      clearTimeout(tDone);
    };
  }, [active]);

  if (!active || phase === "idle") return null;

  const showConfetti = phase === "confetti" || phase === "done";

  // ── Render ─────────────────────────────────────────────────────────────────

  return (
    <div
      className="absolute inset-0 pointer-events-none z-50 overflow-hidden"
      aria-hidden="true"
    >
      {/* Centering anchor — follows position if given */}
      <div
        className="absolute"
        style={
          position
            ? { left: position.x, top: position.y }
            : { left: "50%", top: "50%" }
        }
      >
        {/* Winner flash: brief white radial burst */}
        <div
          className="absolute -translate-x-1/2 -translate-y-1/2 w-32 h-32 rounded-full bg-white animate-winner-flash"
          style={{
            left: 0,
            top: 0,
          }}
        />

        {/* Core geyser: 16 particles shooting upward in fountain pattern */}
        {particles.map((p) => (
          <div
            key={p.id}
            className="absolute rounded-full"
            style={{
              left: 0,
              top: 0,
              width: p.size,
              height: p.size,
              backgroundColor: p.color,
              transform: "translate(-50%, -50%)",
              animation: `geyser-erupt ${p.duration}s ease-out ${p.delay}s forwards`,
              "--gx": `${p.xDrift}px`,
              "--gy": `${p.yRise}px`,
            } as React.CSSProperties}
          />
        ))}

        {/* Water splash at base: droplets expanding outward */}
        {splash.map((s) => (
          <div
            key={s.id}
            className="absolute rounded-full"
            style={{
              left: 0,
              top: 0,
              width: s.size,
              height: s.size,
              backgroundColor: s.color,
              transform: "translate(-50%, -50%)",
              animation: `water-splash 0.6s ease-out ${s.delay}s forwards`,
              "--s-x": `${s.sX}px`,
              "--s-y": `${s.sY}px`,
            } as React.CSSProperties}
          />
        ))}
      </div>

      {/* Confetti rain: drifts down from above the whole scene */}
      {showConfetti &&
        confetti.map((c) => (
          <div
            key={c.id}
            className={`absolute ${
              c.shape === "circle" ? "rounded-full" : "rounded-sm"
            }`}
            style={{
              left: `${10 + (c.id * 7) % 80}%`,
              top: "-10px",
              width: c.size,
              height: c.size,
              backgroundColor: c.color,
              animation: `confetti-fall ${c.duration}s ease-in ${c.delay}s forwards`,
              "--c-drift": `${c.drift}px`,
              "--c-rotation": `${c.rotation}deg`,
            } as React.CSSProperties}
          />
        ))}

      {/* Winner floating text — appears after the flash, floats up slowly */}
      <div
        className="absolute left-1/2"
        style={{
          top: "30%",
          animation: "winner-text-float 2.5s ease-out 0.3s forwards",
        }}
      >
        <span className="relative inline-block text-lg font-black text-yellow-300 tracking-wide drop-shadow-[0_0_10px_rgba(251,191,36,0.7)]">
          GANADOR: {winnerName}
        </span>
      </div>
    </div>
  );
}
