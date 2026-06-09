"use client";

import React from 'react';
import type { GashaRarity } from './rarityConfig';

// ── Props ───────────────────────────────────────────────────────────────────────

interface ParticlesProps {
  rarity: GashaRarity;
  count?: number;         // default 18
  burst?: boolean;        // true = burst outward from center, false = slow rain
  durationMs?: number;    // CSS animation duration (ms)
}

// ── Rarity particle shapes ──────────────────────────────────────────────────────

interface ParticleShape {
  /** Emoji or CSS shape character */
  symbol: string;
  /** CSS class suffix for the animation keyframe */
  animClass: string;
  /** Size range [min, max] in px */
  sizeRange: [number, number];
  /** Color palette (hex or hsl) */
  colors: string[];
}

const SHAPES: Record<GashaRarity, ParticleShape> = {
  common: {
    symbol: '●',
    animClass: 'p-common',
    sizeRange: [6, 14],
    colors: ['#2DD4BF', '#14B8A6', '#5EEAD4', '#99F6E4', '#0D9488'],
  },
  rare: {
    symbol: '◆',
    animClass: 'p-rare',
    sizeRange: [8, 16],
    colors: ['#22D3EE', '#06B6D4', '#67E8F9', '#38BDF8', '#0EA5E9'],
  },
  epic: {
    symbol: '★',
    animClass: 'p-epic',
    sizeRange: [10, 18],
    colors: ['#A855F7', '#C084FC', '#8B5CF6', '#D8B4FE', '#7C3AED'],
  },
  legendary: {
    symbol: '✦',
    animClass: 'p-legendary',
    sizeRange: [8, 20],
    colors: ['#FBBF24', '#F59E0B', '#FCD34D', '#FDE68A', '#EAB308'],
  },
  astral: {
    symbol: '●',
    animClass: 'p-astral',
    sizeRange: [6, 16],
    colors: ['#C084FC', '#A78BFA', '#E879F9', '#818CF8', '#F0ABFC'],
  },
};

// ── Generate particle configs (deterministic from seed to avoid React key warnings) ──

function generateParticles(
  count: number,
  shape: ParticleShape,
  burst: boolean,
): Array<{
  id: number;
  sym: string;
  color: string;
  size: number;
  leftPct: number;
  delayS: number;
  driftX: number;
  driftY: number;
  rotDeg: number;
}> {
  // Pseudo-random seeded by count + burst to keep render stable
  let seed = count * 7 + (burst ? 31 : 17);
  const prng = () => {
    seed = (seed * 16807) % 2147483647;
    return (seed - 1) / 2147483646;
  };

  return Array.from({ length: count }, (_, i) => ({
    id: i,
    sym: shape.symbol,
    color: shape.colors[i % shape.colors.length],
    size: Math.floor(shape.sizeRange[0] + prng() * (shape.sizeRange[1] - shape.sizeRange[0])),
    leftPct: burst ? 50 : prng() * 100,
    delayS: +(prng() * 2.5).toFixed(2),
    driftX: burst ? (prng() - 0.5) * 280 : (prng() - 0.5) * 120,
    driftY: burst ? -(prng() * 400 + 100) : -(prng() * 300 + 80),
    rotDeg: prng() * 720 - 360,
  }));
}

// ── Component ───────────────────────────────────────────────────────────────────

export default function Particles({
  rarity,
  count = 18,
  burst = true,
  durationMs = 1800,
}: ParticlesProps) {
  const shape = SHAPES[rarity];
  const particles = React.useMemo(
    () => generateParticles(count, shape, burst),
    [count, shape, burst],
  );

  const animName = burst ? `${shape.animClass}-burst` : `${shape.animClass}-rain`;

  return (
    <div className="absolute inset-0 pointer-events-none overflow-hidden" aria-hidden>
      <style dangerouslySetInnerHTML={{ __html: `
        @keyframes ${animName} {
          0%   { transform: translate(0, 0) rotate(0deg); opacity: 0; }
          5%   { opacity: 1; }
          60%  { opacity: 0.9; }
          95%  { opacity: 0.1; }
          100% { transform: translate(var(--p-drift-x), var(--p-drift-y)) rotate(var(--p-rot)); opacity: 0; }
        }
        .p-item {
          will-change: transform, opacity;
          animation: ${animName} ${durationMs}ms var(--p-delay) ease-out both;
          position: absolute;
          left: var(--p-left);
          top: ${burst ? '50%' : '90%'};
        }
      `}} />

      {particles.map(p => (
        <span
          key={p.id}
          className="p-item select-none leading-none"
          style={{
            '--p-left': `${p.leftPct}%`,
            '--p-drift-x': `${p.driftX}px`,
            '--p-drift-y': `${p.driftY}px`,
            '--p-rot': `${p.rotDeg}deg`,
            '--p-delay': `${p.delayS}s`,
            fontSize: `${p.size}px`,
            color: p.color,
            marginLeft: burst ? `-${p.size / 2}px` : undefined,
            marginTop: burst ? `-${p.size / 2}px` : undefined,
          } as React.CSSProperties}
        >
          {p.sym}
        </span>
      ))}
    </div>
  );
}
