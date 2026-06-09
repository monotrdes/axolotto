"use client";

import React, { useEffect } from 'react';
import type { GashaRarity } from './rarityConfig';
import { rarityGlow } from './rarityConfig';
import Particles from './Particles';

// ── Props ───────────────────────────────────────────────────────────────────────

interface CapsuleOpenPhaseProps {
  rarity: GashaRarity;
  onComplete: () => void;
}

// ── Component ───────────────────────────────────────────────────────────────────

export default function CapsuleOpenPhase({
  rarity,
  onComplete,
}: CapsuleOpenPhaseProps) {
  // Auto-complete after 600ms
  useEffect(() => {
    const t = setTimeout(onComplete, 600);
    return () => clearTimeout(t);
  }, [onComplete]);

  const glow = rarityGlow(rarity);

  return (
    <div className="relative w-full h-[320px] flex items-center justify-center overflow-hidden">
      <style dangerouslySetInnerHTML={{ __html: `
        @keyframes half-rise {
          0%   { transform: translateY(0) rotate(0deg); opacity: 1; }
          100% { transform: translateY(-90px) rotate(-12deg); opacity: 0; }
        }
        @keyframes half-fall {
          0%   { transform: translateY(0) rotate(0deg); opacity: 1; }
          100% { transform: translateY(90px) rotate(12deg); opacity: 0; }
        }
        @keyframes ring-expand {
          0%   { transform: scale(0.3); opacity: 1; border-width: 8px; }
          100% { transform: scale(4); opacity: 0; border-width: 1px; }
        }
        @keyframes open-flash {
          0%   { opacity: 0; }
          15%  { opacity: 0.6; }
          100% { opacity: 0; }
        }
        .half-rise-anim  { animation: half-rise 0.5s ease-in forwards; }
        .half-fall-anim  { animation: half-fall 0.5s ease-in forwards; }
        .ring-expand-anim { animation: ring-expand 0.6s ease-out forwards; }
        .open-flash-anim  { animation: open-flash 0.5s ease-out forwards; }
      `}} />

      {/* Particles burst */}
      <Particles rarity={rarity} count={20} burst durationMs={1200} />

      {/* White flash overlay */}
      <div className="open-flash-anim absolute inset-0 bg-white pointer-events-none" />

      {/* Expanding ring */}
      <div
        className="ring-expand-anim absolute rounded-full pointer-events-none"
        style={{
          width: '100px', height: '100px',
          border: `8px solid ${glow}`,
        }}
      />

      {/* Top half — rises */}
      <div
        className="half-rise-anim absolute w-20 h-14 rounded-t-full border-2 border-b-0"
        style={{
          top: 'calc(50% - 56px)',
          left: '50%',
          marginLeft: '-40px',
          background: `linear-gradient(180deg, ${glow}, rgba(5,2,15,0.9))`,
          borderColor: glow,
          boxShadow: `0 0 16px ${glow}`,
        }}
      />

      {/* Bottom half — falls */}
      <div
        className="half-fall-anim absolute w-20 h-14 rounded-b-full border-2 border-t-0"
        style={{
          top: 'calc(50% + 4px)',
          left: '50%',
          marginLeft: '-40px',
          background: `linear-gradient(0deg, ${glow}, rgba(5,2,15,0.9))`,
          borderColor: glow,
          boxShadow: `0 0 16px ${glow}`,
        }}
      />
    </div>
  );
}
