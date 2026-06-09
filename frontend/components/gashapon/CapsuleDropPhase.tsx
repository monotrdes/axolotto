"use client";

import React, { useEffect, useState } from 'react';
import type { Tier } from './tierConfig';
import { TIER_CONFIG } from './tierConfig';
import type { GashaRarity } from './rarityConfig';
import { rarityGlow } from './rarityConfig';

// ── Props ───────────────────────────────────────────────────────────────────────

interface CapsuleDropPhaseProps {
  tier: Tier;
  rarity: GashaRarity;
  onComplete: () => void;
}

// ── Component ───────────────────────────────────────────────────────────────────

export default function CapsuleDropPhase({
  tier,
  rarity,
  onComplete,
}: CapsuleDropPhaseProps) {
  const [stage, setStage] = useState<'drop' | 'vibrate' | 'done'>('drop');
  const cfg = TIER_CONFIG[tier];

  // Phase timing: drop 400ms → vibrate 400ms → done → onComplete
  useEffect(() => {
    const t1 = setTimeout(() => setStage('vibrate'), 400);
    const t2 = setTimeout(() => {
      setStage('done');
      onComplete();
    }, 800);
    return () => { clearTimeout(t1); clearTimeout(t2); };
  }, [onComplete]);

  const glow = rarityGlow(rarity);

  return (
    <div className="relative w-full h-[320px] flex items-center justify-center overflow-hidden">
      <style dangerouslySetInnerHTML={{ __html: `
        @keyframes capsule-drop {
          0%   { transform: translateY(-160px); opacity: 0; }
          20%  { opacity: 1; }
          70%  { transform: translateY(8px); }
          85%  { transform: translateY(-4px); }
          100% { transform: translateY(0); opacity: 1; }
        }
        @keyframes capsule-vibrate {
          0%   { transform: translateX(0); }
          12%  { transform: translateX(-6px) rotate(-2deg); }
          25%  { transform: translateX(5px) rotate(1.5deg); }
          37%  { transform: translateX(-3px) rotate(-1deg); }
          50%  { transform: translateX(4px) rotate(1deg); }
          62%  { transform: translateX(-2px); }
          75%  { transform: translateX(2px); }
          87%  { transform: translateX(-1px); }
          100% { transform: translateX(0); }
        }
        @keyframes capsule-flash {
          0%, 100% { opacity: 0; }
          30%  { opacity: 0.5; }
          60%  { opacity: 0.1; }
          85%  { opacity: 0.7; }
        }
        .capsule-drop-anim  { animation: capsule-drop 0.4s ease-out both; }
        .capsule-vibe-anim  { animation: capsule-vibrate 0.4s ease-in-out both; }
        .capsule-flash-anim { animation: capsule-flash 0.8s ease-out both; }
      `}} />

      {/* Floor shadow */}
      <div
        className="absolute bottom-16 left-1/2 -translate-x-1/2 w-20 h-4 rounded-full blur-md transition-opacity duration-300"
        style={{
          background: glow,
          opacity: stage === 'drop' ? 0 : 0.5,
        }}
      />

      {/* Capsule */}
      <div
        className={`relative w-20 h-28 ${stage === 'drop' ? 'capsule-drop-anim' : 'capsule-vibe-anim'}`}
        style={{ willChange: 'transform' }}
      >
        {/* Top hemisphere */}
        <div
          className="absolute top-0 left-0 right-0 h-14 rounded-t-full border-2 border-b-0"
          style={{
            background: `linear-gradient(180deg, ${cfg.glow}, rgba(5,2,15,0.9))`,
            borderColor: cfg.border,
            boxShadow: `inset 0 4px 10px rgba(255,255,255,0.1), 0 0 14px ${glow}`,
          }}
        />
        {/* Rim */}
        <div
          className="absolute top-[52px] left-0 right-0 h-2 z-10 rounded-full"
          style={{
            background: `linear-gradient(180deg, ${cfg.color}, ${cfg.glow})`,
            boxShadow: `0 0 6px ${cfg.color}`,
          }}
        />
        {/* Bottom hemisphere */}
        <div
          className="absolute bottom-0 left-0 right-0 h-14 rounded-b-full border-2 border-t-0"
          style={{
            background: `linear-gradient(0deg, ${cfg.glow}, rgba(5,2,15,0.9))`,
            borderColor: cfg.border,
            boxShadow: `inset 0 -4px 10px rgba(0,0,0,0.4), 0 0 14px ${glow}`,
          }}
        />

        {/* Internal mystery light */}
        <div
          className="capsule-flash-anim absolute inset-2 rounded-full"
          style={{
            background: `radial-gradient(circle, ${glow}, transparent 70%)`,
          }}
        />
      </div>

      {/* Label */}
      <p
        className="absolute bottom-10 text-[10px] font-black uppercase tracking-widest text-slate-500 transition-opacity duration-300"
        style={{ opacity: stage !== 'drop' ? 1 : 0 }}
      >
        {stage === 'vibrate' ? '¡Abriendo…!' : ''}
      </p>
    </div>
  );
}
