"use client";
import { useState, useEffect, useRef } from 'react';
import type { AxoPos } from '@/types/santuario';

/** Static CSS keyframes shared across all NidoScene instances. */
const STATIC_CSS = `
@keyframes cenote-bubble {
  0%   { opacity: 0.35; transform: translateY(0)      scale(1);   }
  60%  { opacity: 0.55; }
  100% { opacity: 0;    transform: translateY(-320px) scale(0.3); }
}
@keyframes ray-flicker {
  0%,100% { opacity: 0.04; }
  50%     { opacity: 0.12; }
}
@keyframes shimmer-heat {
  0%,100% { opacity: 0.04; }
  50%     { opacity: 0.10; }
}
@keyframes golden-float {
  0%   { opacity: 0;   transform: translateY(0);     }
  20%  { opacity: 0.7; }
  100% { opacity: 0;   transform: translateY(-70px); }
}
@keyframes glow-pulse {
  0%,100% { opacity: 0.5; }
  50%     { opacity: 0.8; }
}
@keyframes energy-flow {
  to { stroke-dashoffset: -20; }
}
.energy-line {
  stroke-dasharray: 4 4;
  animation: energy-flow 1.5s linear infinite;
}
`;

export interface SwimBubble {
  left: number;
  delay: number;
  duration: number;
  size: number;
}

/**
 * Generates bubble data and per-axolotito swim positions + CSS keyframes.
 *
 * Extracted from NidoScene to keep rendering logic thin and avoid re-generating
 * @keyframes blocks inline on every render.
 */
export function useSwimAnimation(
  axolotitos: any[],
  isManagement: boolean,
) {
  // ── Bubbles (stable across lifetime) ──
  const [bubbles] = useState<SwimBubble[]>(() => {
    if (typeof window === 'undefined') return [];
    return Array.from({ length: 14 }, () => ({
      left: Math.random() * 94,
      delay: Math.random() * 10,
      duration: 5 + Math.random() * 7,
      size: 2 + Math.random() * 5,
    }));
  });

  // ── Free-range axo positions ──
  const positionsRef = useRef<Record<number, AxoPos>>({});
  const [axoPositions, setAxoPositions] = useState<Record<number, AxoPos>>({});

  useEffect(() => {
    if (isManagement) return;
    let changed = false;
    axolotitos.forEach(axo => {
      if (!positionsRef.current[axo.id]) {
        positionsRef.current[axo.id] = {
          left:     12 + Math.random() * 68,
          bottom:   38 + Math.random() * 28,
          depth:    0.3 + Math.random() * 0.7,
          duration: 8 + Math.random() * 8,
          delay:    Math.random() * 5,
          driftX:   (Math.random() > 0.5 ? 1 : -1) * (18 + Math.random() * 30),
        };
        changed = true;
      }
    });
    if (changed) setAxoPositions({ ...positionsRef.current });
  }, [axolotitos, isManagement]);

  // ── Per-axolotito swim CSS (libre mode) ──
  const swimCss = !isManagement ? axolotitos.map(axo => {
    const p = positionsRef.current[axo.id];
    if (!p) return '';
    const dx = p.driftX;
    return `@keyframes axo-swim-${axo.id} {
      0%   { transform: translateX(0px)          translateY(0px)   scaleX(1);  }
      25%  { transform: translateX(${dx * 0.4}px) translateY(-7px)  scaleX(1);  }
      50%  { transform: translateX(${dx}px)        translateY(-12px) scaleX(${dx > 0 ? 1 : -1}); }
      75%  { transform: translateX(${dx * 0.4}px) translateY(-5px)  scaleX(-1); }
      100% { transform: translateX(0px)          translateY(0px)   scaleX(1);  }
    }`;
  }).join('\n') : '';

  // ── Combined CSS block ──
  const cssBlock = STATIC_CSS + swimCss;

  return { bubbles, axoPositions, positionsRef, cssBlock };
}
