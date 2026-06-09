"use client";

import React, { useCallback, useEffect, useRef, useState } from "react";

// ── Types ─────────────────────────────────────────────────────────────────────

interface CenoteBackgroundProps {
  /** Parallax offset from mouse (set by CenoteRoom) */
  mouseX?: number;
  mouseY?: number;
}

// ── Particle helpers ──────────────────────────────────────────────────────────

interface Particle {
  id: number;
  /** CSS animation duration in seconds */
  dur: number;
  /** Horizontal position % */
  x: number;
  /** Animation delay in seconds */
  delay: number;
  /** Size in px */
  size: number;
  /** Opacity range [min, max] */
  opacityMin: number;
  opacityMax: number;
}

function generateParticles(count: number, seed?: number): Particle[] {
  // Simple seeded pseudo-random (no external lib)
  let s = seed ?? 42;
  const next = () => {
    s = (s * 16807 + 0) % 2147483647;
    return (s - 1) / 2147483646;
  };

  return Array.from({ length: count }, (_, i) => ({
    id: i,
    dur: 3 + next() * 5,         // 3-8s
    x: next() * 100,
    delay: next() * 6,
    size: 2 + next() * 4,        // 2-6px
    opacityMin: 0.1 + next() * 0.2,
    opacityMax: 0.3 + next() * 0.4,
  }));
}

// ── Fish helper ───────────────────────────────────────────────────────────────

interface Fish {
  id: number;
  y: number;           // vertical position %
  dur: number;         // drift duration
  delay: number;       // start delay
  size: number;        // px
}

function generateFish(count: number): Fish[] {
  let s = 99;
  const next = () => {
    s = (s * 16807 + 0) % 2147483647;
    return (s - 1) / 2147483646;
  };
  return Array.from({ length: count }, (_, i) => ({
    id: i,
    y: 30 + next() * 60,
    dur: 8 + next() * 10,
    delay: next() * 12,
    size: 2 + next() * 2,
  }));
}

// ── Component ─────────────────────────────────────────────────────────────────

export default function CenoteBackground({
  mouseX = 0,
  mouseY = 0,
}: CenoteBackgroundProps) {
  // Generate stable particles on mount
  const deepParticles = React.useMemo(() => generateParticles(10, 1), []);
  const midParticles = React.useMemo(() => generateParticles(8, 2), []);
  const fish = React.useMemo(() => generateFish(4), []);

  // Parallax factors
  const deepOffsetX = mouseX * 0.01;
  const deepOffsetY = mouseY * 0.01;
  const midOffsetX = mouseX * 0.03;
  const midOffsetY = mouseY * 0.03;
  const frontOffsetX = mouseX * 0.06;
  const frontOffsetY = mouseY * 0.06;

  return (
    <div
      className="absolute inset-0 overflow-hidden pointer-events-none"
      style={{ zIndex: 0 }}
    >
      {/* ── DEEP LAYER ──────────────────────────────────────────────────── */}
      <div
        className="absolute inset-0 transition-transform duration-300 ease-out"
        style={{
          transform: `translate(${deepOffsetX}px, ${deepOffsetY}px)`,
          background: `
            radial-gradient(ellipse at 50% 30%, rgba(10,40,60,0.6) 0%, rgba(5,15,30,0.9) 50%, rgba(2,6,12,1) 100%),
            radial-gradient(ellipse at 20% 70%, rgba(15,50,70,0.3) 0%, transparent 60%),
            radial-gradient(ellipse at 80% 40%, rgba(8,30,50,0.4) 0%, transparent 50%)
          `,
        }}
      >
        {/* Floating particles */}
        {deepParticles.map((p) => (
          <div
            key={`deep-${p.id}`}
            className="absolute rounded-full animate-particle-float"
            style={{
              left: `${p.x}%`,
              top: `${30 + (p.id * 4) % 50}%`,
              width: p.size,
              height: p.size,
              animationDuration: `${p.dur}s`,
              animationDelay: `${p.delay}s`,
              opacity: p.opacityMin,
              backgroundColor: "rgba(100,180,220,0.5)",
              boxShadow: `0 0 ${p.size * 2}px rgba(100,180,220,${p.opacityMax * 0.3})`,
            }}
          />
        ))}
      </div>

      {/* ── MID LAYER ────────────────────────────────────────────────────── */}
      <div
        className="absolute inset-0 transition-transform duration-300 ease-out"
        style={{
          transform: `translate(${midOffsetX}px, ${midOffsetY}px)`,
        }}
      >
        {/* Stalagmite silhouettes (CSS clip-path) */}
        <div
          className="absolute bottom-0 left-[10%]"
          style={{
            width: "8%",
            height: "35%",
            background: "linear-gradient(to top, rgba(20,40,50,0.7) 0%, rgba(10,25,35,0.3) 100%)",
            clipPath: "polygon(20% 100%, 35% 20%, 40% 0%, 45% 15%, 50% 5%, 55% 20%, 60% 40%, 65% 100%)",
          }}
        />
        <div
          className="absolute bottom-0 right-[15%]"
          style={{
            width: "6%",
            height: "28%",
            background: "linear-gradient(to top, rgba(20,40,50,0.6) 0%, rgba(10,25,35,0.2) 100%)",
            clipPath: "polygon(25% 100%, 30% 30%, 38% 10%, 45% 25%, 50% 8%, 58% 20%, 62% 35%, 70% 100%)",
          }}
        />
        <div
          className="absolute bottom-0 left-[45%]"
          style={{
            width: "5%",
            height: "20%",
            background: "linear-gradient(to top, rgba(15,35,45,0.6) 0%, rgba(8,20,30,0.2) 100%)",
            clipPath: "polygon(30% 100%, 40% 40%, 45% 15%, 50% 35%, 55% 10%, 62% 30%, 68% 100%)",
          }}
        />

        {/* Algae strands */}
        <div
          className="absolute bottom-[20%] left-[25%] animate-algae-sway"
          style={{
            width: "2px",
            height: "60px",
            background: "linear-gradient(to top, rgba(30,120,60,0.5), rgba(20,90,40,0.2))",
            borderRadius: "1px",
            transformOrigin: "bottom center",
            animationDuration: "4s",
          }}
        />
        <div
          className="absolute bottom-[25%] left-[27%] animate-algae-sway"
          style={{
            width: "2px",
            height: "45px",
            background: "linear-gradient(to top, rgba(40,140,70,0.4), rgba(20,100,50,0.15))",
            borderRadius: "1px",
            transformOrigin: "bottom center",
            animationDuration: "5s",
            animationDelay: "0.5s",
          }}
        />
        <div
          className="absolute bottom-[18%] right-[30%] animate-algae-sway"
          style={{
            width: "2px",
            height: "50px",
            background: "linear-gradient(to top, rgba(30,120,60,0.4), rgba(20,90,40,0.15))",
            borderRadius: "1px",
            transformOrigin: "bottom center",
            animationDuration: "4.5s",
            animationDelay: "1s",
          }}
        />

        {/* Mid-layer floating particles */}
        {midParticles.map((p) => (
          <div
            key={`mid-${p.id}`}
            className="absolute rounded-full animate-particle-float"
            style={{
              left: `${p.x}%`,
              top: `${20 + (p.id * 7) % 60}%`,
              width: p.size * 0.7,
              height: p.size * 0.7,
              animationDuration: `${p.dur * 1.2}s`,
              animationDelay: `${p.delay}s`,
              opacity: p.opacityMin * 0.6,
              backgroundColor: "rgba(80,200,150,0.4)",
            }}
          />
        ))}

        {/* Tiny fish that drift horizontally */}
        {fish.map((f) => (
          <div
            key={`fish-${f.id}`}
            className="absolute rounded-full"
            style={{
              top: `${f.y}%`,
              left: "-5%",
              width: f.size,
              height: f.size,
              backgroundColor: "rgba(150,220,200,0.5)",
              animation: `fish-drift ${f.dur}s ease-in-out ${f.delay}s infinite`,
              boxShadow: `0 0 ${f.size * 2}px rgba(150,220,200,0.2)`,
            }}
          />
        ))}
      </div>

      {/* ── FRONT LAYER ──────────────────────────────────────────────────── */}
      <div
        className="absolute inset-0 transition-transform duration-300 ease-out"
        style={{
          transform: `translate(${frontOffsetX}px, ${frontOffsetY}px)`,
        }}
      >
        {/* Rising bubbles (larger, closer) */}
        {[0, 1, 2, 3, 4, 5].map((i) => (
          <div
            key={`bubble-${i}`}
            className="absolute rounded-full animate-bubble-rise-cenote"
            style={{
              left: `${10 + i * 16}%`,
              bottom: "-10px",
              width: `${3 + (i % 3) * 2}px`,
              height: `${3 + (i % 3) * 2}px`,
              animationDuration: `${4 + (i % 3) * 2}s`,
              animationDelay: `${i * 0.8}s`,
              border: "1px solid rgba(150,230,255,0.3)",
              backgroundColor: "rgba(200,240,255,0.08)",
            }}
          />
        ))}

        {/* Sparkle particles */}
        {[0, 1, 2].map((i) => (
          <div
            key={`sparkle-${i}`}
            className="absolute rounded-full animate-particle-float"
            style={{
              left: `${30 + i * 25}%`,
              top: `${40 + i * 15}%`,
              width: 3,
              height: 3,
              animationDuration: `${5 + i}s`,
              animationDelay: `${i * 2}s`,
              backgroundColor: "rgba(255,255,200,0.6)",
              boxShadow: "0 0 6px rgba(255,255,200,0.4)",
            }}
          />
        ))}
      </div>
    </div>
  );
}
